from typing import Optional
from datetime import datetime
from abc import ABC, abstractmethod

from kin_news_core.telegram.entities import MessageEntity, ChannelEntity


class ITelegramProxy(ABC):
    @abstractmethod
    def fetch_posts_from_channel(
        self,
        channel_name: str,
        *,
        offset_date: Optional[datetime] = None,
        earliest_date: Optional[datetime] = None,
    ) -> list[MessageEntity]:
        pass

    @abstractmethod
    def get_channel(self, channel_link: str) -> ChannelEntity:
        pass

    @abstractmethod
    def download_channel_profile_photo(self, channel_link: str, path_to_save: str) -> None:
        pass
