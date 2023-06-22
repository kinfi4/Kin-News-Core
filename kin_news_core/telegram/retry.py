from typing import Any, Callable
from functools import wraps


def retry_connection_async(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(self, *args, **kwargs) -> Any:
        if self._client is None or not self._client.is_connected():
            self._client = self._initialize_client()

        return await func(self, *args, **kwargs)

    return wrapper


def retry_connection_sync(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(self, *args, **kwargs) -> Any:
        if self._client is None or not self._client.is_connected():
            self._client = self._initialize_client()

        return func(self, *args, **kwargs)

    return wrapper
