import logging

from kin_txt_core.exceptions import ServiceProxyError, ServiceProxyDuplicateError
from kin_txt_core.messaging import AbstractEventProducer
from kin_txt_core.reports_building.domain.services.predicting import IPredictorFactory
from kin_txt_core.reports_building.domain.entities import CustomModelRegistrationEntity
from kin_txt_core.reports_building.events import ReportsBuilderCreated

__all__ = ["ModelTypeRegistrationService"]


class ModelTypeRegistrationService:
    MODEL_TYPES_EXCHANGE = "ModelTypes"

    def __init__(
        self,
        predictor_factory: IPredictorFactory,
        events_producer: AbstractEventProducer,
    ) -> None:
        self._predictor_factory = predictor_factory
        self._events_producer = events_producer

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
            self._logger.info(f"[ModelTypeService] Registering model {model_registration_entity.code}...")

            try:
                self._publish_registration_event(model_registration_entity)
            except ServiceProxyDuplicateError:
                self._logger.info(
                    f"[ModelTypeService] Model type {model_registration_entity.code} already registered"
                )
                continue
            except ServiceProxyError as error:
                self._logger.error(f"[ModelTypeService] Service error occurred during model type registration: {error}")
                raise
            except Exception as error:
                self._logger.error(f"[ModelTypeService] Failed to register model type: {error}")
                raise

            self._logger.info(f"Model {model_registration_entity.code} registration event sent successfully")

    def _publish_registration_event(self, registration_entity: CustomModelRegistrationEntity) -> None:
        event = ReportsBuilderCreated(
            code=registration_entity.code,
            name=registration_entity.name,
            owner_username=registration_entity.owner_username,
            category_mapping=registration_entity.category_mapping,
            preprocessing_config=registration_entity.preprocessing_config,
        )

        self._events_producer.publish(self.MODEL_TYPES_EXCHANGE, [event])
