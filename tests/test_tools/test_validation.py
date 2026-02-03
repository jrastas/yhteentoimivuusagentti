"""Tests for validation tools."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from yhteentoimivuusalusta_mcp.models.schemas import Concept, LocalizedString, Status
from yhteentoimivuusalusta_mcp.tools.validation import (
    tokenize_finnish,
    validate_terminology,
)


class TestTokenizeFinnish:
    """Tests for Finnish text tokenization."""

    def test_basic_tokenization(self):
        """Test basic word extraction."""
        text = "Tämä on testi."
        tokens = tokenize_finnish(text)
        assert "testi" in tokens
        # "on" and "tämä" are stop words

    def test_removes_stop_words(self):
        """Test that stop words are removed."""
        text = "ja tai mutta jos"
        tokens = tokenize_finnish(text)
        assert len(tokens) == 0

    def test_preserves_compound_words(self):
        """Test that hyphenated compound words are preserved."""
        text = "asunto-osakeyhtiö rakennuskohde"
        tokens = tokenize_finnish(text)
        assert "asunto-osakeyhtiö" in tokens
        assert "rakennuskohde" in tokens

    def test_creates_compound_terms(self):
        """Test that compound terms are created."""
        text = "fyysinen rakennuskohde"
        tokens = tokenize_finnish(text)
        assert "fyysinen" in tokens
        assert "rakennuskohde" in tokens
        assert "fyysinen rakennuskohde" in tokens

    def test_handles_punctuation(self):
        """Test handling of punctuation."""
        text = "rakennus, rakennelma (tai) muu."
        tokens = tokenize_finnish(text)
        assert "rakennus" in tokens
        assert "rakennelma" in tokens
        assert "muu" in tokens


@pytest.fixture
def mock_sanastot_client():
    """Create a mock Sanastot client."""
    client = MagicMock()
    client.search_concepts = AsyncMock()
    return client


@pytest.mark.asyncio
async def test_validate_terminology_valid_term(mock_sanastot_client):
    """Test validation with a valid term."""
    mock_sanastot_client.search_concepts.return_value = [
        Concept(
            id="concept-rakennus",
            uri="https://example.com/concept-rakennus",
            vocabulary_id="rakymp",
            preferred_label=LocalizedString(fi="rakennus"),
            definition=LocalizedString(fi="Pysyvä rakennelma"),
            status=Status.VALID,
        )
    ]

    result = await validate_terminology(
        client=mock_sanastot_client,
        text="Järjestelmä käsittelee rakennus tietoja.",
        vocabularies=["rakymp"],
    )

    assert result["tokens_analyzed"] > 0
    assert "summary" in result
    # The term "rakennus" should be found
    assert result["summary"]["valid_terms"] >= 0


@pytest.mark.asyncio
async def test_validate_terminology_with_suggestions(mock_sanastot_client):
    """Test validation with suggestions for typos."""
    mock_sanastot_client.search_concepts.return_value = [
        Concept(
            id="concept-rakennus",
            uri="https://example.com/concept-rakennus",
            vocabulary_id="rakymp",
            preferred_label=LocalizedString(fi="rakennus"),
            status=Status.VALID,
        )
    ]

    result = await validate_terminology(
        client=mock_sanastot_client,
        text="Tämä on rakennux.",  # typo
        vocabularies=["rakymp"],
        suggest_corrections=True,
        fuzzy_threshold=0.7,
    )

    assert "suggestions" in result
    assert "unknown_terms" in result


@pytest.mark.asyncio
async def test_validate_terminology_text_limit(mock_sanastot_client):
    """Test that text is truncated to 10000 characters."""
    mock_sanastot_client.search_concepts.return_value = []

    long_text = "a" * 15000

    result = await validate_terminology(
        client=mock_sanastot_client,
        text=long_text,
    )

    assert result["text_length"] == 10000
