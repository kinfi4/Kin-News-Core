import logging
from typing import cast, Callable

from kin_txt_core.reports_building.constants import ReportTypes
from kin_txt_core.reports_building.domain.entities import GenerateReportEntity
from kin_txt_core.reports_building.domain.services.generate_report import IGeneratingReportsService
from kin_txt_core.reports_building.domain.services.predicting import IPredictorFactory
from kin_txt_core.reports_building.events import GenerateReportRequestOccurred
from kin_txt_core.reports_building.infrastructure.services import ModelTypesService


class GenerateRequestHandlerService:
    def __init__(
        self,
        predictor_factory: IPredictorFactory,
        model_types_service: ModelTypesService,
        generating_reports_service: IGeneratingReportsService,
        generating_word_cloud_service: IGeneratingReportsService,
    ) -> None:
        self._predictor_factory = predictor_factory
        self._model_types_service = model_types_service

        self._generating_reports_service = generating_reports_service
        self._generating_word_cloud_service = generating_word_cloud_service

        self._logger = logging.getLogger(self.__class__.__name__)

    def handle_request(self, event: GenerateReportRequestOccurred) -> None:
        if not self._predictor_factory.is_handling(event.model_type, event.model_code):
            self._logger.info(f"[GenerateRequestHandlerService] Current service is not handling model {event.model_code}")
            return

        target_task = self._get_celery_task_from_event(event)
        target_task(event)

    def _get_celery_task_from_event(self, event: GenerateReportRequestOccurred) -> Callable[..., None]:
        if event.report_type == ReportTypes.WORD_CLOUD:
            return self.generate_word_cloud_task

        if event.report_type == ReportTypes.STATISTICAL:
            return self.generate_statistical_report_task

        raise RuntimeError('Unknown report type provided!')

    def generate_statistical_report_task(self, generation_request: GenerateReportEntity) -> None:
        self._logger.info("Instantiating generate report entity and running the processing...")

        self._generating_reports_service.generate_report(cast(GenerateReportEntity, generation_request))

    def generate_word_cloud_task(self, generation_request: GenerateReportEntity) -> None:
        self._logger.info("Instantiating generate report entity and running the processing...")

        self._generating_word_cloud_service.generate_report(cast(GenerateReportEntity, generation_request))
