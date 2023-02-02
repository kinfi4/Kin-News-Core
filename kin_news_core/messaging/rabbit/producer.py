import logging

from kin_news_core.messaging.dtos.event import BasicEvent
from kin_news_core.messaging.interfaces import AbstractEventProducer, ISerializer
from kin_news_core.messaging.rabbit.client import RabbitClient


class RabbitProducer(AbstractEventProducer):
    def __init__(self, client: RabbitClient, serializer: ISerializer) -> None:
        self._client = client
        self._serializer = serializer
        self._logger = logging.getLogger(self.__class__.__name__)

    def publish(self, destination: str, events: list[BasicEvent]) -> None:
        for event in events:
            self._logger.info(f'Publishing event: {event.__class__.__name__} to exchange: {destination}')
            serialized_event = self._serializer.serialize(event)

            self._client.publish_event(destination, serialized_event)
