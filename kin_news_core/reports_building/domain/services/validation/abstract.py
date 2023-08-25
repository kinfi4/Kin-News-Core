import os
import logging
from abc import ABC, abstractmethod

from kin_news_core.reports_building.domain.entities import ModelEntity
from kin_news_core.messaging import AbstractEventProducer
from kin_news_core.reports_building.constants import MODEL_TYPES_EXCHANGE, ModelTypes
from kin_news_core.reports_building.events import ModelValidationStarted, ModelValidationFinished
from kin_news_core.reports_building.types import ValidationResult
from kin_news_core.reports_building.infrastructure.services import ModelTypesService


class ModelValidationService(ABC):
    def __init__(
        self,
        events_producer: AbstractEventProducer,
        model_type_service: ModelTypesService,
        model_storage_path: str,
    ) -> None:
        self._events_producer = events_producer
        self._model_type_service = model_type_service
        self._model_storage_path = model_storage_path

        self._logger = logging.getLogger(self.__class__.__name__)

    def validate_model(self, model: ModelEntity) -> None:
        self._events_producer.publish(
            MODEL_TYPES_EXCHANGE,
            [ModelValidationStarted(code=model.code, username=model.owner_username)]
        )

        try:
            self.__preload_model_binaries(model)
            validation_status, error_message = self._validate_model(model)
        except Exception as error:
            self._logger.error(f"[ModelService] Model validation failed: {error}")
            validation_status, error_message = False, str(error)

        self._events_producer.publish(
            MODEL_TYPES_EXCHANGE,
            [
                ModelValidationFinished(
                    code=model.code,
                    username=model.owner_username,
                    status=validation_status,
                    error_message=error_message,
                )
            ]
        )

    @abstractmethod
    def _validate_model(self, model_entity: ModelEntity) -> ValidationResult:
        pass

    def __preload_model_binaries(self, model: ModelEntity) -> None:
        self._logger.info(f"[ModelService] Preloading model binaries for {model.code}")

        model_data = self._model_type_service.get_model_binaries(model.owner_username, model.code)
        tokenizer_data = self._model_type_service.get_tokenizer_binaries(model.owner_username, model.code)

        user_model_storage_path = model.get_model_directory_path(self._model_storage_path)
        if not os.path.exists(user_model_storage_path):
            os.makedirs(user_model_storage_path)

        model_path = model.get_model_binaries_path(self._model_storage_path)
        with open(model_path, "wb") as model_file:
            model_file.write(model_data.read())

        tokenizer_path = model.get_tokenizer_binaries_path(self._model_storage_path)
        with open(tokenizer_path, "wb") as tokenizer_file:
            tokenizer_file.write(tokenizer_data.read())
