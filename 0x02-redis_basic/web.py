#!/usr/bin/env python3
"""
Provides a function to fetch web pages with caching and request counting.
"""

import redis
import requests
from functools import wraps
from typing import Callable


def cache_and_count(expiration: int = 10) -> Callable:
    """
    Decorator to cache the result of a function and count the number of calls.

    Args:
        expiration (int): Cache expiration time in seconds. Default is 10.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(url: str) -> str:
            redis_client = redis.Redis()

            # Create keys for caching and counting
            cache_key = f"cache:{url}"
            count_key = f"count:{url}"

            # Increment the access count
            redis_client.incr(count_key)

            # Check if the result is cached
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return cached_result.decode('utf-8')

            # If not cached, call the original function
            result = func(url)

            # Cache the result with expiration
            redis_client.setex(cache_key, expiration, result)

            return result
        return wrapper
    return decorator


@cache_and_count()
def get_page(url: str) -> str:
    """
    Obtain the HTML content of a particular URL.

    Args:
        url (str): The URL to fetch.

    Returns:
        str: The HTML content of the URL.
    """
    response = requests.get(url)
    return response.text


if __name__ == "__main__":
    url = ("http://slowwly.robertomurray.co.uk"
           "/delay/1000/url/http://www.example.com")

    # First call (not cached)
    print(get_page(url))
    print(f"Count: {redis.Redis().get(f'count:{url}').decode('utf-8')}")

    # Second call (cached)
    print(get_page(url))
    print(f"Count: {redis.Redis().get(f'count:{url}').decode('utf-8')}")
