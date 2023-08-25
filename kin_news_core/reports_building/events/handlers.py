from typing import Callable, cast

from celery import Task
from dependency_injector.wiring import inject, Provide

from kin_news_core.constants import DEFAULT_DATE_FORMAT
from kin_news_core.reports_building.constants import ReportTypes, ModelTypes
from kin_news_core.reports_building.domain.entities import ModelEntity
from kin_news_core.reports_building.domain.services.validation import ModelValidationService
from kin_news_core.reports_building.events import GenerateReportRequestOccurred, ModelValidationRequestOccurred
from kin_news_core.reports_building.tasks import generate_word_cloud_task, generate_statistical_report_task
from kin_news_core.reports_building.containers import Container


def on_report_processing_request(
    event: GenerateReportRequestOccurred,
) -> None:
    target_task = cast(Task, _get_celery_task_from_event(event))
    target_task.delay(
        start_date=event.start_date.strftime(DEFAULT_DATE_FORMAT),
        end_date=event.end_date.strftime(DEFAULT_DATE_FORMAT),
        channel_list=event.channel_list,
        username=event.username,
        report_id=event.report_id,
        model_id=event.model_code,
        template_id=event.template_id,
        report_name=event.name,
    )


@inject
def on_model_validation_request(
    event: ModelValidationRequestOccurred,
    model_validation_service: ModelValidationService = Provide[Container.domain_services.model_validation_service],
) -> None:
    if event.model_type == ModelTypes.CUSTOM:
        return  # nothing to validate for custom models

    model_validation_service.validate_model(ModelEntity(**event.dict()))


def _get_celery_task_from_event(
    event: GenerateReportRequestOccurred
) -> Callable[..., None]:
    if event.report_type == ReportTypes.WORD_CLOUD:
        return generate_word_cloud_task

    if event.report_type == ReportTypes.STATISTICAL:
        return generate_statistical_report_task

    raise RuntimeError('Unknown report type provided!')
