"""Caching utilities for the MCP server."""

import hashlib
import json
from pathlib import Path
from typing import Any

from diskcache import Cache

# Cache TTL settings (in seconds)
CACHE_TTL = {
    "vocabularies": 86400,  # 24 hours - vocabulary list changes rarely
    "vocabulary": 86400,  # 24 hours
    "concepts": 43200,  # 12 hours - concepts may be updated
    "concept": 43200,  # 12 hours
    "search": 3600,  # 1 hour - search results
    "data_models": 86400,  # 24 hours - models change rarely
    "data_model": 86400,  # 24 hours
    "classes": 43200,  # 12 hours
    "class": 43200,  # 12 hours
    "code_schemes": 3600,  # 1 hour - code lists may update
    "code_scheme": 3600,  # 1 hour
    "codes": 3600,  # 1 hour
}

# Stale cache TTL - how long to keep data for offline mode (7 days)
STALE_CACHE_TTL = 604800


class CacheManager:
    """Manages caching for API responses."""

    def __init__(
        self,
        enabled: bool = True,
        directory: str = "~/.cache/yhteentoimivuusalusta",
    ) -> None:
        """Initialize the cache manager.

        Args:
            enabled: Whether caching is enabled.
            directory: Cache directory path.
        """
        self.enabled = enabled
        self._cache: Cache | None = None

        if enabled:
            cache_dir = Path(directory).expanduser()
            cache_dir.mkdir(parents=True, exist_ok=True)
            self._cache = Cache(str(cache_dir))

    def _make_key(self, prefix: str, *args: Any, **kwargs: Any) -> str:
        """Create a cache key from prefix and arguments.

        Args:
            prefix: Key prefix (e.g., 'vocabulary', 'concept').
            *args: Positional arguments to include in key.
            **kwargs: Keyword arguments to include in key.

        Returns:
            Cache key string.
        """
        key_parts = [prefix] + [str(a) for a in args]
        if kwargs:
            # Sort kwargs for consistent key generation
            sorted_kwargs = sorted(kwargs.items())
            key_parts.append(json.dumps(sorted_kwargs, sort_keys=True))

        key_str = ":".join(key_parts)
        # Use hash for long keys
        if len(key_str) > 200:
            key_hash = hashlib.md5(key_str.encode()).hexdigest()
            return f"{prefix}:{key_hash}"
        return key_str

    def get(self, prefix: str, *args: Any, **kwargs: Any) -> Any | None:
        """Get a value from cache.

        Args:
            prefix: Key prefix.
            *args: Key arguments.
            **kwargs: Key keyword arguments.

        Returns:
            Cached value or None if not found.
        """
        if not self.enabled or not self._cache:
            return None

        key = self._make_key(prefix, *args, **kwargs)
        return self._cache.get(key)

    def set(
        self,
        prefix: str,
        value: Any,
        *args: Any,
        ttl: int | None = None,
        **kwargs: Any,
    ) -> None:
        """Set a value in cache.

        Args:
            prefix: Key prefix.
            value: Value to cache.
            *args: Key arguments.
            ttl: Time-to-live in seconds. If None, uses default for prefix.
            **kwargs: Key keyword arguments.
        """
        if not self.enabled or not self._cache:
            return

        key = self._make_key(prefix, *args, **kwargs)
        expire = ttl if ttl is not None else CACHE_TTL.get(prefix, 3600)
        self._cache.set(key, value, expire=expire)

        # Also store a stale backup with longer TTL for offline mode
        stale_key = f"stale:{key}"
        self._cache.set(stale_key, value, expire=STALE_CACHE_TTL)

    def get_stale(self, prefix: str, *args: Any, **kwargs: Any) -> Any | None:
        """Get a stale value from cache for offline mode.

        This retrieves data that may be older but is kept longer
        for offline fallback scenarios.

        Args:
            prefix: Key prefix.
            *args: Key arguments.
            **kwargs: Key keyword arguments.

        Returns:
            Stale cached value or None if not found.
        """
        if not self.enabled or not self._cache:
            return None

        key = self._make_key(prefix, *args, **kwargs)
        stale_key = f"stale:{key}"
        return self._cache.get(stale_key)

    def delete(self, prefix: str, *args: Any, **kwargs: Any) -> bool:
        """Delete a value from cache.

        Args:
            prefix: Key prefix.
            *args: Key arguments.
            **kwargs: Key keyword arguments.

        Returns:
            True if deleted, False if not found.
        """
        if not self.enabled or not self._cache:
            return False

        key = self._make_key(prefix, *args, **kwargs)
        return self._cache.delete(key)

    def clear(self) -> None:
        """Clear all cached data."""
        if self._cache:
            self._cache.clear()

    def close(self) -> None:
        """Close the cache connection."""
        if self._cache:
            self._cache.close()
