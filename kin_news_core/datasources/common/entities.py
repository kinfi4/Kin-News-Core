from typing import Any
from datetime import datetime
from dataclasses import dataclass


@dataclass
class ClassificationEntity:
    text: str | None
    created_at: datetime | None = None
    blobs: list[bytes] | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class DatasourceLink:
    source_link: str
    offset_date: datetime | None = None
    earliest_date: datetime | None = None
    skip_messages_without_text: bool = False
    params: dict[str, Any] | None = None
