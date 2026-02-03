# Yhteentoimivuusalusta MCP Server

## Project Overview

This project creates an MCP (Model Context Protocol) server that integrates with Finland's Yhteentoimivuusalusta (Interoperability Platform) to assist with design documentation by ensuring proper use of standardized Finnish terminology, data models, and code values.

### Platform Components

- **Sanastot** (sanastot.suomi.fi) - Terminologies and vocabularies (~90 vocabularies)
- **Tietomallit** (tietomallit.suomi.fi) - Data models and schemas (~170 models)
- **Koodistot** (koodistot.suomi.fi) - Code lists and classifications (700+ code lists)

### Primary Use Case

When writing design documents, technical specifications, or architecture descriptions for Finnish government or building industry projects, the tool will:
- Suggest correct standardized terms from relevant vocabularies
- Reference appropriate data models for data structure descriptions
- Provide valid code list values for enumerations
- Validate terminology consistency across documentation

## Technology Stack

- **Language:** Python 3.11+
- **MCP Library:** `mcp` Python package (Anthropic official SDK)
- **HTTP Client:** `httpx` (async support)
- **Caching:** `diskcache` (local) or Redis (shared)
- **Data Models:** `pydantic` for validation
- **Optional:** `voikko` (Finnish NLP), `rapidfuzz` (fuzzy matching), `openpyxl` (Excel), `rdflib` (RDF/OWL)

## Project Structure

```
yhteentoimivuusalusta-mcp/
├── src/
│   └── yhteentoimivuusalusta_mcp/
│       ├── __init__.py
│       ├── server.py              # MCP server entry point
│       ├── tools/
│       │   ├── terminology.py     # search_terminology, get_concept_details, list_vocabularies
│       │   ├── datamodel.py       # search_datamodel, get_datamodel_classes, get_model_vocabulary_links
│       │   ├── codelist.py        # search_codelist, get_codes, export_codes_csv
│       │   ├── validation.py      # validate_terminology
│       │   └── unified.py         # unified_search, suggest_references, get_codelist_for_attribute
│       ├── clients/
│       │   ├── base.py            # Base HTTP client with rate limiting and offline mode
│       │   ├── sanastot.py        # Sanastot API client
│       │   ├── tietomallit.py     # Tietomallit API client
│       │   └── koodistot.py       # Koodistot API client
│       ├── models/
│       │   └── schemas.py         # Pydantic models
│       └── utils/
│           ├── cache.py           # Caching utilities with offline mode support
│           ├── config.py          # Configuration loader
│           ├── fuzzy.py           # Fuzzy matching utilities
│           └── nlp.py             # Finnish NLP utilities (optional)
├── tests/
├── docs/
├── pyproject.toml
└── config.yaml.example
```

## MCP Tools (13 total)

| Tool | Platform | Purpose |
|------|----------|---------|
| `search_terminology` | Sanastot | Search for terms across vocabularies |
| `get_concept_details` | Sanastot | Get detailed concept information |
| `list_vocabularies` | Sanastot | List available vocabularies |
| `search_datamodel` | Tietomallit | Search for data models |
| `get_datamodel_classes` | Tietomallit | Get classes from a model |
| `get_model_vocabulary_links` | Tietomallit | Link models to vocabularies |
| `search_codelist` | Koodistot | Search for code lists |
| `get_codes` | Koodistot | Get codes from a code list |
| `export_codes_csv` | Koodistot | Export codes to CSV format |
| `validate_terminology` | Cross-platform | Validate text against standards |
| `unified_search` | Cross-platform | Search all platforms simultaneously |
| `suggest_references` | Cross-platform | Suggest standards for text |
| `get_codelist_for_attribute` | Cross-platform | Find code lists for data model attributes |

## API Endpoints

### Sanastot API
- Base URL: `https://sanastot.suomi.fi/terminology-api/api/v1/`
- Key endpoints: `/frontend/terminologies`, `/frontend/searchConcept`, `/export/{id}`

### Tietomallit API
- Base URL: `https://tietomallit.suomi.fi/datamodel-api/api/v2/`
- Key endpoints: `/frontend/searchModels`, `/frontend/model/{prefix}`, `/frontend/model/{prefix}/classes`

### Koodistot API
- Base URL: `https://koodistot.suomi.fi/codelist-api/api/v1/`
- Key endpoints: `/coderegistries`, `/coderegistries/{registry}/codeschemes/{scheme}/codes`

## Common Resource IDs

### Vocabularies (Sanastot)
- `rakymp` - Built environment vocabulary
- `jhka` - Public admin architecture
- `oksa` - Education vocabulary
- `kela` - Social security vocabulary

### Data Models (Tietomallit)
- `rytj-kaava` - Spatial planning data model
- `raktkk` - Physical building data model
- `digione` - Education data models

### Code Registries (Koodistot)
- `rakennustieto` - Building information codes
- `koulutus` - Education codes
- `julkishallinto` - Public administration codes

---

# Development Phases

## Phase 1: Foundation (Week 1-2) - COMPLETED

### Milestone 1.1: API Exploration
- [x] Test all three API endpoints with curl/Postman
- [x] Document response structures
- [x] Identify rate limits and caching needs
- [x] Create example request/response library
- [x] Verify API authentication requirements (none expected)

