import logging

from kin_news_core.reports_building.domain.entities import ModelEntity
from kin_news_core.messaging import AbstractEventProducer
from kin_news_core.reports_building.constants import MODEL_TYPES_EXCHANGE
from kin_news_core.reports_building.domain.services.validation.factory_interface import BaseValidatorFactory
from kin_news_core.reports_building.events import ModelValidationStarted, ModelValidationFinished
from kin_news_core.reports_building.types import ValidationResult

__all__ = ["ModelValidationService"]


class ModelValidationService:
    def __init__(
        self,
        events_producer: AbstractEventProducer,
        validador_factory: BaseValidatorFactory,
    ) -> None:
        self._events_producer = events_producer
        self._validador_factory = validador_factory

        self._logger = logging.getLogger(self.__class__.__name__)

    def validate_model(self, model: ModelEntity) -> None:
        self._events_producer.publish(
            MODEL_TYPES_EXCHANGE,
            [ModelValidationStarted(code=model.code, username=model.owner_username)]
        )

        try:
            validation_status, error_message = self._validate_model(model)
        except Exception as error:
            self._logger.error(f"[ModelService] Model validation failed: {error}")
            validation_status, error_message = False, str(error)

        self._publish_model_validation_finished(model, validation_status, error_message)

    def _validate_model(self, model_entity: ModelEntity) -> ValidationResult:
        validator = self._validador_factory.create_validator(model_entity)

        return validator.validate_model(model_entity)

    def _publish_model_validation_finished(self, model: ModelEntity, status: bool, message: str | None) -> None:
        self._events_producer.publish(
            MODEL_TYPES_EXCHANGE,
            [
                ModelValidationFinished(
                    code=model.code,
                    username=model.owner_username,
                    status=status,
                    error_message=message,
                )
            ]
        )
