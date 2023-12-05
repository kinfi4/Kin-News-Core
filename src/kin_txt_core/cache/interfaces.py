from abc import ABC, abstractmethod

from kin_txt_core.datasources.telegram import TelegramChannelEntity


class AbstractCache(ABC):
    @abstractmethod
    def get_channel_info(self, channel_link: str) -> TelegramChannelEntity:
        pass

    @abstractmethod
    def get_channel_photo_url(self, channel_link: str) -> str:
        pass

    @abstractmethod
    def set_channel_info(self, channel: TelegramChannelEntity) -> None:
        pass

    @abstractmethod
    def set_channel_photo_url(self, channel_link: str, photo_url: str) -> None:
        pass
