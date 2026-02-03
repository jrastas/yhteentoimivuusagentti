"""Tests for code list tools."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from yhteentoimivuusalusta_mcp.models.schemas import Code, CodeScheme, LocalizedString, Status
from yhteentoimivuusalusta_mcp.tools.codelist import (
    export_codes_csv,
    get_codes,
    search_codelist,
)


@pytest.fixture
def mock_koodistot_client():
    """Create a mock Koodistot client."""
    client = MagicMock()
    client.search_code_schemes = AsyncMock()
    client.get_code_scheme = AsyncMock()
    client.get_codes = AsyncMock()
    return client


@pytest.fixture
def sample_code_scheme():
    """Sample code scheme for testing."""
    return CodeScheme(
        id="RakennuksenKayttotarkoitus",
        registry="rakennustieto",
        uri="https://example.com/scheme",
        label=LocalizedString(fi="Rakennuksen käyttötarkoitus"),
        description=LocalizedString(fi="Rakennusten käyttötarkoitusluokitus"),
        code_count=3,
    )


@pytest.fixture
def sample_codes():
    """Sample codes for testing."""
    return [
        Code(
            code="01",
            uri="https://example.com/code/01",
            label=LocalizedString(fi="Asuinrakennukset", en="Residential buildings"),
            definition=LocalizedString(fi="Rakennukset asuinkäytössä"),
            status=Status.VALID,
            order=1,
        ),
        Code(
            code="011",
            uri="https://example.com/code/011",
            label=LocalizedString(fi="Yhden asunnon talot", en="Detached houses"),
            status=Status.VALID,
            broader_code="01",
            order=2,
        ),
    ]


@pytest.mark.asyncio
async def test_search_codelist(mock_koodistot_client, sample_code_scheme):
    """Test code list search."""
    mock_koodistot_client.search_code_schemes.return_value = [sample_code_scheme]

    result = await search_codelist(
        client=mock_koodistot_client,
        query="käyttötarkoitus",
        registry="rakennustieto",
    )

    assert result["query"] == "käyttötarkoitus"
    assert result["result_count"] == 1
    assert result["results"][0]["id"] == "RakennuksenKayttotarkoitus"


@pytest.mark.asyncio
async def test_get_codes(mock_koodistot_client, sample_code_scheme, sample_codes):
    """Test getting codes from a scheme."""
    mock_koodistot_client.get_code_scheme.return_value = sample_code_scheme
    mock_koodistot_client.get_codes.return_value = sample_codes

    result = await get_codes(
        client=mock_koodistot_client,
        registry="rakennustieto",
        scheme="RakennuksenKayttotarkoitus",
    )

    assert result["registry"] == "rakennustieto"
    assert result["scheme"] == "RakennuksenKayttotarkoitus"
    assert result["code_count"] == 2
    assert result["codes"][0]["code"] == "01"


@pytest.mark.asyncio
async def test_get_codes_not_found(mock_koodistot_client):
    """Test getting codes when scheme not found."""
    mock_koodistot_client.get_code_scheme.return_value = None

    result = await get_codes(
        client=mock_koodistot_client,
        registry="nonexistent",
        scheme="nonexistent",
    )

    assert "error" in result


@pytest.mark.asyncio
async def test_export_codes_csv(mock_koodistot_client, sample_code_scheme, sample_codes):
    """Test CSV export of codes."""
    mock_koodistot_client.get_code_scheme.return_value = sample_code_scheme
    mock_koodistot_client.get_codes.return_value = sample_codes

    result = await export_codes_csv(
        client=mock_koodistot_client,
        registry="rakennustieto",
        scheme="RakennuksenKayttotarkoitus",
        include_header=True,
    )

    assert result["format"] == "csv"
    assert result["code_count"] == 2
    assert "csv_content" in result

    # Check CSV content
    csv_content = result["csv_content"]
    assert "CODEVALUE" in csv_content  # Header
    assert "01" in csv_content  # First code
    assert "011" in csv_content  # Second code
    assert "Asuinrakennukset" in csv_content


@pytest.mark.asyncio
async def test_export_codes_csv_no_header(mock_koodistot_client, sample_code_scheme, sample_codes):
    """Test CSV export without header."""
    mock_koodistot_client.get_code_scheme.return_value = sample_code_scheme
    mock_koodistot_client.get_codes.return_value = sample_codes

    result = await export_codes_csv(
        client=mock_koodistot_client,
        registry="rakennustieto",
        scheme="RakennuksenKayttotarkoitus",
        include_header=False,
    )

    csv_content = result["csv_content"]
    assert "CODEVALUE" not in csv_content  # No header
    assert "01" in csv_content  # First code


@pytest.mark.asyncio
async def test_export_codes_csv_not_found(mock_koodistot_client):
    """Test CSV export when scheme not found."""
    mock_koodistot_client.get_code_scheme.return_value = None

    result = await export_codes_csv(
        client=mock_koodistot_client,
        registry="nonexistent",
        scheme="nonexistent",
    )

    assert "error" in result
