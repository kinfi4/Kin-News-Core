from typing import Any
from datetime import datetime
from dataclasses import dataclass

from praw.models import Submission

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

    @classmethod
    def from_reddit_submission(cls, submission: Submission) -> "ClassificationEntity":
        return cls(
            text=f"{submission.title}\n\n{submission.selftext}",
            created_at=datetime.fromtimestamp(submission.created_utc),
        )


@dataclass
class DatasourceLink:
    source_link: str
    offset_date: datetime | None = None
    earliest_date: datetime | None = None
    skip_messages_without_text: bool = False
    params: dict[str, Any] | None = None
