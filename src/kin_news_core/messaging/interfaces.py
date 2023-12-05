from typing import Type, Callable
from abc import ABC, abstractmethod

from kin_news_core.messaging.dtos.event import BasicEvent


class AbstractEventProducer(ABC):
    @abstractmethod
    def publish(self, destination: str, events: list[BasicEvent]) -> None:
        pass


class AbstractEventSubscriber(ABC):
    @abstractmethod
    def subscribe(self, destination: str, event_class: Type[BasicEvent], callback: Callable):
        pass

    @abstractmethod
    def start_consuming(self) -> None:
        pass


class ISerializer(ABC):
    @abstractmethod
    def serialize(self, event: BasicEvent) -> bytes:
        pass


class IDeserializer(ABC):
    @abstractmethod
    def deserialize(self, event_class: Type[BasicEvent], data: bytes) -> BasicEvent:
        pass
