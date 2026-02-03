"""Pytest fixtures for tests."""

import pytest

from yhteentoimivuusalusta_mcp.clients.koodistot import KoodistotClient
from yhteentoimivuusalusta_mcp.clients.sanastot import SanastotClient
from yhteentoimivuusalusta_mcp.clients.tietomallit import TietomalditClient
from yhteentoimivuusalusta_mcp.utils.cache import CacheManager


@pytest.fixture
def cache_manager():
    """Create a disabled cache manager for testing."""
    return CacheManager(enabled=False)


@pytest.fixture
def sanastot_client(cache_manager):
    """Create a Sanastot client for testing."""
    return SanastotClient(cache=cache_manager)


@pytest.fixture
def tietomallit_client(cache_manager):
    """Create a Tietomallit client for testing."""
    return TietomalditClient(cache=cache_manager)


@pytest.fixture
def koodistot_client(cache_manager):
    """Create a Koodistot client for testing."""
    return KoodistotClient(cache=cache_manager)


# Sample API response fixtures
@pytest.fixture
def vocabulary_response():
    """Sample vocabulary API response."""
    return {
        "terminologies": [
            {
                "prefix": "rakymp",
                "uri": "https://sanastot.suomi.fi/terminology/rakymp",
                "label": {"fi": "Rakennetun ympäristön sanasto", "en": "Built environment vocabulary"},
                "description": {"fi": "Rakennetun ympäristön käsitteitä"},
                "status": "VALID",
                "conceptCount": 500,
                "languages": ["fi", "en", "sv"],
                "informationDomains": ["Rakennettu ympäristö"],
                "organizations": [{"label": {"fi": "DVV"}}],
            }
        ]
    }


@pytest.fixture
def concept_response():
    """Sample concept API response."""
    return {
        "concepts": [
            {
                "id": "concept-123",
                "uri": "https://sanastot.suomi.fi/terminology/rakymp/concept-123",
                "label": {"fi": "rakennus", "en": "building"},
                "definition": {"fi": "Pysyvä rakennelma"},
                "terminology": {"prefix": "rakymp"},
                "status": "VALID",
                "broader": [],
                "narrower": ["concept-124"],
                "related": [],
            }
        ]
    }


@pytest.fixture
def datamodel_response():
    """Sample data model API response."""
    return {
        "responseObjects": [
            {
                "prefix": "rytj-kaava",
                "uri": "https://tietomallit.suomi.fi/model/rytj-kaava",
                "label": {"fi": "Kaavatietomalli"},
                "description": {"fi": "Maankäytön suunnittelun tietomalli"},
                "type": "PROFILE",
                "status": "VALID",
                "informationDomains": ["Rakennettu ympäristö"],
            }
        ]
    }


@pytest.fixture
def codescheme_response():
    """Sample code scheme API response."""
    return {
        "results": [
            {
                "codeValue": "RakennuksenKayttotarkoitus",
                "uri": "https://koodistot.suomi.fi/codelist/rakennustieto/RakennuksenKayttotarkoitus",
                "prefLabel": {"fi": "Rakennuksen käyttötarkoitus"},
                "description": {"fi": "Rakennusten käyttötarkoitusluokitus"},
                "codeRegistry": {"codeValue": "rakennustieto"},
                "codeCount": 50,
            }
        ]
    }


@pytest.fixture
def codes_response():
    """Sample codes API response."""
    return {
        "results": [
            {
                "codeValue": "011",
                "uri": "https://koodistot.suomi.fi/code/rakennustieto/011",
                "prefLabel": {"fi": "Yhden asunnon talot"},
                "definition": {"fi": "Asuinrakennukset, joissa on yksi asunto"},
                "status": "VALID",
                "broaderCode": {"codeValue": "01"},
                "order": 1,
            },
            {
                "codeValue": "012",
                "uri": "https://koodistot.suomi.fi/code/rakennustieto/012",
                "prefLabel": {"fi": "Kahden asunnon talot"},
                "definition": {"fi": "Asuinrakennukset, joissa on kaksi asuntoa"},
                "status": "VALID",
                "broaderCode": {"codeValue": "01"},
                "order": 2,
            },
        ]
    }
