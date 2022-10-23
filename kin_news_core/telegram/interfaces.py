from typing import Optional
from datetime import datetime
from abc import ABC, abstractmethod

from kin_news_core.telegram.entities import ChannelLink, MessageEntity, ChannelEntity


class ITelegramProxy(ABC):
    @abstractmethod
    def fetch_posts_from_channel(
        self,
        channel_name: ChannelLink,
        *,
        offset_date: Optional[datetime] = None,
        earliest_date: Optional[datetime] = None,
    ) -> list[MessageEntity]:
        pass

    @abstractmethod
    def get_channel(self, channel_link: ChannelLink) -> ChannelEntity:
        pass
