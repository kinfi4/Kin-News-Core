from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from telethon.tl.custom.message import Message

from kin_txt_core.datasources.telegram.utils import compose_message_link


class TelegramMessageEntity(BaseModel):
    text: Optional[str] = Field(None)
    channel_title: str = Field(..., alias="channelTitle")
    message_link: str = Field(..., alias="messageLink")
    created_at: datetime = Field(..., alias="createdAt")

    class Config:
        allow_population_by_field_name = True

    @classmethod
    def from_telegram_obj(cls, message: Message) -> "TelegramMessageEntity":
        return cls(
            text=message.text,
            channel_title=message.chat.title,
            message_link=compose_message_link(message.chat.username, message.id),
            created_at=message.date,
        )
