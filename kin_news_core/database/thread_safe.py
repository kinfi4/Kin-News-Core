import threading
from functools import wraps
from typing import Callable


def thread_safe_function(func: Callable) -> Callable:
    lock = threading.Lock()

    @wraps(func)
    def wrapper(*args, **kwargs):
        with lock:
            return func(*args, **kwargs)

    return wrapper
