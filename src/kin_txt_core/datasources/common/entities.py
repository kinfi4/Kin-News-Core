from typing import Any
from datetime import datetime
from dataclasses import dataclass

from kin_txt_core.datasources.telegram import TelegramMessageEntity


@dataclass
class ClassificationEntity:
    text: str | None
    created_at: datetime | None = None
    blobs: list[bytes] | None = None
    metadata: dict[str, Any] | None = None

    @classmethod
    def from_tg_message_entity(cls, message: TelegramMessageEntity) -> "ClassificationEntity":
        return cls(
            text=message.text,
            created_at=message.created_at,
        )


@dataclass
class DatasourceLink:
    source_link: str
    offset_date: datetime | None = None
    earliest_date: datetime | None = None
    skip_messages_without_text: bool = False
    params: dict[str, Any] | None = None
