from dataclasses import dataclass
from typing import Callable, Type, Any, Optional

from pika.spec import Basic
from pika.adapters.blocking_connection import BlockingChannel

from kin_news_core.messaging.dtos import BasicEvent


@dataclass()
class EventData:
    body: bytes
    channel: BlockingChannel
    method: Basic.Deliver
    headers: dict[str, Any]

    @property
    def delivery_tag(self) -> int:
        return self.method.delivery_tag

    def add_header(self, key: str, value: Any) -> None:
        self.headers[key] = value

    @property
    def event_type(self) -> Optional[str]:
        return self.headers.get('event-type')


@dataclass()
class Subscription:
    aggregate_type: str
    event_class: Type[BasicEvent]
    callback: Callable
