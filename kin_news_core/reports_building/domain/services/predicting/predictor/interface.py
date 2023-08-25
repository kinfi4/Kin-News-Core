from abc import ABC, abstractmethod

from kin_news_core.reports_building.domain.entities import ModelEntity
from kin_news_core.reports_building.domain.services.predicting.predictor.meta import PredictorMetaClass
from kin_news_core.reports_building.domain.services.predicting.preprocessing.interface import ITextPreprocessor


class IPredictor(ITextPreprocessor, ABC, metaclass=PredictorMetaClass):
    model_type_code_list: tuple[str]

    @abstractmethod
    def predict(self, text: str) -> str:
        pass


class IPredictorFactory(ABC):
    def __init__(self, model_entity: ModelEntity) -> None:
        self._model_entity = model_entity

    @abstractmethod
    def create_predictor(self) -> IPredictor:
        pass
