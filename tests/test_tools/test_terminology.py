"""Tests for terminology tools."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from yhteentoimivuusalusta_mcp.models.schemas import Concept, LocalizedString, Status, Vocabulary
from yhteentoimivuusalusta_mcp.tools.terminology import (
    get_concept_details,
    list_vocabularies,
    search_terminology,
)


@pytest.fixture
def mock_sanastot_client():
    """Create a mock Sanastot client."""
    client = MagicMock()
    client.search_concepts = AsyncMock()
    client.get_concept = AsyncMock()
    client.list_vocabularies = AsyncMock()
    return client


@pytest.mark.asyncio
async def test_search_terminology(mock_sanastot_client):
    """Test search_terminology tool."""
    mock_sanastot_client.search_concepts.return_value = [
        Concept(
            id="concept-1",
            uri="https://example.com/concept-1",
            vocabulary_id="rakymp",
            preferred_label=LocalizedString(fi="rakennus", en="building"),
            definition=LocalizedString(fi="Pysyvä rakennelma"),
            status=Status.VALID,
        )
    ]

    result = await search_terminology(
        client=mock_sanastot_client,
        query="rakennus",
        vocabulary_id="rakymp",
        language="fi",
        max_results=10,
    )

    assert result["query"] == "rakennus"
    assert result["vocabulary_id"] == "rakymp"
    assert result["result_count"] == 1
    assert len(result["results"]) == 1
    assert result["results"][0]["preferred_label"] == "rakennus"
    assert result["results"][0]["definition"] == "Pysyvä rakennelma"


@pytest.mark.asyncio
async def test_get_concept_details(mock_sanastot_client):
    """Test get_concept_details tool."""
    mock_sanastot_client.get_concept.return_value = Concept(
        id="concept-1",
        uri="https://example.com/concept-1",
        vocabulary_id="rakymp",
        preferred_label=LocalizedString(fi="rakennus", en="building"),
        definition=LocalizedString(fi="Pysyvä rakennelma", en="Permanent structure"),
        status=Status.VALID,
        broader=["concept-parent"],
        narrower=["concept-child"],
    )

    result = await get_concept_details(
        client=mock_sanastot_client,
        vocabulary_id="rakymp",
        concept_id="concept-1",
        include_relations=True,
    )

    assert result["id"] == "concept-1"
    assert result["vocabulary_id"] == "rakymp"
    assert result["labels"]["fi"] == "rakennus"
    assert result["labels"]["en"] == "building"
    assert result["definitions"]["fi"] == "Pysyvä rakennelma"
    assert "relations" in result
    assert result["relations"]["broader"] == ["concept-parent"]


@pytest.mark.asyncio
async def test_get_concept_details_not_found(mock_sanastot_client):
    """Test get_concept_details when concept not found."""
    mock_sanastot_client.get_concept.return_value = None

    result = await get_concept_details(
        client=mock_sanastot_client,
        vocabulary_id="rakymp",
        concept_id="nonexistent",
    )

    assert "error" in result
    assert "not found" in result["error"].lower()


@pytest.mark.asyncio
async def test_list_vocabularies(mock_sanastot_client):
    """Test list_vocabularies tool."""
    mock_sanastot_client.list_vocabularies.return_value = [
        Vocabulary(
            id="rakymp",
            uri="https://example.com/rakymp",
            label=LocalizedString(fi="Rakennetun ympäristön sanasto"),
            description=LocalizedString(fi="Kuvaus"),
            domain=["Rakennettu ympäristö"],
            concept_count=500,
            status=Status.VALID,
        )
    ]

    result = await list_vocabularies(
        client=mock_sanastot_client,
        domain="Rakennettu",
    )

    assert result["total_count"] == 1
    assert len(result["vocabularies"]) == 1
    assert result["vocabularies"][0]["id"] == "rakymp"


@pytest.mark.asyncio
async def test_list_vocabularies_with_domain_filter(mock_sanastot_client):
    """Test list_vocabularies with domain filter."""
    mock_sanastot_client.list_vocabularies.return_value = [
        Vocabulary(
            id="rakymp",
            uri="https://example.com/rakymp",
            label=LocalizedString(fi="Rakennetun ympäristön sanasto"),
            domain=["Rakennettu ympäristö"],
            status=Status.VALID,
        ),
        Vocabulary(
            id="oksa",
            uri="https://example.com/oksa",
            label=LocalizedString(fi="Opetussanasto"),
            domain=["Koulutus"],
            status=Status.VALID,
        ),
    ]

    result = await list_vocabularies(
        client=mock_sanastot_client,
        domain="Koulutus",
    )

    assert result["total_count"] == 1
    assert result["vocabularies"][0]["id"] == "oksa"
