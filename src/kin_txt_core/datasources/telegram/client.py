import asyncio
import logging
from datetime import datetime
from typing import Optional

from telethon import TelegramClient
from telethon.errors import FloodWaitError, UsernameInvalidError
from telethon.tl.custom.message import Message
from telethon.sessions import StringSession
from telethon import functions

from kin_txt_core.datasources.common.entities import DatasourceLink, ClassificationEntity
from kin_txt_core.datasources.common.interface import IDataSource
from kin_txt_core.datasources.settings import TelegramSettings
from kin_txt_core.exceptions import InvalidChannelURLError, TelegramIsUnavailable
from kin_txt_core.datasources.telegram.entities import TelegramChannelEntity
from kin_txt_core.constants import MESSAGES_LIMIT_FOR_ONE_CALL
from kin_txt_core.datasources.telegram.retry import retry_connection_async, retry_connection_sync

logging.getLogger("telethon").setLevel(logging.ERROR)


class TelegramDatasource(IDataSource):
    def __init__(self, session_str: str, api_id: int, api_hash: str) -> None:
        self._session_obj = StringSession(session_str)
        self._api_id = api_id
        self._api_hash = api_hash

        self._client = None
        self._logger = logging.getLogger(self.__class__.__name__)

    def fetch_data(self, source: DatasourceLink) -> list[ClassificationEntity]:
        messages: list[ClassificationEntity] = self.fetch_posts_from_channel(
            source.source_link,
            offset_date=source.offset_date,
            earliest_date=source.earliest_date,
            skip_messages_without_text=source.skip_messages_without_text,
        )

        return messages

    @retry_connection_sync
    def fetch_posts_from_channel(
        self,
        channel_name: str,
        *,
        offset_date: Optional[datetime] = None,
        earliest_date: Optional[datetime] = None,
        skip_messages_without_text: bool = False,
    ) -> list[ClassificationEntity]:
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

    @retry_connection_sync
    def get_channel(self, channel_link: str) -> TelegramChannelEntity:
        self._logger.info(f"[TelegramDatasource] Getting information for channel: {channel_link}")

        with self._client:
            return self._client.loop.run_until_complete(
                self.get_channel_async(channel_link)
            )

    @retry_connection_async
    async def fetch_posts_from_channel_async(
        self,
        channel_name: str,
        *,
        offset_date: Optional[datetime] = None,
        earliest_date: Optional[datetime] = None,
        skip_messages_without_text: bool = False,
    ) -> list[ClassificationEntity]:
        self._logger.info(f"[TelegramProxy] Fetching data from {channel_name}")

        channel_entity: TelegramChannelEntity = await self.get_channel_async(channel_name)
        messages_to_return = []

        previous_message: Optional[Message] = None
        message: Message

        async with self._client:
            async for message in self._client.iter_messages(
                channel_entity.link,
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

        return [ClassificationEntity.from_tg_message(channel_name, msg) for msg in messages_to_return]

    @retry_connection_async
    async def get_channel_async(self, channel_link: str) -> TelegramChannelEntity:
        try:
            async with self._client:
                channel_full_obj = await self._client(functions.channels.GetFullChannelRequest(channel=channel_link))
        except (ValueError, TypeError, UsernameInvalidError) as err:
            self._logger.warning(f"Impossible to find channel for {channel_link}, with {err.__class__.__name__}: {str(err)}")
            raise InvalidChannelURLError(f"Channel link {channel_link} is invalid, or channel with this name does not exists")

        return TelegramChannelEntity.from_telegram_obj(
            channel_full_obj.chats[0],
            channel_full_obj.full_chat.about,
            channel_full_obj.full_chat.participants_count,
        )

    def _initialize_client(self) -> TelegramClient:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        return TelegramClient(self._session_obj, self._api_id, self._api_hash)

    @classmethod
    def from_settings(cls) -> "TelegramDatasource":
        settings = TelegramSettings()
        return cls(
            session_str=settings.session_string,
            api_id=settings.api_id,
            api_hash=settings.api_hash,
        )
