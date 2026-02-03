"""Base HTTP client for API requests."""

import asyncio
import logging
import time
from typing import Any

import httpx

from yhteentoimivuusalusta_mcp.utils.cache import CacheManager

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple rate limiter using token bucket algorithm."""

    def __init__(self, requests_per_second: float = 10.0) -> None:
        """Initialize the rate limiter.

        Args:
            requests_per_second: Maximum requests per second.
        """
        self.requests_per_second = requests_per_second
        self.min_interval = 1.0 / requests_per_second
        self._last_request_time: float = 0.0
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Acquire permission to make a request, waiting if necessary."""
        async with self._lock:
            now = time.monotonic()
            time_since_last = now - self._last_request_time
            if time_since_last < self.min_interval:
                wait_time = self.min_interval - time_since_last
                await asyncio.sleep(wait_time)
            self._last_request_time = time.monotonic()


class BaseClient:
    """Base class for API clients with retry, caching, and rate limiting support."""

    # Shared rate limiter across all clients (10 requests/second)
    _rate_limiter: RateLimiter | None = None

    def __init__(
        self,
        base_url: str,
        timeout: int = 30,
        retry_count: int = 3,
        cache: CacheManager | None = None,
        rate_limit: float = 10.0,
    ) -> None:
        """Initialize the base client.

        Args:
            base_url: Base URL for the API.
            timeout: Request timeout in seconds.
            retry_count: Number of retries for failed requests.
            cache: Cache manager instance.
            rate_limit: Maximum requests per second.
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retry_count = retry_count
        self.cache = cache
        self._client: httpx.AsyncClient | None = None

        # Initialize shared rate limiter
        if BaseClient._rate_limiter is None:
            BaseClient._rate_limiter = RateLimiter(rate_limit)

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client.

        Returns:
            Async HTTP client instance.
        """
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers={
                    "Accept": "application/json",
                    "User-Agent": "yhteentoimivuusalusta-mcp/0.1.0",
                },
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        cache_prefix: str | None = None,
        cache_ttl: int | None = None,
        allow_stale: bool = True,
    ) -> Any:
        """Make an HTTP request with retry logic and offline mode support.

        Args:
            method: HTTP method (GET, POST, etc.).
            endpoint: API endpoint path.
            params: Query parameters.
            json_data: JSON body data.
            cache_prefix: Cache key prefix for caching GET requests.
            cache_ttl: Cache TTL in seconds.
            allow_stale: If True, return stale cached data when API fails.

        Returns:
            JSON response data.

        Raises:
            httpx.HTTPStatusError: If the request fails after retries.
        """
        cache_key_args = (endpoint,)
        cache_key_kwargs = params or {}

        # Check cache for GET requests
        if method == "GET" and cache_prefix and self.cache:
            cached = self.cache.get(cache_prefix, *cache_key_args, **cache_key_kwargs)
            if cached is not None:
                logger.debug(f"Cache hit for {cache_prefix}:{endpoint}")
                return cached

        # Apply rate limiting
        if BaseClient._rate_limiter:
            await BaseClient._rate_limiter.acquire()

        client = await self._get_client()
        last_error: Exception | None = None

        for attempt in range(self.retry_count):
            try:
                response = await client.request(
                    method=method,
                    url=endpoint,
                    params=params,
                    json=json_data,
                )
                response.raise_for_status()
                data = response.json()

                # Cache successful GET responses
                if method == "GET" and cache_prefix and self.cache:
                    self.cache.set(
                        cache_prefix,
                        data,
                        endpoint,
                        ttl=cache_ttl,
                        **(params or {}),
                    )

                return data

            except httpx.HTTPStatusError as e:
                last_error = e
                # Don't retry client errors (4xx)
                if 400 <= e.response.status_code < 500:
                    logger.warning(f"Client error: {e.response.status_code} for {endpoint}")
                    raise
                logger.warning(
                    f"Request failed (attempt {attempt + 1}/{self.retry_count}): {e}"
                )

            except httpx.RequestError as e:
                last_error = e
                logger.warning(
                    f"Request error (attempt {attempt + 1}/{self.retry_count}): {e}"
                )

        # All retries exhausted - try offline mode with stale cache
        if allow_stale and method == "GET" and cache_prefix and self.cache:
            stale_data = self.cache.get_stale(
                cache_prefix, *cache_key_args, **cache_key_kwargs
            )
            if stale_data is not None:
                logger.info(
                    f"Offline mode: returning stale cache for {cache_prefix}:{endpoint}"
                )
                return stale_data

        # No cached data available
        if last_error:
            raise last_error
        raise RuntimeError(f"Request failed after {self.retry_count} attempts")

    async def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        cache_prefix: str | None = None,
        cache_ttl: int | None = None,
    ) -> Any:
        """Make a GET request.

        Args:
            endpoint: API endpoint path.
            params: Query parameters.
            cache_prefix: Cache key prefix.
            cache_ttl: Cache TTL in seconds.

        Returns:
            JSON response data.
        """
        return await self._request(
            "GET",
            endpoint,
            params=params,
            cache_prefix=cache_prefix,
            cache_ttl=cache_ttl,
        )

    async def post(
        self,
        endpoint: str,
        json_data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Make a POST request.

        Args:
            endpoint: API endpoint path.
            json_data: JSON body data.
            params: Query parameters.

        Returns:
            JSON response data.
        """
        return await self._request(
            "POST",
            endpoint,
            params=params,
            json_data=json_data,
        )
