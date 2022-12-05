import pickle
import logging
from typing import Optional

from redis import Redis

from kin_news_core.cache.interfaces import AbstractCache
from kin_news_core.telegram.entities import TelegramChannelEntity


class RedisCache(AbstractCache):
    def __init__(self, redis_channel_client: Redis, redis_photo_client: Redis) -> None:
        self._redis_channel_client = redis_channel_client
        self._redis_photo_client = redis_photo_client

        self._logger = logging.getLogger(self.__class__.__name__)

    def get_channel_info(self, channel_link: str) -> Optional[TelegramChannelEntity]:
        encoded_channel = self._redis_channel_client.get(name=channel_link)
        if encoded_channel is None:  # that means that we don't have this in cache
            return None

        decoded_channel_dict = pickle.loads(encoded_channel)

        self._logger.info(f'[RedisCache] Getting cache info for channel: {channel_link}')
        return TelegramChannelEntity(**decoded_channel_dict)

    def set_channel_info(self, channel: TelegramChannelEntity) -> None:
        self._logger.info(f'[RedisCache] Set cache info for channel: {channel.link}')

        encoded_channel = pickle.dumps(channel.dict())
        self._redis_channel_client.set(name=channel.link, value=encoded_channel)

    def get_channel_photo_url(self, channel_link: str) -> Optional[str]:

        photo_url = self._redis_photo_client.get(name=channel_link)

        if photo_url is not None:
            self._logger.info(f'[RedisCache] Getting cache info for channel photo: {channel_link}')
            return photo_url.decode()

    def set_channel_photo_url(self, channel_link: str, photo_url: str) -> None:
        self._logger.info(f'[RedisCache] Set cache info for channel photo: {channel_link}')

        self._redis_photo_client.set(name=channel_link, value=photo_url)

    @classmethod
    def from_settings(
        cls,
        hostname: str,
        port: int = 6379,
        password: Optional[str] = None,
        *,
        photo_db_name: int = 0,
        channel_db_name: int = 1,
    ) -> "RedisCache":
        redis_photo_client = Redis(host=hostname, port=port, password=password, db=photo_db_name)
        redis_channel_client = Redis(host=hostname, port=port, password=password, db=channel_db_name)

        return cls(redis_channel_client, redis_photo_client)
