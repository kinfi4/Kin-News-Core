from typing import Literal
from abc import ABC, abstractmethod

from kin_txt_core.reports_building.constants import ModelTypes
from kin_txt_core.reports_building.domain.entities import ModelEntity, CustomModelRegistrationEntity
from kin_txt_core.reports_building.domain.services.predicting.predictor.meta import PredictorValidateModelType
from kin_txt_core.reports_building.domain.services.predicting.preprocessing.interface import ITextPreprocessor


class IPredictor(ITextPreprocessor, ABC):
    @abstractmethod
    def predict(self, text: str) -> str:
        pass


class IPredictorFactory(ABC, metaclass=PredictorValidateModelType):
    model_type: CustomModelRegistrationEntity | Literal["GenericModel"]

    @abstractmethod
    def create_predictor(self, model_entity: ModelEntity) -> IPredictor:
        pass

    @abstractmethod
    def is_handling(self, model_type: ModelTypes, model_code: str) -> bool:
        pass
