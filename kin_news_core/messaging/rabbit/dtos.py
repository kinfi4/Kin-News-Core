from dataclasses import dataclass
from typing import Callable, Type

from pika.spec import Basic
from pika.adapters.blocking_connection import BlockingChannel

from kin_news_core.messaging.dtos import BasicEvent


@dataclass()
class EventData:
    body: bytes
    channel: BlockingChannel
    method: Basic.Deliver

    @property
    def delivery_tag(self) -> int:
        return self.method.delivery_tag


@dataclass()
class Subscription:
    aggregate_type: str
    event_class: Type[BasicEvent]
    callback: Callable
