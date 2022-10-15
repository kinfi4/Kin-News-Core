import logging
from datetime import datetime, timedelta

from django.conf import settings
from telethon import TelegramClient
from telethon.tl.custom.message import Message
from telethon.tl.types import Channel


class TelegramService:
    def __init__(self, telegram_client: TelegramClient):
        self._client = telegram_client
        self._logger = logging.getLogger(self.__class__.__name__)

    def fetch_posts_from_channel(self, channel_name: str, offset_minutes: int):
        self._logger.info(f'[TelegramService] Fetching data from {channel_name}')
        entity: Channel = await self._client.get_entity(channel_name)
        last_post_to_fetch_date = datetime.now() - timedelta(minutes=offset_minutes)

        message: Message
        async for message in self._client.iter_messages(entity):
            post_date = message.date.astimezone(tz=settings.LOCAL_TIMEZONE)

            if last_post_to_fetch_date and post_date < last_post_to_fetch_date:
                break

    @classmethod
    def from_api_config(cls, api_id: int, api_hash: str) -> "TelegramService":
        client = TelegramClient('session-1', api_id, api_hash)

        return cls(telegram_client=client)
