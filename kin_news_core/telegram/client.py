import asyncio
import logging
from datetime import datetime
from typing import Optional

from telethon import TelegramClient
from telethon.tl.custom.message import Message
from telethon.tl.types import Channel
from telethon.sessions import StringSession
from telethon import functions

from kin_news_core.exceptions import InvalidChannelURLError
from kin_news_core.telegram.entities import TelegramMessageEntity, TelegramChannelEntity
from kin_news_core.constants import MESSAGES_LIMIT_FOR_ONE_CALL
from kin_news_core.telegram.interfaces import ITelegramProxy


logging.getLogger('telethon').setLevel(logging.ERROR)


class TelegramClientProxy(ITelegramProxy):
    def __init__(self, session_str: str, api_id: int, api_hash: str) -> None:
        self._session_obj = StringSession(session_str)
        self._api_id = api_id
        self._api_hash = api_hash

        self._client = None
        self._logger = logging.getLogger(self.__class__.__name__)

    def fetch_posts_from_channel(
        self,
        channel_name: str,
        *,
        offset_date: Optional[datetime] = None,
        earliest_date: Optional[datetime] = None,
        skip_messages_without_text: bool = False,
    ) -> list[TelegramMessageEntity]:
        self._client = self._initialize_client()
        with self._client:
            return self._client.loop.run_until_complete(
                self._fetch_posts(
                    channel_name,
                    offset_date=offset_date,
                    earliest_date=earliest_date,
                    skip_messages_without_text=skip_messages_without_text,
                )
            )

    def get_channel(self, channel_link: str) -> TelegramChannelEntity:
        self._logger.info(f'[TelegramClientProxy] Getting information for channel: {channel_link}')

        self._client = self._initialize_client()
        with self._client:
            channel, about, participants_count = self._client.loop.run_until_complete(
                self._get_channel_entity_info(channel_link)
            )

        return TelegramChannelEntity.from_telegram_obj(channel, about, participants_count)

    def download_channel_profile_photo(self, channel_link: str, path_to_save: str) -> None:
        self._client = self._initialize_client()
        with self._client:
            self._client.loop.run_until_complete(self._download_channel_profile_photo(
                channel_link, path_to_save
            ))

    async def _download_channel_profile_photo(self, channel_link: str, path_to_save: str) -> None:
        try:
            await self._client.download_profile_photo(channel_link, file=path_to_save)
        except ValueError as err:
            self._logger.warning(f'Impossible to find channel for {channel_link}, with error: {str(err)}')
            raise InvalidChannelURLError(f'Channel link {channel_link} is invalid, or channel with this name does not exists')

    async def _fetch_posts(
        self,
        channel_link: str,
        *,
        offset_date: Optional[datetime] = None,
        earliest_date: Optional[datetime] = None,
        skip_messages_without_text: bool = False,
    ) -> list[TelegramMessageEntity]:
        self._logger.info(f'[TelegramProxy] Fetching data from {channel_link}')

        channel, _, _ = await self._get_channel_entity_info(channel_link)
        messages_to_return = []

        message: Message
        async for message in self._client.iter_messages(
            channel,
            offset_date=offset_date,
            limit=MESSAGES_LIMIT_FOR_ONE_CALL,
        ):
            if skip_messages_without_text and not message.text:
                continue

            local = datetime.now().tzinfo
            post_local_date = message.date.astimezone(tz=local)
            post_local_date = datetime.fromtimestamp(post_local_date.timestamp())

            if earliest_date and post_local_date < earliest_date:
                break

            messages_to_return.append(message)

        return [TelegramMessageEntity.from_telegram_obj(msg) for msg in messages_to_return]

    async def _get_channel_entity_info(self, channel_link: str) -> tuple[Channel, str, int]:
        try:
            channel_full_obj = await self._client(functions.channels.GetFullChannelRequest(channel=channel_link))
        except (ValueError, TypeError) as err:
            self._logger.warning(f'Impossible to find channel for {channel_link}, with error: {str(err)}')
            raise InvalidChannelURLError(f'Channel link {channel_link} is invalid, or channel with this name does not exists')

        return (
            channel_full_obj.chats[0],
            channel_full_obj.full_chat.about,
            channel_full_obj.full_chat.participants_count,
        )

    def _initialize_client(self) -> TelegramClient:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        return TelegramClient(self._session_obj, self._api_id, self._api_hash)
