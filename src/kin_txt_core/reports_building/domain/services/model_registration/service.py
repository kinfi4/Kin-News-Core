import logging

from kin_txt_core.exceptions import ServiceProxyError, ServiceProxyDuplicateError
from kin_txt_core.reports_building.domain.services.predicting import IPredictorFactory
from kin_txt_core.reports_building.infrastructure.services import ModelTypesService

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
        if self._predictor_factory.model_types == "GenericModel":
            self._logger.info(
                f"[ModelTypeService] "
                f"Generic model type {self._predictor_factory.model_types} does not require registration"
            )
            return

        if not isinstance(self._predictor_factory.model_types, list):
            raise ValueError(f"Model types must be a list.")

        for model_registration_entity in self._predictor_factory.model_types:
            try:
                self._model_types_service.register_model_type(model_registration_entity)
            except ServiceProxyDuplicateError:
                self._logger.info(
                    f"[ModelTypeService] Model type {model_registration_entity.code} already registered"
                )
                return
            except ServiceProxyError as error:
                self._logger.error(f"[ModelTypeService] Service error occurred during model type registration: {error}")
                raise
            except Exception as error:
                self._logger.error(f"[ModelTypeService] Failed to register model type: {error}")
                raise

        self._logger.info(
            f"[ModelTypeService] Model types: "
            f"{[model.code for model in self._predictor_factory.model_types]} registered successfully"
        )
