from dataclasses import dataclass

from kin_txt_core.messaging.dtos.event import BasicEvent


@dataclass()
class EventWrapper:
    event: BasicEvent
    payload: bytes
