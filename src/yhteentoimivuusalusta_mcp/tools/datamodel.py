"""Data model tools for Tietomallit API."""

from yhteentoimivuusalusta_mcp.clients.tietomallit import TietomalditClient
from yhteentoimivuusalusta_mcp.models.schemas import Language


async def search_datamodel(
    client: TietomalditClient,
    query: str,
    model_type: str | None = None,
    domain: str | None = None,
    max_results: int = 10,
) -> dict:
    """Search for data models.

    Args:
        client: Tietomallit API client.
        query: Search term for model name or content.
        model_type: PROFILE (application profile) or LIBRARY (reusable components).
        domain: Filter by domain (e.g., 'Rakennettu ympäristö').
        max_results: Maximum results to return.

    Returns:
        Dictionary with search results.
    """
    models = await client.search_models(
        query=query,
        model_type=model_type,
        domain=domain,
        max_results=max_results,
    )

    results = []
    for model in models:
        results.append({
            "id": model.id,
            "type": model.type,
            "label": model.label.get(Language.FI),
            "description": model.description.get(Language.FI) if model.description else None,
            "uri": str(model.uri),
            "status": model.status.value,
            "version": model.version,
            "domains": model.domain,
        })

    return {
        "query": query,
        "model_type": model_type,
        "domain": domain,
        "result_count": len(results),
        "results": results,
    }


async def get_datamodel_classes(
    client: TietomalditClient,
    model_id: str,
    class_name: str | None = None,
    include_properties: bool = True,
    include_associations: bool = True,
) -> dict:
    """Get classes from a data model.

    Args:
        client: Tietomallit API client.
        model_id: The data model identifier (e.g., 'rytj-kaava').
        class_name: Optional filter to specific class.
        include_properties: Include class properties.
        include_associations: Include class associations.

    Returns:
        Dictionary with class information.
    """
    # Get model info first
    model = await client.get_model(model_id)
    if not model:
        return {
            "error": f"Model not found: {model_id}",
            "model_id": model_id,
        }

    # Get classes
    classes = await client.get_model_classes(model_id)

    # Filter by class name if specified
    if class_name:
        classes = [
            c for c in classes
            if class_name.lower() in (c.label.fi or "").lower()
            or class_name.lower() in c.id.lower()
        ]

    results = []
    for cls in classes:
        class_info = {
            "id": cls.id,
            "label": cls.label.get(Language.FI),
            "description": cls.description.get(Language.FI) if cls.description else None,
            "uri": str(cls.uri),
            "is_abstract": cls.is_abstract,
            "parent_class": cls.parent_class,
        }

        if include_properties:
            class_info["properties"] = [
                {
                    "id": prop.id,
                    "label": prop.label.get(Language.FI),
                    "data_type": prop.data_type,
                    "min_count": prop.min_count,
                    "max_count": prop.max_count,
                    "vocabulary_reference": prop.vocabulary_reference,
                }
                for prop in cls.properties
            ]

        if include_associations:
            class_info["associations"] = [
                {
                    "id": assoc.id,
                    "label": assoc.label.get(Language.FI),
                    "target_class": assoc.target_class,
                    "min_count": assoc.min_count,
                    "max_count": assoc.max_count,
                }
                for assoc in cls.associations
            ]

        results.append(class_info)

    return {
        "model_id": model_id,
        "model_label": model.label.get(Language.FI),
        "model_type": model.type,
        "class_filter": class_name,
        "class_count": len(results),
        "classes": results,
    }
