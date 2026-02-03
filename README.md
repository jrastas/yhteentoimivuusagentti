# Yhteentoimivuusalusta MCP Server

An MCP (Model Context Protocol) server that integrates with Finland's Yhteentoimivuusalusta (Interoperability Platform) to assist with design documentation by ensuring proper use of standardized Finnish terminology, data models, and code values.

## Overview

This tool helps when writing design documents, technical specifications, or architecture descriptions for Finnish government or building industry projects by:

- Suggesting correct standardized terms from relevant vocabularies
- Referencing appropriate data models for data structure descriptions
- Providing valid code list values for enumerations
- Validating terminology consistency across documentation

### Supported Platforms

| Platform | URL | Content |
|----------|-----|---------|
| **Sanastot** | sanastot.suomi.fi | ~90 terminologies and vocabularies |
| **Tietomallit** | tietomallit.suomi.fi | ~170 data models and schemas |
| **Koodistot** | koodistot.suomi.fi | 700+ code lists and classifications |

## Installation

### Prerequisites

- Python 3.11 or higher
- pip or uv package manager

### Install from source

```bash
# Clone the repository
git clone https://github.com/yaskael/yhteentoimivuusagentti.git
cd yhteentoimivuusagentti

# Install in development mode
pip install -e .

# Or with uv
uv pip install -e .
```

### Optional dependencies

```bash
# For improved fuzzy matching
pip install rapidfuzz

# For Finnish NLP (lemmatization)
pip install voikko
```

## Configuration

Copy the example configuration file and adjust as needed:

```bash
cp config.yaml.example config.yaml
```

### Configuration options

```yaml
# config.yaml
cache:
  enabled: true
  directory: ~/.cache/yhteentoimivuusalusta

rate_limit:
  requests_per_second: 10.0

# API endpoints (defaults shown)
apis:
  sanastot:
    base_url: https://sanastot.suomi.fi/terminology-api/api/v1
  tietomallit:
    base_url: https://tietomallit.suomi.fi/datamodel-api/api/v2
  koodistot:
    base_url: https://koodistot.suomi.fi/codelist-api/api/v1
```

## Usage

### Running the server

```bash
python -m yhteentoimivuusalusta_mcp.server
```

### Claude Desktop Integration

Add to your Claude Desktop configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "yhteentoimivuusalusta": {
      "command": "python",
      "args": ["-m", "yhteentoimivuusalusta_mcp.server"],
      "cwd": "/path/to/yhteentoimivuusagentti"
    }
  }
}
```

## Available Tools

The server provides 13 MCP tools across three categories:

### Terminology Tools (Sanastot)

| Tool | Description |
|------|-------------|
| `search_terminology` | Search for terms across vocabularies with fuzzy matching |
| `get_concept_details` | Get detailed information about a specific concept |
| `list_vocabularies` | List all available vocabularies |

### Data Model Tools (Tietomallit)

| Tool | Description |
|------|-------------|
| `search_datamodel` | Search for data models by name or description |
| `get_datamodel_classes` | Get all classes from a specific data model |
| `get_model_vocabulary_links` | Find vocabularies linked to a data model |

### Code List Tools (Koodistot)

| Tool | Description |
|------|-------------|
| `search_codelist` | Search for code lists by name or description |
| `get_codes` | Get all codes from a specific code list |
| `export_codes_csv` | Export codes to CSV format |

### Cross-Platform Tools

| Tool | Description |
|------|-------------|
| `validate_terminology` | Validate text against standardized vocabularies |
| `unified_search` | Search all three platforms simultaneously |
| `suggest_references` | Analyze text and suggest relevant standards to reference |
| `get_codelist_for_attribute` | Find appropriate code lists for data model attributes |

## Examples

### Search for a term

```
Tool: search_terminology
Arguments: { "query": "rakennus", "vocabulary_id": "rakymp" }
```

### Validate terminology in a document

```
Tool: validate_terminology
Arguments: {
  "text": "Rakennuksen kerrosala lasketaan ulkoseinien ulkopintojen mukaan.",
  "vocabulary_ids": ["rakymp"]
}
```

### Unified search across all platforms

```
Tool: unified_search
Arguments: {
  "query": "kaava",
  "platforms": ["sanastot", "tietomallit", "koodistot"],
  "limit": 5
}
```

### Suggest standards for documentation

```
Tool: suggest_references
Arguments: {
  "text": "Järjestelmä käsittelee rakennuslupahakemuksia ja niiden liitteitä.",
  "include_vocabularies": true,
  "include_datamodels": true,
  "include_codelists": true
}
```

## Common Resource IDs

### Vocabularies (Sanastot)

- `rakymp` - Built environment vocabulary (Rakennetun ympäristön sanasto)
- `jhka` - Public administration architecture (Julkisen hallinnon kokonaisarkkitehtuuri)
- `oksa` - Education vocabulary (Opetus- ja koulutussanasto)
- `kela` - Social security vocabulary (Kelan sanasto)

### Data Models (Tietomallit)

- `rytj-kaava` - Spatial planning data model
- `raktkk` - Physical building data model
- `digione` - Education data models

### Code Registries (Koodistot)

- `rakennustieto` - Building information codes
- `koulutus` - Education codes
- `julkishallinto` - Public administration codes

## Features

### Caching

- Persistent disk cache with configurable TTL
- Automatic cache invalidation
- Offline mode support with stale cache fallback

### Performance

- Rate limiting (token bucket algorithm, 10 req/sec default)
- Parallel API requests where possible
- Response caching to minimize API calls

### Reliability

- Automatic retry with exponential backoff
- Graceful degradation when APIs are unavailable
- Offline mode returns cached data when network fails

## Project Structure

```
yhteentoimivuusalusta-mcp/
├── src/
│   └── yhteentoimivuusalusta_mcp/
│       ├── __init__.py
│       ├── server.py              # MCP server entry point
│       ├── tools/
│       │   ├── terminology.py     # Sanastot tools
│       │   ├── datamodel.py       # Tietomallit tools
│       │   ├── codelist.py        # Koodistot tools
│       │   ├── validation.py      # Text validation
│       │   └── unified.py         # Cross-platform tools
│       ├── clients/
│       │   ├── base.py            # Base HTTP client
│       │   ├── sanastot.py        # Sanastot API client
│       │   ├── tietomallit.py     # Tietomallit API client
│       │   └── koodistot.py       # Koodistot API client
│       ├── models/
│       │   └── schemas.py         # Pydantic models
│       └── utils/
│           ├── cache.py           # Caching utilities
│           ├── config.py          # Configuration loader
│           └── fuzzy.py           # Fuzzy matching
├── tests/
├── pyproject.toml
└── config.yaml.example
```

## Development

### Running tests

```bash
pytest tests/
```

### Code formatting

```bash
ruff format src/ tests/
ruff check src/ tests/
```

## License

MIT License

## References

- [Sanastot - Finnish Terminology Service](https://sanastot.suomi.fi/)
- [Tietomallit - Finnish Data Model Service](https://tietomallit.suomi.fi/)
- [Koodistot - Finnish Code List Service](https://koodistot.suomi.fi/)
- [MCP Protocol Documentation](https://modelcontextprotocol.io/)
