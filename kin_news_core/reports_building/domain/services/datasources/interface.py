from abc import ABC, abstractmethod

from kin_news_core.datasources.common import IDataSource
from kin_news_core.datasources.constants import DataSourceTypes
from kin_news_core.reports_building.settings import Settings


class IDataSourceFactory(ABC):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @abstractmethod
    def get_data_source(self, source: DataSourceTypes) -> IDataSource:
        pass
