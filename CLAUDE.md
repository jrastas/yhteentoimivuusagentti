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
│       │   ├── datamodel.py       # search_datamodel, get_datamodel_classes
│       │   ├── codelist.py        # search_codelist, get_codes
│       │   └── validation.py      # validate_terminology
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
│           └── nlp.py             # Finnish NLP utilities (optional)
├── tests/
├── docs/
├── pyproject.toml
└── config.yaml.example
```

## MCP Tools (8 total)

| Tool | Platform | Purpose |
|------|----------|---------|
| `search_terminology` | Sanastot | Search for terms across vocabularies |
| `get_concept_details` | Sanastot | Get detailed concept information |
| `list_vocabularies` | Sanastot | List available vocabularies |
| `search_datamodel` | Tietomallit | Search for data models |
| `get_datamodel_classes` | Tietomallit | Get classes from a model |
| `search_codelist` | Koodistot | Search for code lists |
| `get_codes` | Koodistot | Get codes from a code list |
| `validate_terminology` | Cross-platform | Validate text against standards |

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

## Phase 1: Foundation (Week 1-2)

### Milestone 1.1: API Exploration
- [ ] Test all three API endpoints with curl/Postman
- [ ] Document response structures
- [ ] Identify rate limits and caching needs
- [ ] Create example request/response library
- [ ] Verify API authentication requirements (none expected)

### Milestone 1.2: MCP Server Setup
- [ ] Initialize MCP server project (Python)
- [ ] Set up development environment with uv/pip
- [ ] Configure basic server structure
- [ ] Test MCP connection with Claude Desktop
- [ ] Implement stdio transport

### Milestone 1.3: HTTP Clients
- [ ] Create Sanastot API client with httpx
- [ ] Create Tietomallit API client
- [ ] Create Koodistot API client
- [ ] Add error handling and retries
- [ ] Implement response caching with diskcache

**Deliverables:**
- Working MCP server skeleton
- Three API clients with unit tests
- Development environment documentation

---

## Phase 2: Core Tools (Week 3-4)

### Milestone 2.1: Terminology Tools
- [ ] Implement `search_terminology`
- [ ] Implement `get_concept_details`
- [ ] Implement `list_vocabularies`
- [ ] Add multilingual support (FI/EN/SV)
- [ ] Add fuzzy matching for typos

### Milestone 2.2: Data Model Tools
- [ ] Implement `search_datamodel`
- [ ] Implement `get_datamodel_classes`
- [ ] Parse class structures and properties
- [ ] Extract relationships and associations
- [ ] Link models to vocabularies

### Milestone 2.3: Code List Tools
- [ ] Implement `search_codelist`
- [ ] Implement `get_codes`
- [ ] Support hierarchical code navigation
- [ ] Add CSV export capability

**Deliverables:**
- Seven working MCP tools
- Integration tests for each tool
- Tool documentation with examples

---

## Phase 3: Advanced Features (Week 5-6)

### Milestone 3.1: Text Validation
- [ ] Implement `validate_terminology`
- [ ] Extract Finnish terms from text (tokenization)
- [ ] Match against vocabularies
- [ ] Generate suggestions for non-standard terms
- [ ] Optionally integrate Voikko for lemmatization

### Milestone 3.2: Cross-Platform Integration
- [ ] Link vocabulary concepts to data models
- [ ] Link data model attributes to code lists
- [ ] Build unified search across platforms
- [ ] Add "suggest references" functionality

### Milestone 3.3: Caching & Performance
- [ ] Implement persistent disk cache
- [ ] Add cache invalidation (TTL-based)
- [ ] Optimize API calls (batch where possible)
- [ ] Add rate limiting protection
- [ ] Implement offline mode with cached data

**Deliverables:**
- Complete tool suite (8 tools)
- Performance optimizations
- Offline capability

---

## Phase 4: Testing & Documentation (Week 7-8)

### Milestone 4.1: Real-World Testing
- [ ] Test with IFC Tarkistaja project documentation
- [ ] Test with building permit design docs
- [ ] Test with Finnish government integration specs
- [ ] Collect user feedback
- [ ] Performance benchmarking

### Milestone 4.2: Edge Cases & Error Handling
- [ ] Handle missing/deprecated vocabularies
- [ ] Handle API failures gracefully
- [ ] Support offline mode (cached data)
- [ ] Handle mixed FI/EN text
- [ ] Validate all input parameters

### Milestone 4.3: Documentation
- [ ] Write comprehensive README
- [ ] Create INSTALLATION.md
- [ ] Create USAGE.md with examples
- [ ] Create API_REFERENCE.md
- [ ] Create EXAMPLES.md
- [ ] Create TROUBLESHOOTING.md
- [ ] Create CONTRIBUTING.md

**Deliverables:**
- Production-ready MCP server
- Complete documentation suite
- Example use case demonstrations

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
