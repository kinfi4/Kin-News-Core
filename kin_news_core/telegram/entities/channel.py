from pydantic import BaseModel, Field
from telethon.tl.types import Channel

from kin_news_core.telegram.utils import compose_participants_count


class TelegramChannelEntity(BaseModel):
    link: str
    title: str
    description: str
    participants_count: str = Field(..., alias='subscribersNumber')

    class Config:
        allow_population_by_field_name = True

    @classmethod
    def from_telegram_obj(cls, channel: Channel, about: str, participants_count: int) -> 'TelegramChannelEntity':
        return cls(
            link=channel.username,
            title=channel.title,
            participants_count=compose_participants_count(participants_count),
            description=about,
        )
