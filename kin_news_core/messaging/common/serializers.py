import json
from typing import Type
from copy import deepcopy
from datetime import date, datetime

from kin_news_core.messaging.dtos.event import BasicEvent
from kin_news_core.messaging.interfaces import ISerializer, IDeserializer
from kin_news_core.constants import DEFAULT_DATE_FORMAT


class JsonSerializer(IDeserializer, ISerializer):
    def deserialize(self, event_class: Type[BasicEvent], data: bytes) -> BasicEvent:
        print(json.loads(data.decode()))
        print("EVENT INIT")

        event = event_class(**json.loads(data.decode()))

        print("EVENT POST INIT")
        print(event)

        return event

    def serialize(self, event: BasicEvent) -> bytes:
        data_to_encode = deepcopy(event.dict())
        for key, value in event.dict().items():
            if isinstance(value, (datetime, date)):
                data_to_encode[key] = value.strftime(DEFAULT_DATE_FORMAT)

        return json.dumps(data_to_encode).encode()
