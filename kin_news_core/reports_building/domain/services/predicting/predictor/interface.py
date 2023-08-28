from abc import ABC, abstractmethod

from kin_news_core.reports_building.constants import ModelTypes
from kin_news_core.reports_building.domain.entities import ModelEntity
from kin_news_core.reports_building.domain.services.predicting.preprocessing.interface import ITextPreprocessor


class IPredictor(ITextPreprocessor, ABC):
    model_type_code_list: tuple[str]

    @abstractmethod
    def predict(self, text: str) -> str:
        pass


class IPredictorFactory(ABC):
    @abstractmethod
    def create_predictor(self, model_entity: ModelEntity) -> IPredictor:
        pass

    @abstractmethod
    def is_handling(self, model_type: ModelTypes, model_code: str) -> bool:
        pass
