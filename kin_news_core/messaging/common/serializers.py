import json
from typing import Type
from dataclasses import asdict

from kin_news_core.messaging.dtos.event import BasicEvent
from kin_news_core.messaging.interfaces import ISerializer, IDeserializer


class JsonSerializer(IDeserializer, ISerializer):
    def deserialize(self, event_class: Type[BasicEvent], data: bytes) -> BasicEvent:
        return event_class(**json.loads(data.decode()))

    def serialize(self, event: BasicEvent) -> bytes:
        return json.dumps(asdict(event)).encode()
