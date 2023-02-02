import logging
from typing import Callable, Type
from functools import partial

from kin_news_core.messaging.dtos.event import BasicEvent
from kin_news_core.messaging.interfaces import AbstractEventSubscriber, IDeserializer
from kin_news_core.messaging.rabbit.client import RabbitClient
from kin_news_core.messaging.rabbit.dtos import Subscription


def deserialize_and_callback(body: bytes, callback: Callable, deserializer: IDeserializer, event_class: Type[BasicEvent]):
    deserialized_event = deserializer.deserialize(event_class, body)
    callback(deserialized_event)


class RabbitSubscriber(AbstractEventSubscriber):
    def __init__(self, client: RabbitClient, deserializer: IDeserializer) -> None:
        self._client = client
        self._deserializer = deserializer

        self._subscriptions = []
        self._logger = logging.getLogger(self.__class__.__name__)

    def subscribe(self, destination: str, event_class: Type[BasicEvent], callback: Callable) -> None:
        callback = partial(
            deserialize_and_callback,
            callback=callback,
            event_class=event_class,
            deserializer=self._deserializer,
        )

        self._subscriptions.append(Subscription(aggregate_type=destination, callback=callback))

    def start_consuming(self) -> None:
        self._create_subscriptions()
        self._client.start_consuming()

    def _create_subscriptions(self) -> None:
        for subscription in self._subscriptions:
            self._client.declare_exchange(subscription.aggregate_type)

            queue_name = f'{subscription.aggregate_type}-queue'
            self._client.declare_queue(queue_name)

            self._client.bind_exchange_2_queue(subscription.aggregate_type, queue_name)

            self._client.bind_callback_2_queue(queue_name, subscription.callback)
