from kin_txt_core.datasources.reddit import RedditDatasource
from kin_txt_core.datasources.telegram import TelegramDatasource
from kin_txt_core.datasources.common.interface import IDataSource
from kin_txt_core.datasources.constants import DataSourceTypes
from kin_txt_core.reports_building.domain.services.datasources.interface import IDataSourceFactory


class DataSourceFactory(IDataSourceFactory):
    def get_data_source(self, source: DataSourceTypes) -> IDataSource:
        if source == DataSourceTypes.TELEGRAM:
            return TelegramDatasource.from_settings()
        elif source == DataSourceTypes.TWITTER:
            raise NotImplemented("Twitter client is not implemented yet")
        elif source == DataSourceTypes.REDDIT:
            return RedditDatasource.from_settings()
        else:
            raise NotImplemented(f"Data source {source} is not implemented yet")
