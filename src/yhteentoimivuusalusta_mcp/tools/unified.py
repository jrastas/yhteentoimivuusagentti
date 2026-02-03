"""Unified cross-platform search tools."""

import asyncio
from typing import Any

from yhteentoimivuusalusta_mcp.clients.koodistot import KoodistotClient
from yhteentoimivuusalusta_mcp.clients.sanastot import SanastotClient
from yhteentoimivuusalusta_mcp.clients.tietomallit import TietomalditClient
from yhteentoimivuusalusta_mcp.models.schemas import Language


async def unified_search(
    sanastot_client: SanastotClient,
    tietomallit_client: TietomalditClient,
    koodistot_client: KoodistotClient,
    query: str,
    search_terminologies: bool = True,
    search_datamodels: bool = True,
    search_codelists: bool = True,
    max_results_per_platform: int = 5,
) -> dict[str, Any]:
    """Search across all Yhteentoimivuusalusta platforms simultaneously.

    Performs parallel searches across Sanastot, Tietomallit, and Koodistot
    to find all relevant standards for a given query.

    Args:
        sanastot_client: Sanastot API client.
        tietomallit_client: Tietomallit API client.
        koodistot_client: Koodistot API client.
        query: Search term.
        search_terminologies: Include terminology search.
        search_datamodels: Include data model search.
        search_codelists: Include code list search.
        max_results_per_platform: Maximum results per platform.

    Returns:
        Dictionary with combined search results from all platforms.
    """
    tasks = []

    # Create search tasks for enabled platforms
    if search_terminologies:
        tasks.append(("terminologies", _search_terminologies(
            sanastot_client, query, max_results_per_platform
        )))

    if search_datamodels:
        tasks.append(("datamodels", _search_datamodels(
            tietomallit_client, query, max_results_per_platform
        )))

    if search_codelists:
        tasks.append(("codelists", _search_codelists(
            koodistot_client, query, max_results_per_platform
        )))

    # Execute all searches in parallel
    results = {}
    if tasks:
        task_names = [t[0] for t in tasks]
        task_coros = [t[1] for t in tasks]
        task_results = await asyncio.gather(*task_coros, return_exceptions=True)

        for name, result in zip(task_names, task_results):
            if isinstance(result, Exception):
                results[name] = {"error": str(result), "results": []}
            else:
                results[name] = result

    # Calculate totals
    total_results = sum(
        len(r.get("results", []))
        for r in results.values()
        if isinstance(r, dict)
    )

    return {
        "query": query,
        "total_results": total_results,
        "platforms_searched": list(results.keys()),
        **results,
    }


async def _search_terminologies(
    client: SanastotClient,
    query: str,
    max_results: int,
) -> dict[str, Any]:
    """Search terminologies."""
    concepts = await client.search_concepts(
        query=query,
        max_results=max_results,
    )

    return {
        "platform": "sanastot.suomi.fi",
        "result_count": len(concepts),
        "results": [
            {
                "type": "concept",
                "id": c.id,
                "vocabulary_id": c.vocabulary_id,
                "label": c.preferred_label.get(Language.FI),
                "definition": c.definition.get(Language.FI) if c.definition else None,
                "uri": str(c.uri),
            }
            for c in concepts
        ],
    }


async def _search_datamodels(
    client: TietomalditClient,
    query: str,
    max_results: int,
) -> dict[str, Any]:
    """Search data models."""
    models = await client.search_models(
        query=query,
        max_results=max_results,
    )

    return {
        "platform": "tietomallit.suomi.fi",
        "result_count": len(models),
        "results": [
            {
                "type": "datamodel",
                "id": m.id,
                "model_type": m.type,
                "label": m.label.get(Language.FI),
                "description": m.description.get(Language.FI) if m.description else None,
                "uri": str(m.uri),
            }
            for m in models
        ],
    }


async def _search_codelists(
    client: KoodistotClient,
    query: str,
    max_results: int,
) -> dict[str, Any]:
    """Search code lists."""
    schemes = await client.search_code_schemes(
        query=query,
        max_results=max_results,
    )

    return {
        "platform": "koodistot.suomi.fi",
        "result_count": len(schemes),
        "results": [
            {
                "type": "codelist",
                "id": s.id,
                "registry": s.registry,
                "label": s.label.get(Language.FI),
                "description": s.description.get(Language.FI) if s.description else None,
                "uri": str(s.uri),
                "code_count": s.code_count,
            }
            for s in schemes
        ],
    }