### Milestone 1.2: MCP Server Setup
- [x] Initialize MCP server project (Python)
- [x] Set up development environment with uv/pip
- [x] Configure basic server structure
- [x] Test MCP connection with Claude Desktop
- [x] Implement stdio transport

### Milestone 1.3: HTTP Clients
- [x] Create Sanastot API client with httpx
- [x] Create Tietomallit API client
- [x] Create Koodistot API client
- [x] Add error handling and retries
- [x] Implement response caching with diskcache

**Deliverables:**
- [x] Working MCP server skeleton
- [x] Three API clients with unit tests
- [x] Development environment documentation

---

## Phase 2: Core Tools (Week 3-4) - COMPLETED

### Milestone 2.1: Terminology Tools
- [x] Implement `search_terminology`
- [x] Implement `get_concept_details`
- [x] Implement `list_vocabularies`
- [x] Add multilingual support (FI/EN/SV)
- [x] Add fuzzy matching for typos

### Milestone 2.2: Data Model Tools
- [x] Implement `search_datamodel`
- [x] Implement `get_datamodel_classes`
- [x] Parse class structures and properties
- [x] Extract relationships and associations
- [x] Link models to vocabularies (`get_model_vocabulary_links`)

### Milestone 2.3: Code List Tools
- [x] Implement `search_codelist`
- [x] Implement `get_codes`
- [x] Support hierarchical code navigation
- [x] Add CSV export capability (`export_codes_csv`)

**Deliverables:**
- [x] Ten working MCP tools (exceeded target of 7!)
- [x] Integration tests for each tool
- [ ] Tool documentation with examples

---

## Phase 3: Advanced Features (Week 5-6) - COMPLETED

### Milestone 3.1: Text Validation
- [x] Implement `validate_terminology`
- [x] Extract Finnish terms from text (tokenization)
- [x] Match against vocabularies
- [x] Generate suggestions for non-standard terms
- [ ] Optionally integrate Voikko for lemmatization

### Milestone 3.2: Cross-Platform Integration
- [x] Link vocabulary concepts to data models
- [x] Link data model attributes to code lists (`get_codelist_for_attribute`)
- [x] Build unified search across platforms (`unified_search`)
- [x] Add "suggest references" functionality (`suggest_references`)

### Milestone 3.3: Caching & Performance
- [x] Implement persistent disk cache
- [x] Add cache invalidation (TTL-based)
- [x] Optimize API calls (batch where possible)
- [x] Add rate limiting protection (token bucket algorithm)
- [x] Implement offline mode with cached data (stale cache fallback)

**Deliverables:**
- [x] Complete tool suite (13 tools - exceeded target!)
- [x] Performance optimizations (rate limiting)
- [x] Offline capability (stale cache fallback)

---

## Phase 4: Testing & Documentation (Week 7-8) - IN PROGRESS

### Milestone 4.1: Real-World Testing
- [ ] Test with IFC Tarkistaja project documentation
- [ ] Test with building permit design docs
- [ ] Test with Finnish government integration specs
- [ ] Collect user feedback
- [ ] Performance benchmarking

### Milestone 4.2: Edge Cases & Error Handling
- [x] Handle missing/deprecated vocabularies (graceful error handling)
- [x] Handle API failures gracefully (retry with backoff)
- [x] Support offline mode (cached data)
- [x] Handle mixed FI/EN text (tokenization supports both)
- [x] Validate all input parameters (validation helpers added)

### Milestone 4.3: Documentation
- [x] Write comprehensive README
- [x] Create INSTALLATION.md
- [x] Create USAGE.md with examples
- [x] Create API_REFERENCE.md
- [x] Create EXAMPLES.md
- [x] Create TROUBLESHOOTING.md
- [x] Create CONTRIBUTING.md
- [x] Create SECURITY.md with security review

**Deliverables:**
- [x] Production-ready MCP server (42 tests passing)
- [x] Core documentation (README, USAGE, API_REFERENCE)
- [x] Complete documentation suite
- [x] Security review and documentation

---

## Phase 5: Future Enhancements (Post-MVP)

### Potential Features
- **Code Generation:** Generate Python/TypeScript classes from data models
- **Documentation Templates:** Pre-filled design document templates
- **CI/CD Integration:** Pre-commit hook for terminology validation
- **IDE Extensions:** VS Code extension with inline suggestions
- **Comparative Analysis:** Compare terminology across documents

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Response Time (cached) | < 500ms |
| Response Time (uncached) | < 3s |
| API Coverage | 100% (all 3 platforms) |
| Cache Hit Rate | > 80% |
| Error Rate | < 1% |

## Getting Started

1. Set up Python 3.11+ environment
2. Install dependencies: `pip install -e .`
3. Copy `config.yaml.example` to `config.yaml`
4. Run server: `python -m yhteentoimivuusalusta_mcp.server`
5. Configure Claude Desktop to use the MCP server

## References

- Project Plan: `yhteentoimivuusalusta-mcp-project-plan-v1.1.md`
- Sanastot: https://sanastot.suomi.fi/
- Tietomallit: https://tietomallit.suomi.fi/
- Koodistot: https://koodistot.suomi.fi/
