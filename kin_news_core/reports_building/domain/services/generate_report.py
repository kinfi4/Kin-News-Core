import logging
from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
from typing import Type

from kin_news_core.telegram import IDataGetterProxy
from kin_news_core.messaging import AbstractEventProducer
from kin_news_core.reports_building.infrastructure.services import ModelTypesService
from kin_news_core.reports_building.domain.entities import (
    GenerateReportEntity,
    WordCloudReport,
    StatisticalReport,
    GenerationTemplateWrapper,
    VisualizationTemplate, ModelEntity,
)
from kin_news_core.reports_building.events import (
    ReportProcessingStarted,
    WordCloudReportProcessingFinished,
    StatisticalReportProcessingFinished,
)
from kin_news_core.reports_building.domain.services.predicting.predictor import IPredictorFactory, IPredictor
from kin_news_core.reports_building.domain.services.statistical_report.reports_builder import ReportsBuilder
from kin_news_core.reports_building.domain.services.word_cloud.reports_builder import WordCloudReportBuilder
from kin_reports_generation.constants import ReportProcessingResult, REPORTS_STORING_EXCHANGE


class IGeneratingReportsService(ABC):
    _REPORT_TYPE_TO_EVENT_MAPPING = {
        WordCloudReport: WordCloudReportProcessingFinished,
        StatisticalReport: StatisticalReportProcessingFinished,
    }

    reports_builder: WordCloudReportBuilder | ReportsBuilder

    def __init__(
        self,
        telegram_client: IDataGetterProxy,
        events_producer: AbstractEventProducer,
        model_types_service: ModelTypesService,
        predictor_factory_class: Type[IPredictorFactory],
    ) -> None:
        self._logger = logging.getLogger(self.__class__.__name__)

        self._telegram = telegram_client
        self._events_producer = events_producer
        self._model_types_service = model_types_service
        self._predictor_factory_class = predictor_factory_class

    def generate_report(self, generate_report_entity: GenerateReportEntity) -> None:
        username = generate_report_entity.username

        self._logger.info(f'[{self.__class__.__name__}] Starting generating report for user: {username}')

        try:
            self._publish_report_processing_started(generate_report_entity.report_id)

            model_meta_dict = self._model_types_service.get_model_metadata(username, generate_report_entity.model_code)
            model_meta = ModelEntity(**model_meta_dict)

            predictor = self._initialize_predictor(model_meta)

            generate_report_wrapper = GenerationTemplateWrapper(
                predictor=predictor,
                generate_report_metadata=generate_report_entity,
                model_metadata=model_meta,
                visualization_template=self._load_visualization_template(generate_report_entity),
            )

            report_entity = self._build_report_entity(generate_report_wrapper)
            self._publish_finished_report(username, report_entity)
        except Exception as error:
            self._logger.error(
                f'[{self.__class__.__name__}]'
                f' {error.__class__.__name__} occurred during processing report for user: {username} with message: {str(error)}',
                exc_info=True,
            )

            error.with_traceback(error.__traceback__)

            postponed_report = self._build_postponed_report(generate_report_entity.report_id, generate_report_entity.name, error)
            self._publish_finished_report(username, postponed_report)

    @abstractmethod
    def _build_report_entity(self, generate_report_wrapper: GenerationTemplateWrapper) -> StatisticalReport | WordCloudReport:
        pass

    def _load_visualization_template(self, gen_request: GenerateReportEntity) -> VisualizationTemplate | None:
        if not gen_request.template_id:
            return None

        return VisualizationTemplate(
            **self._model_types_service.get_visualization_templates(
                gen_request.username,
                gen_request.template_id,
            )
        )

    @classmethod
    def _build_postponed_report(cls, report_id: int, report_name: str, error: Exception) -> StatisticalReport | WordCloudReport:
        return (
            cls.reports_builder.from_report_id(report_id)
            .set_report_name(report_name)
            .set_status(ReportProcessingResult.POSTPONED)
            .set_failed_reason(str(error))
            .build()
        )

    def _datetime_from_date(self, dt: date, end_of_day: bool = False) -> datetime:
        return datetime(year=dt.year, month=dt.month, day=dt.day) + timedelta(days=int(end_of_day))

    def _initialize_predictor(self, model_entity: ModelEntity) -> IPredictor:
        predictor_factory = self._predictor_factory_class(model_entity)
        return predictor_factory.create_predictor()

    def _publish_report_processing_started(self, report_id: int) -> None:
        event = ReportProcessingStarted(report_id=report_id)

        self._events_producer.publish(
            REPORTS_STORING_EXCHANGE,
            [event],
        )

    def _publish_finished_report(self, username: str, report: WordCloudReport | StatisticalReport) -> None:
        event_type = self._REPORT_TYPE_TO_EVENT_MAPPING[type(report)]
        event = event_type(**report.dict(), username=username)

        self._events_producer.publish(
            REPORTS_STORING_EXCHANGE,
            [event],
        )
