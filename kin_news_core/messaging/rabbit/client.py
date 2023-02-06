import random
from typing import Optional, Callable

from pika import URLParameters
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection
from pika.exchange_type import ExchangeType

from kin_news_core.messaging import IDeserializer
from kin_news_core.messaging.rabbit.callback import RabbitCallbackWrapper
from kin_news_core.messaging.common.serializers import JsonSerializer


class RabbitClient:
    _DLX_NAME = 'dlx-topic'
    _MIN_CHANNEL_IDX = 1
    _MAX_CHANNEL_IDX = 10000

    def __init__(self, connection_string: str, deserializer: IDeserializer = JsonSerializer()) -> None:
        self._settings = URLParameters(url=connection_string)
        self._deserializer = deserializer
        self._connection: Optional[BlockingConnection] = None
        self._channel: Optional[BlockingChannel] = None

    @property
    def connection(self) -> BlockingConnection:
        if self._connection is None:
            self._connection = BlockingConnection(self._settings)

        return self._connection

    @property
    def channel(self) -> BlockingChannel:
        if self._channel is None:
            self._channel = self.connection.channel(random.randint(self._MIN_CHANNEL_IDX, self._MAX_CHANNEL_IDX))

        return self._channel

    def declare_exchange(self, exchange_name: str, exchange_type: Optional[str] = None) -> None:
        if exchange_type is None:
            exchange_type = ExchangeType.fanout.value

        self.channel.exchange_declare(exchange_name, exchange_type=exchange_type)

    def declare_queue(self, queue_name: str) -> None:
        queue_params = self._dead_letters_exchange_declare(queue_name)
        self.channel.queue_declare(queue_name, arguments=queue_params, durable=True)

    def bind_exchange_2_queue(self, exchange: str, queue: str, routing_key: Optional[str] = None) -> None:
        self.channel.queue_bind(exchange=exchange, queue=queue, routing_key=routing_key)

    def bind_callback_2_queue(self, queue_name: str, callback: Callable) -> None:
        callback_wrapper = RabbitCallbackWrapper(callback)
        self.channel.basic_consume(queue_name, on_message_callback=callback_wrapper)

    def publish_event(self, exchange: str, message: bytes | str, routing_key: str = ''):
        self.channel.basic_publish(exchange, body=message, routing_key=routing_key)

    def start_consuming(self) -> None:
        self.channel.start_consuming()

    def _dead_letters_exchange_declare(self, target_queue: str) -> dict[str, str]:
        self.channel.exchange_declare(
            exchange=self._DLX_NAME,
            exchange_type=ExchangeType.topic.value,
        )

        dlx_routing_key = f'{target_queue}-routing-key'
        dlx_queue_name = f"{target_queue}-dlx"

        self.channel.queue_declare(dlx_queue_name, durable=True)

        self.bind_exchange_2_queue(self._DLX_NAME, dlx_queue_name, dlx_routing_key)

        return {
            "x-dead-letter-exchange": self._DLX_NAME,
            "x-dead-letter-routing-key": dlx_routing_key,
        }
