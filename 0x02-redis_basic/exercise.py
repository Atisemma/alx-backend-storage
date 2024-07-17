#!/usr/bin/env python3
"""
This module defines a Cache class for interacting with Redis.
"""

import redis
import uuid
from typing import Union


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
