from typing import NoReturn

from kin_txt_core.datasources.telegram import TelegramDatasource
from kin_txt_core.datasources.common import IDataSource
from kin_txt_core.datasources.constants import DataSourceTypes
from kin_txt_core.reports_building.domain.services.datasources.interface import IDataSourceFactory


class DataSourceFactory(IDataSourceFactory):
    def get_data_source(self, source: DataSourceTypes) -> IDataSource:
        if source == DataSourceTypes.TELEGRAM:
            return self._build_telegram_client()
        elif source == DataSourceTypes.TWITTER:
            raise NotImplemented("Twitter client is not implemented yet")

    def _build_telegram_client(self) -> TelegramDatasource:
        if not self.settings.telegram:
            raise ValueError("Telegram settings are not provided")

        return TelegramDatasource(
            session_str=self.settings.telegram.session_string,
            api_id=self.settings.telegram.api_id,
            api_hash=self.settings.telegram.api_hash,
        )

    def _build_twitter_client(self) -> NoReturn:
        raise NotImplemented("Twitter client is not implemented yet")
