import asyncio
import logging
from datetime import datetime
from typing import Optional

from telethon import TelegramClient
from telethon.errors import FloodWaitError, UsernameInvalidError
from telethon.tl.custom.message import Message
from telethon.tl.types import Channel
from telethon.sessions import StringSession
from telethon import functions

from kin_news_core.exceptions import InvalidChannelURLError, TelegramIsUnavailable
from kin_news_core.telegram.entities import TelegramMessageEntity, TelegramChannelEntity
from kin_news_core.constants import MESSAGES_LIMIT_FOR_ONE_CALL
from kin_news_core.telegram.interfaces import IDataGetterProxy


logging.getLogger("telethon").setLevel(logging.ERROR)


class TelegramClientProxy(IDataGetterProxy):
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
            try:
                return self._client.loop.run_until_complete(
                    self.fetch_posts_from_channel_async(
                        channel_name,
                        offset_date=offset_date,
                        earliest_date=earliest_date,
                        skip_messages_without_text=skip_messages_without_text,
                    )
                )
            except FloodWaitError as error:
                self._logger.error(f"Telegram flood happened, backoff: {error.seconds}")
                raise TelegramIsUnavailable("Telegram flooded!", seconds=error.seconds)

    def get_channel(self, channel_link: str) -> TelegramChannelEntity:
        self._logger.info(f"[TelegramClientProxy] Getting information for channel: {channel_link}")

        self._client = self._initialize_client()
        with self._client:
            return self._client.loop.run_until_complete(
                self.get_channel_async(channel_link)
            )

    def download_channel_profile_photo(self, channel_link: str, path_to_save: str) -> None:
        self._client = self._initialize_client()
        with self._client:
            self._client.loop.run_until_complete(self.download_channel_profile_photo_async(
                channel_link, path_to_save
            ))

    async def fetch_posts_from_channel_async(
        self,
        channel_name: str,
        *,
        offset_date: Optional[datetime] = None,
        earliest_date: Optional[datetime] = None,
        skip_messages_without_text: bool = False,
    ) -> list[TelegramMessageEntity]:
        self._logger.info(f"[TelegramProxy] Fetching data from {channel_name}")

        channel, _, _ = await self.get_channel_async(channel_name)
        messages_to_return = []

        previous_message: Optional[Message] = None
        message: Message
        async for message in self._client.iter_messages(
            channel,
            offset_date=offset_date,
            limit=MESSAGES_LIMIT_FOR_ONE_CALL,
        ):
            if (
                previous_message is not None
                and (previous_message.date == message.date or previous_message.text == message.text)
            ):
                continue

            if skip_messages_without_text and not message.text:
                continue

            local = datetime.now().tzinfo
            post_local_date = message.date.astimezone(tz=local)
            post_local_date = datetime.fromtimestamp(post_local_date.timestamp())

            if earliest_date and post_local_date < earliest_date:
                break

            messages_to_return.append(message)
            previous_message = message

        return [TelegramMessageEntity.from_telegram_obj(msg) for msg in messages_to_return]

    async def get_channel_async(self, channel_link: str) -> TelegramChannelEntity:
        try:
            channel_full_obj = await self._client(functions.channels.GetFullChannelRequest(channel=channel_link))
        except (ValueError, TypeError, UsernameInvalidError) as err:
            self._logger.warning(f"Impossible to find channel for {channel_link}, with error: {str(err)}")
            raise InvalidChannelURLError(f"Channel link {channel_link} is invalid, or channel with this name does not exists")

        return TelegramChannelEntity.from_telegram_obj(
            channel_full_obj.chats[0],
            channel_full_obj.full_chat.about,
            channel_full_obj.full_chat.participants_count,
        )

    async def download_channel_profile_photo_async(self, channel_link: str, path_to_save: str) -> None:
        try:
            await self._client.download_profile_photo(channel_link, file=path_to_save)
        except ValueError as err:
            self._logger.warning(f"Impossible to find channel for {channel_link}, with error: {str(err)}")
            raise InvalidChannelURLError(f"Channel link {channel_link} is invalid, or channel with this name does not exists")

    def _initialize_client(self) -> TelegramClient:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        return TelegramClient(self._session_obj, self._api_id, self._api_hash)
