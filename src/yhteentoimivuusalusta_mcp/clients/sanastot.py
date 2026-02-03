"""Sanastot (Terminologies) API client."""

import logging
from typing import Any

from yhteentoimivuusalusta_mcp.clients.base import BaseClient
from yhteentoimivuusalusta_mcp.models.schemas import (
    Concept,
    Language,
    LocalizedString,
    Status,
    Term,
    Vocabulary,
)
from yhteentoimivuusalusta_mcp.utils.cache import CacheManager

logger = logging.getLogger(__name__)


class SanastotClient(BaseClient):
    """Client for the Sanastot (Terminologies) API.

    API Base: https://sanastot.suomi.fi/terminology-api/api/v1/
    """

    def __init__(
        self,
        base_url: str = "https://sanastot.suomi.fi/terminology-api/api/v1",
        timeout: int = 30,
        retry_count: int = 3,
        cache: CacheManager | None = None,
    ) -> None:
        """Initialize the Sanastot client."""
        super().__init__(base_url, timeout, retry_count, cache)

    async def list_vocabularies(
        self,
        page_size: int = 100,
        page: int = 0,
        status: str | None = None,
    ) -> list[Vocabulary]:
        """List all available vocabularies.

        Args:
            page_size: Number of results per page.
            page: Page number (0-indexed).
            status: Filter by status (VALID, DRAFT, etc.).

        Returns:
            List of vocabulary objects.
        """
        params: dict[str, Any] = {
            "pageSize": page_size,
            "pageFrom": page,
        }
        if status:
            params["status"] = status

        data = await self.get(
            "/frontend/terminologies",
            params=params,
            cache_prefix="vocabularies",
        )

        vocabularies = []
        for item in data.get("terminologies", []):
            vocab = self._parse_vocabulary(item)
            if vocab:
                vocabularies.append(vocab)

        return vocabularies

    async def get_vocabulary(self, vocabulary_id: str) -> Vocabulary | None:
        """Get a specific vocabulary by ID.

        Args:
            vocabulary_id: The vocabulary identifier (e.g., 'rakymp').

        Returns:
            Vocabulary object or None if not found.
        """
        try:
            data = await self.get(
                f"/frontend/terminology/{vocabulary_id}",
                cache_prefix="vocabulary",
            )
            return self._parse_vocabulary(data)
        except Exception as e:
            logger.error(f"Failed to get vocabulary {vocabulary_id}: {e}")
            return None

    async def search_concepts(
        self,
        query: str,
        vocabulary_id: str | None = None,
        language: str = "fi",
        max_results: int = 10,
    ) -> list[Concept]:
        """Search for concepts across vocabularies.

        Args:
            query: Search term.
            vocabulary_id: Optional vocabulary ID to limit search.
            language: Search language (fi, en, sv).
            max_results: Maximum number of results.

        Returns:
            List of matching concepts.
        """
        params: dict[str, Any] = {
            "searchTerm": query,
            "language": language,
            "pageSize": max_results,
        }
        if vocabulary_id:
            params["terminologyId"] = vocabulary_id

        data = await self.get(
            "/frontend/searchConcept",
            params=params,
            cache_prefix="search",
        )

        concepts = []
        for item in data.get("concepts", []):
            concept = self._parse_concept(item)
            if concept:
                concepts.append(concept)

        return concepts

    async def get_concept(
        self,
        vocabulary_id: str,
        concept_id: str,
    ) -> Concept | None:
        """Get a specific concept by ID.

        Args:
            vocabulary_id: The vocabulary identifier.
            concept_id: The concept identifier.

        Returns:
            Concept object or None if not found.
        """
        try:
            data = await self.get(
                f"/frontend/terminology/{vocabulary_id}/concept/{concept_id}",
                cache_prefix="concept",
            )
            return self._parse_concept(data, vocabulary_id)
        except Exception as e:
            logger.error(f"Failed to get concept {concept_id}: {e}")
            return None

    async def get_vocabulary_concepts(
        self,
        vocabulary_id: str,
        page_size: int = 100,
        page: int = 0,
    ) -> list[Concept]:
        """Get all concepts from a vocabulary.

        Args:
            vocabulary_id: The vocabulary identifier.
            page_size: Number of results per page.
            page: Page number (0-indexed).

        Returns:
            List of concepts.
        """
        params = {
            "pageSize": page_size,
            "pageFrom": page,
        }

        data = await self.get(
            f"/frontend/terminology/{vocabulary_id}/concepts",
            params=params,
            cache_prefix="concepts",
        )

        concepts = []
        for item in data.get("concepts", []):
            concept = self._parse_concept(item, vocabulary_id)
            if concept:
                concepts.append(concept)

        return concepts

    def _parse_vocabulary(self, data: dict[str, Any]) -> Vocabulary | None:
        """Parse vocabulary data from API response.

        Args:
            data: Raw API response data.

        Returns:
            Parsed Vocabulary object.
        """
        if not data:
            return None

        try:
            label = self._parse_localized(data.get("label", {}))
            description = self._parse_localized(data.get("description", {}))

            # Extract languages from the data
            languages = []
            for lang in data.get("languages", []):
                try:
                    languages.append(Language(lang.lower()))
                except ValueError:
                    pass

            return Vocabulary(
                id=data.get("prefix", data.get("id", "")),
                uri=data.get("uri", ""),
                label=label,
                description=description,
                domain=data.get("informationDomains", []),
                organization=data.get("organizations", [{}])[0].get("label", {}).get("fi")
                if data.get("organizations")
                else None,
                concept_count=data.get("conceptCount", 0),
                status=self._parse_status(data.get("status", "VALID")),
                languages=languages,
            )
        except Exception as e:
            logger.error(f"Failed to parse vocabulary: {e}")
            return None

    def _parse_concept(
        self,
        data: dict[str, Any],
        vocabulary_id: str | None = None,
    ) -> Concept | None:
        """Parse concept data from API response.

        Args:
            data: Raw API response data.
            vocabulary_id: Vocabulary ID if not in data.

        Returns:
            Parsed Concept object.
        """
        if not data:
            return None

        try:
            # Parse labels
            label = self._parse_localized(data.get("label", data.get("prefLabel", {})))
            definition = self._parse_localized(data.get("definition", {}))

            # Parse terms
            terms = []
            for term_data in data.get("terms", []):
                term = self._parse_term(term_data)
                if term:
                    terms.append(term)

            # Parse relations
            broader = [r.get("id", r) for r in data.get("broader", [])]
            narrower = [r.get("id", r) for r in data.get("narrower", [])]
            related = [r.get("related", r) for r in data.get("related", [])]

            return Concept(
                id=data.get("id", data.get("identifier", "")),
                uri=data.get("uri", ""),
                vocabulary_id=data.get("terminology", {}).get("prefix", vocabulary_id or ""),
                preferred_label=label,
                definition=definition,
                terms=terms,
                status=self._parse_status(data.get("status", "VALID")),
                broader=broader if isinstance(broader, list) else [],
                narrower=narrower if isinstance(narrower, list) else [],
                related=related if isinstance(related, list) else [],
            )
        except Exception as e:
            logger.error(f"Failed to parse concept: {e}")
            return None

    def _parse_term(self, data: dict[str, Any]) -> Term | None:
        """Parse term data from API response."""
        if not data:
            return None

        try:
            return Term(
                label=data.get("label", ""),
                language=Language(data.get("language", "fi").lower()),
                status=data.get("status", "PREFERRED"),
                scope=data.get("scope"),
            )
        except Exception as e:
            logger.error(f"Failed to parse term: {e}")
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
