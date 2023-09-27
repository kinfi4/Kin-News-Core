from abc import ABC, abstractmethod

from kin_news_core.datasources.common.entities import ClassificationEntity, DatasourceLink


class IDataSource(ABC):
    @abstractmethod
    def fetch_data(self, source: DatasourceLink) -> list[ClassificationEntity]:
        pass
