"""Tests for Sanastot API client."""

import pytest

from yhteentoimivuusalusta_mcp.clients.sanastot import SanastotClient
from yhteentoimivuusalusta_mcp.models.schemas import Language, Status


class TestSanastotClient:
    """Tests for SanastotClient."""

    def test_parse_vocabulary(self, sanastot_client, vocabulary_response):
        """Test vocabulary parsing."""
        vocab_data = vocabulary_response["terminologies"][0]
        vocab = sanastot_client._parse_vocabulary(vocab_data)

        assert vocab is not None
        assert vocab.id == "rakymp"
        assert vocab.label.fi == "Rakennetun ympäristön sanasto"
        assert vocab.label.en == "Built environment vocabulary"
        assert vocab.status == Status.VALID
        assert vocab.concept_count == 500
        assert "Rakennettu ympäristö" in vocab.domain

    def test_parse_concept(self, sanastot_client, concept_response):
        """Test concept parsing."""
        concept_data = concept_response["concepts"][0]
        concept = sanastot_client._parse_concept(concept_data)

        assert concept is not None
        assert concept.id == "concept-123"
        assert concept.preferred_label.fi == "rakennus"
        assert concept.preferred_label.en == "building"
        assert concept.definition.fi == "Pysyvä rakennelma"
        assert concept.vocabulary_id == "rakymp"
        assert concept.status == Status.VALID

    def test_parse_localized_string(self, sanastot_client):
        """Test localized string parsing."""
        data = {"fi": "suomeksi", "en": "in English", "sv": "på svenska"}
        localized = sanastot_client._parse_localized(data)

        assert localized.fi == "suomeksi"
        assert localized.en == "in English"
        assert localized.sv == "på svenska"
        assert localized.get(Language.FI) == "suomeksi"
        assert localized.get("en") == "in English"

    def test_parse_localized_string_fallback(self, sanastot_client):
        """Test localized string fallback."""
        data = {"fi": "vain suomeksi"}
        localized = sanastot_client._parse_localized(data)

        assert localized.fi == "vain suomeksi"
        assert localized.en is None
        assert localized.get(Language.EN) == "vain suomeksi"  # Falls back to fi

    def test_parse_status(self, sanastot_client):
        """Test status parsing."""
        assert sanastot_client._parse_status("VALID") == Status.VALID
        assert sanastot_client._parse_status("DRAFT") == Status.DRAFT
        assert sanastot_client._parse_status("invalid") == Status.VALID  # Default

    def test_parse_empty_vocabulary(self, sanastot_client):
        """Test parsing empty/None vocabulary data."""
        assert sanastot_client._parse_vocabulary(None) is None
        assert sanastot_client._parse_vocabulary({}) is None

    def test_parse_empty_concept(self, sanastot_client):
        """Test parsing empty/None concept data."""
        assert sanastot_client._parse_concept(None) is None
        assert sanastot_client._parse_concept({}) is None
