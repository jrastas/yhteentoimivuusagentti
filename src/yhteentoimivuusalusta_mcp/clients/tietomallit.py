"""Tietomallit (Data Models) API client."""

import logging
from typing import Any

from yhteentoimivuusalusta_mcp.clients.base import BaseClient
from yhteentoimivuusalusta_mcp.models.schemas import (
    DataModel,
    DataModelAssociation,
    DataModelClass,
    DataModelProperty,
    LocalizedString,
    Status,
)
from yhteentoimivuusalusta_mcp.utils.cache import CacheManager

logger = logging.getLogger(__name__)


class TietomalditClient(BaseClient):
    """Client for the Tietomallit (Data Models) API.

    API Base: https://tietomallit.suomi.fi/datamodel-api/api/v2/
    """

    def __init__(
        self,
        base_url: str = "https://tietomallit.suomi.fi/datamodel-api/api/v2",
        timeout: int = 30,
        retry_count: int = 3,
        cache: CacheManager | None = None,
    ) -> None:
        """Initialize the Tietomallit client."""
        super().__init__(base_url, timeout, retry_count, cache)

    async def search_models(
        self,
        query: str,
        model_type: str | None = None,
        domain: str | None = None,
        max_results: int = 10,
    ) -> list[DataModel]:
        """Search for data models.

        Args:
            query: Search term.
            model_type: Filter by type (PROFILE or LIBRARY).
            domain: Filter by domain.
            max_results: Maximum number of results.

        Returns:
            List of matching data models.
        """
        params: dict[str, Any] = {
            "searchTerm": query,
            "pageSize": max_results,
        }
        if model_type:
            params["type"] = model_type
        if domain:
            params["domain"] = domain

        data = await self.get(
            "/frontend/searchModels",
            params=params,
            cache_prefix="search",
        )

        models = []
        for item in data.get("models", data.get("responseObjects", [])):
            model = self._parse_model(item)
            if model:
                models.append(model)

        return models

    async def get_model(self, model_id: str) -> DataModel | None:
        """Get a specific data model by ID.

        Args:
            model_id: The model identifier (prefix), e.g., 'rytj-kaava'.

        Returns:
            DataModel object or None if not found.
        """
        try:
            data = await self.get(
                f"/frontend/model/{model_id}",
                cache_prefix="data_model",
            )
            return self._parse_model(data)
        except Exception as e:
            logger.error(f"Failed to get model {model_id}: {e}")
            return None

    async def get_model_classes(
        self,
        model_id: str,
        page_size: int = 100,
    ) -> list[DataModelClass]:
        """Get all classes from a data model.

        Args:
            model_id: The model identifier.
            page_size: Number of results per page.

        Returns:
            List of classes in the model.
        """
        params = {"pageSize": page_size}

        data = await self.get(
            f"/frontend/model/{model_id}/classes",
            params=params,
            cache_prefix="classes",
        )

        classes = []
        for item in data.get("classes", data.get("responseObjects", [])):
            cls = self._parse_class(item)
            if cls:
                classes.append(cls)

        return classes

    async def get_class(
        self,
        model_id: str,
        class_id: str,
    ) -> DataModelClass | None:
        """Get a specific class from a data model.

        Args:
            model_id: The model identifier.
            class_id: The class identifier.

        Returns:
            DataModelClass object or None if not found.
        """
        try:
            data = await self.get(
                f"/frontend/model/{model_id}/class/{class_id}",
                cache_prefix="class",
            )
            return self._parse_class(data)
        except Exception as e:
            logger.error(f"Failed to get class {class_id}: {e}")
            return None

    async def list_models(
        self,
        page_size: int = 100,
        page: int = 0,
        model_type: str | None = None,
    ) -> list[DataModel]:
        """List all available data models.

        Args:
            page_size: Number of results per page.
            page: Page number (0-indexed).
            model_type: Filter by type (PROFILE or LIBRARY).

        Returns:
            List of data models.
        """
        params: dict[str, Any] = {
            "pageSize": page_size,
            "pageFrom": page,
        }
        if model_type:
            params["type"] = model_type

        data = await self.get(
            "/frontend/searchModels",
            params=params,
            cache_prefix="data_models",
        )

        models = []
        for item in data.get("models", data.get("responseObjects", [])):
            model = self._parse_model(item)
            if model:
                models.append(model)

        return models

    def _parse_model(self, data: dict[str, Any]) -> DataModel | None:
        """Parse data model from API response."""
        if not data:
            return None

        try:
            label = self._parse_localized(data.get("label", {}))
            description = self._parse_localized(data.get("description", {}))

            return DataModel(
                id=data.get("prefix", data.get("id", "")),
                uri=data.get("uri", ""),
                type=data.get("type", "PROFILE"),
                status=self._parse_status(data.get("status", "VALID")),
                label=label,
                description=description,
                domain=data.get("informationDomains", data.get("groups", [])),
                version=data.get("version"),
                classes=[],  # Classes loaded separately
            )
        except Exception as e:
            logger.error(f"Failed to parse model: {e}")
            return None

    def _parse_class(self, data: dict[str, Any]) -> DataModelClass | None:
        """Parse data model class from API response."""
        if not data:
            return None

        try:
            label = self._parse_localized(data.get("label", {}))
            description = self._parse_localized(data.get("description", {}))

            # Parse properties
            properties = []
            for prop_data in data.get("attributes", data.get("properties", [])):
                prop = self._parse_property(prop_data)
                if prop:
                    properties.append(prop)

            # Parse associations
            associations = []
            for assoc_data in data.get("associations", []):
                assoc = self._parse_association(assoc_data)
                if assoc:
                    associations.append(assoc)

            return DataModelClass(
                id=data.get("identifier", data.get("id", "")),
                uri=data.get("uri", ""),
                label=label,
                description=description,
                is_abstract=data.get("abstract", False),
                parent_class=data.get("subClassOf"),
                properties=properties,
                associations=associations,
                vocabulary_references=data.get("subject", []),
            )
        except Exception as e:
            logger.error(f"Failed to parse class: {e}")
            return None

    def _parse_property(self, data: dict[str, Any]) -> DataModelProperty | None:
        """Parse property from API response."""
        if not data:
            return None

        try:
            label = self._parse_localized(data.get("label", {}))
            description = self._parse_localized(data.get("description", {}))

            return DataModelProperty(
                id=data.get("identifier", data.get("id", "")),
                label=label,
                description=description,
                data_type=data.get("dataType", data.get("range")),
                min_count=data.get("minCount", 0),
                max_count=data.get("maxCount"),
                vocabulary_reference=data.get("subject"),
            )
        except Exception as e:
            logger.error(f"Failed to parse property: {e}")
            return None

    def _parse_association(self, data: dict[str, Any]) -> DataModelAssociation | None:
        """Parse association from API response."""
        if not data:
            return None

        try:
            label = self._parse_localized(data.get("label", {}))

            return DataModelAssociation(
                id=data.get("identifier", data.get("id", "")),
                label=label,
                target_class=data.get("range", data.get("targetClass", "")),
                min_count=data.get("minCount", 0),
                max_count=data.get("maxCount"),
            )
        except Exception as e:
            logger.error(f"Failed to parse association: {e}")
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
