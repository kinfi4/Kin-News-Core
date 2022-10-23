from abc import ABC, abstractmethod

from kin_news_core.telegram.entities import ChannelEntity


class AbstractCache(ABC):
    @abstractmethod
    def get_channel_info(self, channel_link: str) -> ChannelEntity:
        pass

    @abstractmethod
    def get_channel_photo_url(self, channel_link: str) -> str:
        pass

    @abstractmethod
    def set_channel_info(self, channel: ChannelEntity) -> None:
        pass

    @abstractmethod
    def set_channel_photo_url(self, channel_link: str, photo_url: str) -> None:
        pass
