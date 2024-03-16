import logging
from typing import Any
from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta

from kin_txt_core.datasources.common.entities import ClassificationEntity, DatasourceLink
from kin_txt_core.exceptions import InvalidChannelURLError
from kin_txt_core.messaging import AbstractEventProducer
from kin_txt_core.reports_building.domain.services.datasources.interface import IDataSourceFactory
from kin_txt_core.reports_building.infrastructure.services import ModelTypesService
from kin_txt_core.reports_building.domain.entities import (
    GenerateReportEntity,
    WordCloudReport,
    StatisticalReport,
    VisualizationTemplate, ModelEntity,
)
from kin_txt_core.reports_building.domain.entities.generation_template_wrapper import GenerationTemplateWrapper
from kin_txt_core.reports_building.events import (
    ReportProcessingStarted,
    WordCloudReportProcessingFinished,
    StatisticalReportProcessingFinished,
)
from kin_txt_core.reports_building.domain.services.predicting.predictor import IPredictorFactory, IPredictor
from kin_txt_core.reports_building.domain.services.statistical_report.reports_builder import StatisticalReportsBuilder
from kin_txt_core.reports_building.domain.services.word_cloud.reports_builder import WordCloudReportsBuilder
from kin_txt_core.reports_building.constants import ReportProcessingResult, REPORTS_STORING_EXCHANGE


class IGeneratingReportsService(ABC):
    _REPORT_TYPE_TO_EVENT_MAPPING = {
        WordCloudReport: WordCloudReportProcessingFinished,
        StatisticalReport: StatisticalReportProcessingFinished,
    }

    reports_builder: WordCloudReportsBuilder | StatisticalReportsBuilder

    def __init__(
        self,
        events_producer: AbstractEventProducer,
        model_types_service: ModelTypesService,
        predictor_factory: IPredictorFactory,
        datasource_factory: IDataSourceFactory,
    ) -> None:
        self._logger = logging.getLogger(self.__class__.__name__)

        self._events_producer = events_producer
        self._model_types_service = model_types_service
        self._predictor_factory = predictor_factory
        self._datasource_factory = datasource_factory

        self._report_generation_warnings = []

    def generate_report(self, generate_report_entity: GenerateReportEntity) -> None:
        username = generate_report_entity.username

        self._logger.info(f'[{self.__class__.__name__}] Starting generating report for user: {username}')

        try:
            self._publish_report_processing_started(generate_report_entity.report_id)

            model_meta_dict = self._model_types_service.get_model_metadata(username, generate_report_entity.model_code)
            model_meta = ModelEntity(**model_meta_dict)

            predictor = self._initialize_predictor(model_meta, generate_report_entity)

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

    def _build_report_entity(self, generate_report_wrapper: GenerationTemplateWrapper) -> StatisticalReport | WordCloudReport:
        posts: list[ClassificationEntity] = self._gather_report_data(generate_report_wrapper)

        handled_data = self.handle_posts(posts, generate_report_wrapper)

        return self.build_report(handled_data, generate_report_wrapper)

    def _gather_report_data(self, generate_report_wrapper: GenerationTemplateWrapper) -> list[ClassificationEntity]:
        total_posts: list[ClassificationEntity] = []

        datasource = self._datasource_factory.get_data_source(
            generate_report_wrapper.generate_report_metadata.datasource_type
        )
        generate_report_meta = generate_report_wrapper.generate_report_metadata

        for source_name in generate_report_meta.channel_list:
            try:
                source_posts = datasource.fetch_data(
                    source=DatasourceLink(
                        source_link=source_name,
                        offset_date=self._datetime_from_date(generate_report_meta.end_date, end_of_day=True),
                        earliest_date=self._datetime_from_date(generate_report_meta.start_date),
                        skip_messages_without_text=True,
                    ),
                )

                total_posts.extend(source_posts)  # Append all posts from the source to the total list
            except InvalidChannelURLError:
                self._logger.warning(f"[WordCloudStrategy] Invalid channel URL: {source_name}")
                self._report_generation_warnings.append(self.get_not_existing_source_channel_warning(source_name))
                continue

            if not source_posts:
                self._logger.warning(f"[WordCloudStrategy] No messages from {source_name}")
                self._report_generation_warnings.append(self.get_not_existing_source_channel_warning(source_name))
                continue

            self._logger.info(f"[WordCloudStrategy] Gathered {len(source_posts)} messages from {source_name}")

        return total_posts

    @abstractmethod
    def handle_posts(self, posts: list[ClassificationEntity], generate_report_wrapper: GenerationTemplateWrapper) -> dict[str, Any]:
        pass

    @abstractmethod
    def build_report(
        self,
        handled_data: dict[str, Any],
        generate_report_wrapper: GenerationTemplateWrapper,
    ) -> StatisticalReport | WordCloudReport:
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

    def _initialize_predictor(self, model_entity: ModelEntity, generate_entity: GenerateReportEntity) -> IPredictor:
        return self._predictor_factory.create_predictor(model_entity, generate_entity)

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

    def get_not_existing_source_channel_warning(self, source_channel_name: str) -> str:
        return f"Source channel `{source_channel_name}` does not exist."

    def get_empty_source_channel_warning(self, source_channel_name: str) -> str:
        return f"Source channel `{source_channel_name}` is empty."
