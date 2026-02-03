"""Terminology tools for Sanastot API."""

from yhteentoimivuusalusta_mcp.clients.sanastot import SanastotClient
from yhteentoimivuusalusta_mcp.models.schemas import Language


async def search_terminology(
    client: SanastotClient,
    query: str,
    vocabulary_id: str | None = None,
    language: str = "fi",
    max_results: int = 10,
) -> dict:
    """Search for standardized terms across vocabularies.

    Args:
        client: Sanastot API client.
        query: Search term in Finnish or English.
        vocabulary_id: Optional vocabulary ID to limit search (e.g., 'rakymp').
        language: Search language (fi, en, sv).
        max_results: Maximum results to return.

    Returns:
        Dictionary with search results.
    """
    concepts = await client.search_concepts(
        query=query,
        vocabulary_id=vocabulary_id,
        language=language,
        max_results=max_results,
    )

    results = []
    for concept in concepts:
        lang = Language(language) if language in ["fi", "en", "sv"] else Language.FI
        results.append({
            "id": concept.id,
            "vocabulary_id": concept.vocabulary_id,
            "preferred_label": concept.preferred_label.get(lang),
            "definition": concept.definition.get(lang) if concept.definition else None,
            "uri": str(concept.uri),
            "status": concept.status.value,
            "broader": concept.broader[:3] if concept.broader else [],
            "narrower": concept.narrower[:3] if concept.narrower else [],
            "related": concept.related[:3] if concept.related else [],
        })

    return {
        "query": query,
        "vocabulary_id": vocabulary_id,
        "language": language,
        "result_count": len(results),
        "results": results,
    }


async def get_concept_details(
    client: SanastotClient,
    vocabulary_id: str,
    concept_id: str,
    include_relations: bool = True,
) -> dict:
    """Get detailed information about a concept.

    Args:
        client: Sanastot API client.
        vocabulary_id: The vocabulary containing the concept.
        concept_id: The concept identifier.
        include_relations: Include broader/narrower/related concepts.

    Returns:
        Dictionary with concept details.
    """
    concept = await client.get_concept(vocabulary_id, concept_id)

    if not concept:
        return {
            "error": f"Concept not found: {vocabulary_id}/{concept_id}",
            "vocabulary_id": vocabulary_id,
            "concept_id": concept_id,
        }

    result = {
        "id": concept.id,
        "vocabulary_id": concept.vocabulary_id,
        "uri": str(concept.uri),
        "status": concept.status.value,
        "labels": {
            "fi": concept.preferred_label.fi,
            "en": concept.preferred_label.en,
            "sv": concept.preferred_label.sv,
        },
        "definitions": {
            "fi": concept.definition.fi if concept.definition else None,
            "en": concept.definition.en if concept.definition else None,
            "sv": concept.definition.sv if concept.definition else None,
        },
        "terms": [
            {
                "label": term.label,
                "language": term.language.value,
                "status": term.status,
            }
            for term in concept.terms
        ],
    }

    if include_relations:
        result["relations"] = {
            "broader": concept.broader,
            "narrower": concept.narrower,
            "related": concept.related,
        }

    return result


async def list_vocabularies(
    client: SanastotClient,
    domain: str | None = None,
    status: str | None = None,
) -> dict:
    """List available vocabularies.

    Args:
        client: Sanastot API client.
        domain: Filter by domain (e.g., 'Rakennettu ympäristö').
        status: Filter by status (VALID, DRAFT, INCOMPLETE).

    Returns:
        Dictionary with vocabulary list.
    """
    vocabularies = await client.list_vocabularies(status=status)

    results = []
    for vocab in vocabularies:
        # Filter by domain if specified
        if domain:
            if not any(domain.lower() in d.lower() for d in vocab.domain):
                continue

        results.append({
            "id": vocab.id,
            "label": vocab.label.get(Language.FI),
            "description": vocab.description.get(Language.FI) if vocab.description else None,
            "uri": str(vocab.uri),
            "status": vocab.status.value,
            "concept_count": vocab.concept_count,
            "domains": vocab.domain,
            "organization": vocab.organization,
            "languages": [lang.value for lang in vocab.languages],
        })

    return {
        "domain_filter": domain,
        "status_filter": status,
        "total_count": len(results),
        "vocabularies": results,
    }
