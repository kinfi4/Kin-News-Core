from typing import Literal
from abc import ABC, abstractmethod

from kin_txt_core.datasources.common.entities import ClassificationEntity
from kin_txt_core.reports_building.constants import ModelTypes
from kin_txt_core.reports_building.domain.entities import ModelEntity, CustomModelRegistrationEntity, GenerateReportEntity
from kin_txt_core.reports_building.domain.services.predicting.predictor.meta import PredictorValidateModelType
from kin_txt_core.reports_building.domain.services.predicting.preprocessing.interface import ITextPreprocessor


class IPredictor(ITextPreprocessor, ABC):
    @abstractmethod
    def predict_post(self, entity: ClassificationEntity) -> str:
        pass

    @abstractmethod
    def predict_post_tokens(self, entity: ClassificationEntity) -> dict[str, list[str]]:
        pass


class IPredictorFactory(ABC, metaclass=PredictorValidateModelType):
    model_types: list[CustomModelRegistrationEntity] | Literal["GenericModel"]

    @abstractmethod
    def create_predictor(self, model_entity: ModelEntity, generation_request: GenerateReportEntity) -> IPredictor:
        pass

    @abstractmethod
    def is_handling(self, model_type: ModelTypes, model_code: str) -> bool:
        pass
