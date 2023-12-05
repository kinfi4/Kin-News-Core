import logging

from kin_news_core.exceptions import ServiceProxyError, ServiceProxyDuplicateError
from kin_news_core.reports_building.constants import GENERIC_MODEL_TYPE
from kin_news_core.reports_building.domain.services.predicting import IPredictorFactory
from kin_news_core.reports_building.infrastructure.services import ModelTypesService

__all__ = ["ModelTypeRegistrationService"]


class ModelTypeRegistrationService:
    def __init__(
        self,
        predictor_factory: IPredictorFactory,
        model_types_service: ModelTypesService,
    ) -> None:
        self._predictor_factory = predictor_factory
        self._model_types_service = model_types_service

        self._logger = logging.getLogger(self.__class__.__name__)

    def register_model_type(self) -> None:
        if self._predictor_factory.model_type == GENERIC_MODEL_TYPE:
            self._logger.info(f"[ModelTypeService] Generic model type {self._predictor_factory.model_type} does not require registration")
            return

        try:
            self._model_types_service.register_model_type(self._predictor_factory.model_type)
        except ServiceProxyDuplicateError:
            self._logger.info(f"[ModelTypeService] Model type {self._predictor_factory.model_type.code} already registered")
            return
        except ServiceProxyError as error:
            self._logger.error(f"[ModelTypeService] Service error occurred during model type registration: {error}")
            raise
        except Exception as error:
            self._logger.error(f"[ModelTypeService] Failed to register model type: {error}")
            raise

        self._logger.info(f"[ModelTypeService] Model type {self._predictor_factory.model_type.code} registered successfully")
