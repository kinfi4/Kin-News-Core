import logging

from celery import Celery
from dependency_injector.wiring import Provide, inject

from kin_txt_core.reports_building.constants import ModelStatuses
from kin_txt_core.reports_building.settings import CelerySettings
from kin_txt_core.reports_building.types import CategoryMapping
from kin_txt_core.reports_building.domain.services.validation import ModelValidationService
from kin_txt_core.reports_building.domain.entities import GenerateReportEntity, ModelEntity
from kin_txt_core.reports_building.domain.services.generate_report import IGeneratingReportsService
from kin_txt_core.reports_building.containers import Container

_logger = logging.getLogger(__name__)


celery_app = Celery("kin_reports_generation")
celery_app.config_from_object(CelerySettings())


@celery_app.task
@inject
def generate_statistical_report_task(
    generating_reports_service: IGeneratingReportsService = Provide[Container.domain_services.generate_statistics_report_service],
    **kwargs,
) -> None:
    _logger.info("Instantiating generate report entity and running the processing...")

    generate_report_entity = GenerateReportEntity(**kwargs)
    generating_reports_service.generate_report(generate_report_entity)


@celery_app.task
@inject
def generate_word_cloud_task(
    generating_word_cloud_service: IGeneratingReportsService = Provide[Container.domain_services.generate_word_cloud_report_service],
    **kwargs,
) -> None:
    _logger.info("Instantiating generate report entity and running the processing...")

    generate_report_entity = GenerateReportEntity(**kwargs)
    generating_word_cloud_service.generate_report(generate_report_entity)


@celery_app.task
@inject
def validate_model(
    model_dict_data: dict[str, str | ModelStatuses | CategoryMapping],
    model_service: ModelValidationService = Provide[Container.domain_services.model_validation_service],
) -> None:
    model = ModelEntity.parse_obj(model_dict_data)
    
    _logger.info(f"[CELERY] Initiate model validation {model.code} for user {model.owner_username}...")

    model_service.validate_model(model)
