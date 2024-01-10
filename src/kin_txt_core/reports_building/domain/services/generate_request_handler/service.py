import logging
from typing import cast, Callable

from celery import Task

from kin_txt_core.constants import DEFAULT_DATE_FORMAT
from kin_txt_core.reports_building.constants import ReportTypes, ModelTypes
from kin_txt_core.reports_building.domain.services.predicting import IPredictorFactory
from kin_txt_core.reports_building.events import GenerateReportRequestOccurred
from kin_txt_core.reports_building.infrastructure.services import ModelTypesService


class GenerateRequestHandlerService:
    def __init__(
        self,
        predictor_factory: IPredictorFactory,
        model_types_service: ModelTypesService,
    ) -> None:
        self._predictor_factory = predictor_factory
        self._model_types_service = model_types_service

        self._logger = logging.getLogger(self.__class__.__name__)

    def handle_request(self, event: GenerateReportRequestOccurred) -> None:
        if not self._predictor_factory.is_handling(event.model_type, event.model_code):
            self._logger.info(f"[GenerateRequestHandlerService] Current service is not handling model {event.model_code}")
            return

        target_task = cast(Task, self._get_celery_task_from_event(event))
        target_task.delay(
            start_date=event.start_date.strftime(DEFAULT_DATE_FORMAT),
            end_date=event.end_date.strftime(DEFAULT_DATE_FORMAT),
            channel_list=event.channel_list,
            username=event.username,
            report_id=event.report_id,
            model_code=event.model_code,
            template_id=event.template_id,
            name=event.name,
            datasource_type=event.datasource_type,
            model_type=event.model_type,
        )

    def _get_celery_task_from_event(self, event: GenerateReportRequestOccurred) -> Callable[..., None]:
        from kin_txt_core.reports_building.tasks import generate_word_cloud_task, generate_statistical_report_task

        if event.report_type == ReportTypes.WORD_CLOUD:
            return generate_word_cloud_task

        if event.report_type == ReportTypes.STATISTICAL:
            return generate_statistical_report_task

        raise RuntimeError('Unknown report type provided!')
