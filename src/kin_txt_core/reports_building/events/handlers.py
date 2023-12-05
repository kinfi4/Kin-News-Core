from dependency_injector.wiring import inject, Provide

from kin_txt_core.reports_building.domain.entities import ModelEntity
from kin_txt_core.reports_building.domain.services import GenerateRequestHandlerService
from kin_txt_core.reports_building.domain.services.validation import ModelValidationService
from kin_txt_core.reports_building.events import GenerateReportRequestOccurred, ModelValidationRequestOccurred
from kin_txt_core.reports_building.containers import Container

__all__ = ["on_report_processing_request", "on_model_validation_request"]


@inject
def on_report_processing_request(
    event: GenerateReportRequestOccurred,
    generate_request_handler_service: GenerateRequestHandlerService = Provide[Container.domain_services.generate_request_handler_service],
) -> None:
    generate_request_handler_service.handle_request(event)


@inject
def on_model_validation_request(
    event: ModelValidationRequestOccurred,
    model_validation_service: ModelValidationService = Provide[Container.domain_services.model_validation_service],
) -> None:
    model_validation_service.validate_model(ModelEntity(**event.dict()))
