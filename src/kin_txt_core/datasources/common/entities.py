from typing import Any
from datetime import datetime
from dataclasses import dataclass

from praw.models import Submission
from telethon.tl.custom.message import Message


@dataclass(slots=True)
class ClassificationEntity:
    text: str | None
    created_at: datetime | None = None
    source_link: str | None = None
    blobs: list[bytes] | None = None
    metadata: dict[str, Any] | None = None

    @classmethod
    def from_tg_message(cls, source_link: str, message: Message) -> "ClassificationEntity":
        return cls(
            text=message.text,
            created_at=message.date,
            source_link=source_link,
        )

    @classmethod
    def from_reddit_submission(cls, source_link: str, submission: Submission) -> "ClassificationEntity":
        return cls(
            text=f"{submission.title}\n\n{submission.selftext}",
            created_at=datetime.fromtimestamp(submission.created_utc),
            source_link=source_link,
        )


@dataclass(slots=True)
class DatasourceLink:
    source_link: str
    offset_date: datetime | None = None
    earliest_date: datetime | None = None
    skip_messages_without_text: bool = False
    params: dict[str, Any] | None = None
