import logging

from kin_txt_core.messaging import AbstractEventProducer, ISerializer, BasicEvent
from kin_txt_core.messaging.common import JsonSerializer
from kin_txt_core.messaging.rabbit import RabbitClient
from kin_txt_core.messaging.rabbit.utils import retry_connect


class RabbitProducer(AbstractEventProducer):
    def __init__(self, client: RabbitClient, serializer: ISerializer = JsonSerializer()) -> None:
        self._client = client
        self._serializer = serializer
        self._logger = logging.getLogger(self.__class__.__name__)

    @retry_connect
    def publish(self, destination: str, events: list[BasicEvent]) -> None:
        for event in events:
            self._logger.info(f"[RabbitProducer] Publishing event: {event.__class__.__name__} to exchange: {destination}")
            serialized_event = self._serializer.serialize(event)

            self._client.publish_event(destination, serialized_event, headers={"event-type": event.__class__.__name__})
