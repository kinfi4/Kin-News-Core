from pydantic import BaseModel, Field
from telethon.tl.custom.message import Message

from kin_news_core.telegram.utils import compose_message_link


class MessageEntity(BaseModel):
    text: str
    channel_title: str = Field(..., alias='channelTitle')
    message_link: str = Field(..., alias='messageLink')

    class Config:
        allow_population_by_field_name = True

    @classmethod
    def from_telegram_obj(cls, message: Message) -> 'MessageEntity':
        return cls(
            text=message.text,
            channel_title=message.chat.title,
            message_link=compose_message_link(message.chat.username, message.id),
        )
