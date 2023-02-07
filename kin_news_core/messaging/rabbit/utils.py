from typing import Callable
from functools import wraps

from pika.exceptions import AMQPConnectionError


def retry_connect(func: Callable) -> Callable:
    @wraps(func)
    def inner(pubsub, *args, **kwargs):
        while True:
            try:
                return func(pubsub, *args, **kwargs)
            except AMQPConnectionError:
                pubsub._client.reset_connection()

    return inner
