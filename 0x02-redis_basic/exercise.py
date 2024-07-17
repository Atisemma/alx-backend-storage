#!/usr/bin/env python3
"""
This module defines a Cache class for interacting with Redis.
"""

import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


def call_history(method: Callable) -> Callable:
    """
    Decorator to store the history of inputs and outputs for a function.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        # Create input and output list keys
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"

        # Store input arguments
        self._redis.rpush(input_key, str(args))

        # Execute the wrapped function
        output = method(self, *args, **kwargs)

        # Store output
        self._redis.rpush(output_key, str(output))

        return output

    return wrapper


class Cache:
    """
    A class that provides caching functionality using Redis.
    """

    def __init__(self):
        """
        Initialize the Cache instance.
        Creates a Redis client and flushes the database.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store the input data in Redis using a random key and return the key.

        Args:
            data (Union[str, bytes, int, float]): The data to be stored.

        Returns:
            str: The randomly generated key used to store the data.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str,
            fn: Optional[Callable] = None
            ) -> Union[str, bytes, int, float, None]:
        """
        Retrieve data from Redis for the given key and optionally apply
        a conversion function.

        Args:
            key (str): The key to retrieve data for.
            fn (Optional[Callable]): Optional function to convert the data.

        Returns:
            Union[str, bytes, int, float, None]: The retrieved data,
            potentially converted.
        """
        data = self._redis.get(key)
        if data is None:
            return None
        if fn:
            return fn(data)
        return data

    def get_str(self, key: str) -> Union[str, None]:
        """
        Retrieve a string from Redis for the given key.

        Args:
            key (str): The key to retrieve data for.

        Returns:
            The retrieved string or None if key doesn't exist.
        """
        return self.get(key, fn=lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> Union[int, None]:
        """
        Retrieve an integer from Redis for the given key.

        Args:
            key (str): The key to retrieve data for.

        Returns:
            The retrieved integer or None if key doesn't exist.
        """
        return self.get(key, fn=int)
