import logging
from typing import Callable

from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

from kin_txt_core.messaging.rabbit.dtos import EventData


class RabbitCallbackWrapper:
    def __init__(self, event_handler: Callable) -> None:
        self._event_handler = event_handler
        self._logger = logging.getLogger(self.__class__.__name__)

    def __call__(
        self,
        channel: BlockingChannel,
        method: Basic.Deliver,
        properties: BasicProperties,
        body: bytes,
    ) -> None:
        event_data = EventData(method=method, channel=channel, body=body, headers=properties.headers)

        try:
            self._handle_event(event_data)
        except Exception as err:
            self._handle_error(event_data, err)

    def _handle_event(self, event_data: EventData) -> None:
        event_data.channel.basic_ack(delivery_tag=event_data.delivery_tag)

        self._event_handler(event_data=event_data)

    def _handle_error(self, _: EventData, exc: Exception) -> None:
        self._logger.error(
            f"[RabbitCallbackWrapper] "
            f"During handling event error {exc.__class__.__name__} occurred with message: {str(exc)}",
            exc_info=True,
        )
