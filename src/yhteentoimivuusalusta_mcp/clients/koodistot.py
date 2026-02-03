"""Koodistot (Code Lists) API client."""

import logging
from typing import Any

from yhteentoimivuusalusta_mcp.clients.base import BaseClient
from yhteentoimivuusalusta_mcp.models.schemas import (
    Code,
    CodeScheme,
    LocalizedString,
    Status,
)
from yhteentoimivuusalusta_mcp.utils.cache import CacheManager

logger = logging.getLogger(__name__)


class KoodistotClient(BaseClient):
    """Client for the Koodistot (Code Lists) API.

    API Base: https://koodistot.suomi.fi/codelist-api/api/v1/
    """

    def __init__(
        self,
        base_url: str = "https://koodistot.suomi.fi/codelist-api/api/v1",
        timeout: int = 30,
        retry_count: int = 3,
        cache: CacheManager | None = None,
    ) -> None:
        """Initialize the Koodistot client."""
        super().__init__(base_url, timeout, retry_count, cache)

    async def list_registries(self) -> list[dict[str, Any]]:
        """List all code registries.

        Returns:
            List of registry information.
        """
        data = await self.get(
            "/coderegistries",
            cache_prefix="registries",
        )

        return data.get("results", [])

    async def search_code_schemes(
        self,
        query: str,
        registry: str | None = None,
        max_results: int = 10,
    ) -> list[CodeScheme]:
        """Search for code schemes (code lists).

        Args:
            query: Search term.
            registry: Optional registry ID to limit search.
            max_results: Maximum number of results.

        Returns:
            List of matching code schemes.
        """
        params: dict[str, Any] = {
            "searchTerm": query,
            "pageSize": max_results,
        }

        if registry:
            endpoint = f"/coderegistries/{registry}/codeschemes"
        else:
            endpoint = "/codeschemes"

        data = await self.get(
            endpoint,
            params=params,
            cache_prefix="search",
        )

        schemes = []
        for item in data.get("results", []):
            scheme = self._parse_code_scheme(item)
            if scheme:
                schemes.append(scheme)

        return schemes

    async def get_code_scheme(
        self,
        registry: str,
        scheme: str,
    ) -> CodeScheme | None:
        """Get a specific code scheme.

        Args:
            registry: Code registry ID.
            scheme: Code scheme ID.

        Returns:
            CodeScheme object or None if not found.
        """
        try:
            data = await self.get(
                f"/coderegistries/{registry}/codeschemes/{scheme}",
                cache_prefix="code_scheme",
            )
            return self._parse_code_scheme(data)
        except Exception as e:
            logger.error(f"Failed to get code scheme {registry}/{scheme}: {e}")
            return None

    async def get_codes(
        self,
        registry: str,
        scheme: str,
        status: str | None = "VALID",
        page_size: int = 500,
    ) -> list[Code]:
        """Get all codes from a code scheme.

        Args:
            registry: Code registry ID.
            scheme: Code scheme ID.
            status: Filter by status (VALID, DRAFT, DEPRECATED).
            page_size: Number of results per page.

        Returns:
            List of codes.
        """
        params: dict[str, Any] = {
            "pageSize": page_size,
        }
        if status:
            params["status"] = status

        data = await self.get(
            f"/coderegistries/{registry}/codeschemes/{scheme}/codes",
            params=params,
            cache_prefix="codes",
        )

        codes = []
        for item in data.get("results", []):
            code = self._parse_code(item)
            if code:
                codes.append(code)

        return codes

    async def get_code(
        self,
        registry: str,
        scheme: str,
        code_value: str,
    ) -> Code | None:
        """Get a specific code.

        Args:
            registry: Code registry ID.
            scheme: Code scheme ID.
            code_value: The code value.

        Returns:
            Code object or None if not found.
        """
        try:
            data = await self.get(
                f"/coderegistries/{registry}/codeschemes/{scheme}/codes/{code_value}",
                cache_prefix="code",
            )
            return self._parse_code(data)
        except Exception as e:
            logger.error(f"Failed to get code {code_value}: {e}")
            return None

    async def list_code_schemes(
        self,
        registry: str,
        page_size: int = 100,
        page: int = 0,
    ) -> list[CodeScheme]:
        """List all code schemes in a registry.

        Args:
            registry: Code registry ID.
            page_size: Number of results per page.
            page: Page number (0-indexed).

        Returns:
            List of code schemes.
        """
        params = {
            "pageSize": page_size,
            "pageFrom": page,
        }

        data = await self.get(
            f"/coderegistries/{registry}/codeschemes",
            params=params,
            cache_prefix="code_schemes",
        )

        schemes = []
        for item in data.get("results", []):
            scheme = self._parse_code_scheme(item)
            if scheme:
                schemes.append(scheme)

        return schemes

    def _parse_code_scheme(self, data: dict[str, Any]) -> CodeScheme | None:
        """Parse code scheme from API response."""
        if not data:
            return None

        try:
            label = self._parse_localized(data.get("prefLabel", {}))
            description = self._parse_localized(data.get("description", {}))

            # Extract registry from URI or data
            registry = ""
            if "codeRegistry" in data:
                registry = data["codeRegistry"].get("codeValue", "")
            elif "uri" in data:
                # Parse registry from URI
                uri_parts = data["uri"].split("/")
                if len(uri_parts) > 4:
                    registry = uri_parts[-2]

            return CodeScheme(
                id=data.get("codeValue", data.get("id", "")),
                registry=registry,
                uri=data.get("uri", ""),
                label=label,
                description=description,
                version=data.get("version"),
                code_count=data.get("codeCount", 0),
                codes=[],  # Codes loaded separately
            )
        except Exception as e:
            logger.error(f"Failed to parse code scheme: {e}")
            return None

    def _parse_code(self, data: dict[str, Any]) -> Code | None:
        """Parse code from API response."""
        if not data:
            return None

        try:
            label = self._parse_localized(data.get("prefLabel", {}))
            definition = self._parse_localized(data.get("definition", {}))

            # Get broader code if exists
            broader_code = None
            if "broaderCode" in data and data["broaderCode"]:
                broader_code = data["broaderCode"].get("codeValue")

            return Code(
                code=data.get("codeValue", ""),
                uri=data.get("uri", ""),
                label=label,
                definition=definition,
                status=self._parse_status(data.get("status", "VALID")),
                broader_code=broader_code,
                order=data.get("order"),
            )
        except Exception as e:
            logger.error(f"Failed to parse code: {e}")
            return None

    def _parse_localized(self, data: dict[str, Any] | str | None) -> LocalizedString:
        """Parse localized string from API response."""
        if isinstance(data, str):
            return LocalizedString(fi=data)
        if not data:
            return LocalizedString()
        return LocalizedString(
            fi=data.get("fi"),
            en=data.get("en"),
            sv=data.get("sv"),
        )

    def _parse_status(self, status: str) -> Status:
        """Parse status string to Status enum."""
        try:
            return Status(status.upper())
        except ValueError:
            return Status.VALID