async def suggest_references(
    sanastot_client: SanastotClient,
    tietomallit_client: TietomalditClient,
    koodistot_client: KoodistotClient,
    text: str,
    max_suggestions: int = 10,
) -> dict[str, Any]:
    """Suggest relevant standards references for a text.

    Analyzes text to extract key terms and suggests relevant
    vocabularies, data models, and code lists to reference.

    Args:
        sanastot_client: Sanastot API client.
        tietomallit_client: Tietomallit API client.
        koodistot_client: Koodistot API client.
        text: Input text (e.g., design document excerpt).
        max_suggestions: Maximum suggestions per category.

    Returns:
        Dictionary with suggested references.
    """
    # Extract key terms from text (simple extraction)
    words = text.lower().split()
    # Filter to longer words that might be domain terms
    key_terms = list(set(w.strip(".,;:!?()[]{}") for w in words if len(w) >= 5))[:10]

    # Search for each term across platforms
    all_terminology_results = []
    all_datamodel_results = []
    all_codelist_results = []

    for term in key_terms:
        # Search terminologies
        concepts = await sanastot_client.search_concepts(query=term, max_results=3)
        for c in concepts:
            if c.id not in [r["id"] for r in all_terminology_results]:
                all_terminology_results.append({
                    "id": c.id,
                    "vocabulary_id": c.vocabulary_id,
                    "label": c.preferred_label.get(Language.FI),
                    "matched_term": term,
                    "uri": str(c.uri),
                })

        # Search data models
        models = await tietomallit_client.search_models(query=term, max_results=2)
        for m in models:
            if m.id not in [r["id"] for r in all_datamodel_results]:
                all_datamodel_results.append({
                    "id": m.id,
                    "label": m.label.get(Language.FI),
                    "matched_term": term,
                    "uri": str(m.uri),
                })

        # Search code lists
        schemes = await koodistot_client.search_code_schemes(query=term, max_results=2)
        for s in schemes:
            if s.id not in [r["id"] for r in all_codelist_results]:
                all_codelist_results.append({
                    "id": s.id,
                    "registry": s.registry,
                    "label": s.label.get(Language.FI),
                    "matched_term": term,
                    "uri": str(s.uri),
                })

    return {
        "text_length": len(text),
        "key_terms_extracted": key_terms,
        "suggested_vocabularies": all_terminology_results[:max_suggestions],
        "suggested_datamodels": all_datamodel_results[:max_suggestions],
        "suggested_codelists": all_codelist_results[:max_suggestions],
        "total_suggestions": (
            len(all_terminology_results[:max_suggestions]) +
            len(all_datamodel_results[:max_suggestions]) +
            len(all_codelist_results[:max_suggestions])
        ),
    }


async def get_codelist_for_attribute(
    tietomallit_client: TietomalditClient,
    koodistot_client: KoodistotClient,
    model_id: str,
    class_name: str | None = None,
) -> dict[str, Any]:
    """Find code lists that could be used for data model attributes.

    Examines data model classes and their properties to find
    attributes that might use code lists (enumerations).

    Args:
        tietomallit_client: Tietomallit API client.
        koodistot_client: Koodistot API client.
        model_id: The data model identifier.
        class_name: Optional filter to specific class.

    Returns:
        Dictionary with attribute-to-codelist mappings.
    """
    # Get model classes
    model = await tietomallit_client.get_model(model_id)
    if not model:
        return {
            "error": f"Model not found: {model_id}",
            "model_id": model_id,
        }

    classes = await tietomallit_client.get_model_classes(model_id)

    # Filter by class name if specified
    if class_name:
        classes = [
            c for c in classes
            if class_name.lower() in (c.label.fi or "").lower()
            or class_name.lower() in c.id.lower()
        ]

    # Find attributes that might need code lists
    attribute_suggestions = []

    for cls in classes:
        for prop in cls.properties:
            # Look for properties that might be enumerations
            prop_label = prop.label.get(Language.FI) or prop.id
            prop_name = prop_label.lower()

            # Search for related code lists
            schemes = await koodistot_client.search_code_schemes(
                query=prop_name,
                max_results=3,
            )

            if schemes:
                attribute_suggestions.append({
                    "class_id": cls.id,
                    "class_label": cls.label.get(Language.FI),
                    "attribute_id": prop.id,
                    "attribute_label": prop_label,
                    "data_type": prop.data_type,
                    "suggested_codelists": [
                        {
                            "id": s.id,
                            "registry": s.registry,
                            "label": s.label.get(Language.FI),
                            "code_count": s.code_count,
                            "uri": str(s.uri),
                        }
                        for s in schemes
                    ],
                })

    return {
        "model_id": model_id,
        "model_label": model.label.get(Language.FI),
        "class_filter": class_name,
        "suggestions_count": len(attribute_suggestions),
        "attribute_codelist_suggestions": attribute_suggestions,
    }
