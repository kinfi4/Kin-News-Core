import logging
from typing import Callable, Type
from functools import partial

from kin_txt_core.messaging.common import JsonSerializer
from kin_txt_core.messaging.dtos.event import BasicEvent
from kin_txt_core.messaging.interfaces import AbstractEventSubscriber, IDeserializer
from kin_txt_core.messaging.rabbit.client import RabbitClient
from kin_txt_core.messaging.rabbit.dtos import Subscription, EventData
from kin_txt_core.messaging.rabbit.utils import retry_connect

_logger = logging.getLogger()


def deserialize_and_callback(event_data: EventData, subscriptions: list[Subscription], deserializer: IDeserializer):
    for sub in subscriptions:
        if event_data.event_type == sub.event_class.__name__:
            _logger.info(f"[RabbitSubscriber] Start handling event {sub.event_class.__name__}...")

            deserialized_event = deserializer.deserialize(sub.event_class, event_data.body)
            sub.callback(deserialized_event)

            _logger.info(f"[RabbitSubscriber] Event {sub.event_class.__name__} successfully handled.")
            return

    _logger.debug(f"[RabbitSubscriber] Skipping event {event_data.event_type} because there is no handler.")


class RabbitSubscriber(AbstractEventSubscriber):
    def __init__(self, client: RabbitClient, deserializer: IDeserializer = JsonSerializer()) -> None:
        self._client = client
        self._deserializer = deserializer

        self._subscriptions: list[Subscription] = []
        self._logger = logging.getLogger(self.__class__.__name__)

    def subscribe(self, destination: str, event_class: Type[BasicEvent], callback: Callable) -> None:
        self._subscriptions.append(Subscription(aggregate_type=destination, callback=callback, event_class=event_class))

    @retry_connect
    def start_consuming(self) -> None:
        self._create_subscriptions()
        self._client.start_consuming()

    def _create_subscriptions(self) -> None:
        unique_exchanges = set([sub.aggregate_type for sub in self._subscriptions])

        for exchange in unique_exchanges:
            target_callback = partial(
                deserialize_and_callback,
                subscriptions=[sub for sub in self._subscriptions if sub.aggregate_type == exchange],
                deserializer=self._deserializer,
            )

            self._client.declare_exchange(exchange)

            queue_name = f"{exchange}-queue"
            self._client.declare_queue(queue_name)

            self._client.bind_exchange_2_queue(exchange, queue_name)
            self._client.bind_callback_2_queue(queue_name, target_callback)
