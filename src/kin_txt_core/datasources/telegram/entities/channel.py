from pydantic import ConfigDict, BaseModel, Field
from telethon.tl.types import Channel

from kin_txt_core.datasources.telegram.utils import compose_participants_count


class TelegramChannelEntity(BaseModel):
    link: str
    title: str
    description: str
    participants_count: str = Field(..., alias="subscribersNumber")
    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_telegram_obj(cls, channel: Channel, about: str, participants_count: int) -> "TelegramChannelEntity":
        return cls(
            link=channel.username,
            title=channel.title,
            participants_count=compose_participants_count(participants_count),
            description=about,
        )
