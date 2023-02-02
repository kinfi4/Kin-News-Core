from dataclasses import dataclass
from typing import Callable

from pika.spec import Basic
from pika.adapters.blocking_connection import BlockingChannel


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
    callback: Callable
