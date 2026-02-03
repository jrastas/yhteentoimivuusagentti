"""Tests for Koodistot API client."""

import pytest

from yhteentoimivuusalusta_mcp.clients.koodistot import KoodistotClient
from yhteentoimivuusalusta_mcp.models.schemas import Status


class TestKoodistotClient:
    """Tests for KoodistotClient."""

    def test_parse_code_scheme(self, koodistot_client, codescheme_response):
        """Test code scheme parsing."""
        scheme_data = codescheme_response["results"][0]
        scheme = koodistot_client._parse_code_scheme(scheme_data)

        assert scheme is not None
        assert scheme.id == "RakennuksenKayttotarkoitus"
        assert scheme.registry == "rakennustieto"
        assert scheme.label.fi == "Rakennuksen käyttötarkoitus"
        assert scheme.code_count == 50

    def test_parse_code(self, koodistot_client, codes_response):
        """Test code parsing."""
        code_data = codes_response["results"][0]
        code = koodistot_client._parse_code(code_data)

        assert code is not None
        assert code.code == "011"
        assert code.label.fi == "Yhden asunnon talot"
        assert code.definition.fi == "Asuinrakennukset, joissa on yksi asunto"
        assert code.status == Status.VALID
        assert code.broader_code == "01"
        assert code.order == 1

    def test_parse_code_without_broader(self, koodistot_client):
        """Test parsing code without broader code."""
        code_data = {
            "codeValue": "01",
            "uri": "https://example.com/code/01",
            "prefLabel": {"fi": "Asuinrakennukset"},
            "status": "VALID",
        }
        code = koodistot_client._parse_code(code_data)

        assert code is not None
        assert code.code == "01"
        assert code.broader_code is None

    def test_parse_empty_code_scheme(self, koodistot_client):
        """Test parsing empty/None code scheme data."""
        assert koodistot_client._parse_code_scheme(None) is None
        assert koodistot_client._parse_code_scheme({}) is None

    def test_parse_empty_code(self, koodistot_client):
        """Test parsing empty/None code data."""
        assert koodistot_client._parse_code(None) is None
        assert koodistot_client._parse_code({}) is None
