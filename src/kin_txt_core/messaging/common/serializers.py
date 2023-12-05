import json
from typing import Type
from copy import deepcopy
from datetime import date, datetime

from kin_txt_core.messaging.dtos.event import BasicEvent
from kin_txt_core.messaging.interfaces import ISerializer, IDeserializer
from kin_txt_core.constants import DEFAULT_DATE_FORMAT, DEFAULT_DATETIME_FORMAT


class JsonSerializer(IDeserializer, ISerializer):
    def deserialize(self, event_class: Type[BasicEvent], data: bytes) -> BasicEvent:
        return event_class(**json.loads(data.decode()))

    def serialize(self, event: BasicEvent) -> bytes:
        data_to_encode = deepcopy(event.dict())
        for key, value in event.dict().items():
            if isinstance(value, datetime):
                data_to_encode[key] = value.strftime(DEFAULT_DATETIME_FORMAT)
            elif isinstance(value, date):
                data_to_encode[key] = value.strftime(DEFAULT_DATE_FORMAT)

        return json.dumps(data_to_encode).encode()
