"""Base HTTP client for API requests."""

import logging
from typing import Any

import httpx

from yhteentoimivuusalusta_mcp.utils.cache import CacheManager

logger = logging.getLogger(__name__)


class BaseClient:
    """Base class for API clients with retry and caching support."""

    def __init__(
        self,
        base_url: str,
        timeout: int = 30,
        retry_count: int = 3,
        cache: CacheManager | None = None,
    ) -> None:
        """Initialize the base client.

        Args:
            base_url: Base URL for the API.
            timeout: Request timeout in seconds.
            retry_count: Number of retries for failed requests.
            cache: Cache manager instance.
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retry_count = retry_count
        self.cache = cache
        self._client: httpx.AsyncClient | None = None

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
    ) -> Any:
        """Make an HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.).
            endpoint: API endpoint path.
            params: Query parameters.
            json_data: JSON body data.
            cache_prefix: Cache key prefix for caching GET requests.
            cache_ttl: Cache TTL in seconds.

        Returns:
            JSON response data.

        Raises:
            httpx.HTTPStatusError: If the request fails after retries.
        """
        # Check cache for GET requests
        if method == "GET" and cache_prefix and self.cache:
            cache_key_args = (endpoint,)
            cache_key_kwargs = params or {}
            cached = self.cache.get(cache_prefix, *cache_key_args, **cache_key_kwargs)
            if cached is not None:
                logger.debug(f"Cache hit for {cache_prefix}:{endpoint}")
                return cached

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

        # All retries exhausted
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
