# Yhteentoimivuusalusta MCP Tool - Project Plan

**Project Title:** Design Documentation Assistant with Finnish Government Interoperability Platform Integration

**Version:** 1.1  
**Date:** January 29, 2026  
**Author:** Jaakko  
**Status:** Planning Phase

---

## Executive Summary

This project aims to create an MCP (Model Context Protocol) server that integrates with all three components of Finland's Yhteentoimivuusalusta (Interoperability Platform):

- **Sanastot** (sanastot.suomi.fi) - Terminologies and vocabularies
- **Tietomallit** (tietomallit.suomi.fi) - Data models and schemas
- **Koodistot** (koodistot.suomi.fi) - Code lists and classifications

The initial focus is on assisting with **design documentation** by ensuring proper use of standardized Finnish terminology, data models, and code values.

### Primary Use Case

When writing design documents, technical specifications, or architecture descriptions for Finnish government or building industry projects, the tool will:

- Suggest correct standardized terms from relevant vocabularies
- Reference appropriate data models for data structure descriptions
- Provide valid code list values for enumerations
- Validate terminology consistency across documentation

---

## 1. Background & Motivation

### 1.1 Problem Statement

When developing software for Finnish government integrations or building information systems:

1. **Terminology Fragmentation**: Different projects use inconsistent Finnish terms for the same concepts
2. **Manual Reference Lookup**: Developers must manually browse multiple websites to find correct terms
3. **Data Model Discovery**: Finding relevant standardized data models is time-consuming
4. **Code List Management**: Keeping track of valid code values from different domains is difficult
5. **Documentation Quality**: Design documents often lack references to official standards

### 1.2 Current Workflow Pain Points

**Without this tool:**
```
Developer writing design doc → Opens browser → Navigates to sanastot.suomi.fi
→ Searches for term → Copies definition → Returns to document
→ Realizes related data model exists → Opens tietomallit.suomi.fi
→ Searches for model → Downloads PDF → Reads → Returns to document
→ Needs to use code list → Opens koodistot.suomi.fi
→ Finds code list → Exports CSV → References in doc
```

**With this tool:**
```
Developer writing in editor/Claude → Asks MCP tool
→ Gets term definition, related data models, and code lists
→ Continues writing with inline references
```

---

## 2. Platform Overview

### 2.1 Yhteentoimivuusalusta Structure

The Interoperability Platform consists of three interconnected services. Data models reference vocabularies for semantic definitions, and code lists provide valid values used by both:

```
┌──────────────────────────────────────────────────────────┐
│              YHTEENTOIMIVUUSALUSTA                       │
│        (Interoperability Platform - suomi.fi)            │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌───────────────┐  ┌───────────────┐  ┌──────────────┐ │
│  │   SANASTOT    │  │  TIETOMALLIT  │  │  KOODISTOT   │ │
│  │               │  │               │  │              │ │
│  │ Terminologies │──▶│  Data Models  │◀──│ Code Lists   │ │
│  │  & Concepts   │  │   & Schemas   │  │  & Values    │ │
│  │               │  │               │  │              │ │
│  │   ~90 vocabs  │  │  ~170 models  │  │    700+      │ │
│  └───────────────┘  └───────────────┘  └──────────────┘ │
│                                                          │
│  Arrows show semantic references:                        │
│  • Data models reference vocabulary concepts             │
│  • Data models use code lists for enumerations           │
└──────────────────────────────────────────────────────────┘
```

*Note: Numbers are approximate and change as content is added.*

### 2.2 Sanastot (Terminologies)

**URL:** https://sanastot.suomi.fi/  
**Purpose:** Standardized terminology and concept definitions  
**Content:** ~90 vocabularies covering domains like:

- `rakymp` - Built environment (construction/BIM)
- `jhka` - Public administration architecture
- `oksa` - Education terminology
- `kela` - Social security
- `p2p` - Procurement to payment
- Many others

**API Base:** `https://sanastot.suomi.fi/terminology-api/api/v1/`

**Key Endpoints:**
```
GET /frontend/terminologies              - List all vocabularies
GET /frontend/terminology/{id}           - Get specific vocabulary
GET /frontend/terminology/{id}/concepts  - Get concepts in vocabulary
GET /frontend/searchConcept              - Search concepts across vocabularies
GET /export/{id}?format=xlsx             - Export vocabulary to Excel
```

**Data Structure:**
- **Terminology** (Sanasto): Collection of related concepts
- **Concept** (Käsite): Individual term with definition
- **Term** (Termi): Preferred term and synonyms
- **Definition** (Määritelmä): Explanation of the concept
- **Relations**: Hierarchical (broader/narrower) and associative relationships

### 2.3 Tietomallit (Data Models)

**URL:** https://tietomallit.suomi.fi/  
**Purpose:** Logical data structures and schemas  
**Content:** ~170 data models including:

- **Core Data Models** (Ydintietomalli): Reusable component libraries
- **Application Profiles** (Soveltamisprofiili): Domain-specific implementations

**Example Models:**
- `rytj-kaava` - Spatial planning data model
- `isa2core` - EU core vocabularies
- `raktkk` - Physical building structure
- `digione` - Education data models
- `efti` - Electronic freight transport

**API Base:** `https://tietomallit.suomi.fi/datamodel-api/api/v2/`

**Key Endpoints:**
```
GET /frontend/searchModels               - Search data models
GET /frontend/model/{prefix}             - Get specific model
GET /frontend/model/{prefix}/classes     - Get classes in model
GET /frontend/model/{prefix}/class/{id}  - Get specific class
GET /export/{prefix}                     - Export model (JSON-LD, RDF)
```

**Key Features:**
- UML-based class diagrams
- RDF/OWL representations
- Reusable components
- Version management
- Cross-references to vocabularies and code lists

### 2.4 Koodistot (Code Lists)

**URL:** https://koodistot.suomi.fi/  
**Purpose:** Enumerated value sets and classifications  
**Content:** 700+ code lists for:

- Building types
- Student types
- Countries
- Classifications
- Lookup tables

**API Base:** `https://koodistot.suomi.fi/codelist-api/api/v1/`

**Key Endpoints:**
```
GET /coderegistries                                       - List registries
GET /coderegistries/{registry}/codeschemes                - List code schemes
GET /coderegistries/{registry}/codeschemes/{scheme}       - Get code scheme
GET /coderegistries/{registry}/codeschemes/{scheme}/codes - Get codes
GET /coderegistries/{registry}/codeschemes/{scheme}/codes?format=csv - Export
```

**Data Format Example (CSV):**
```csv
CODEVALUE,URI,STATUS,PREFLABEL_FI,DEFINITION_FI,BROADERCODE
011,http://uri.suomi.fi/...,VALID,Yhden asunnon talot,"Asuinrakennukset...",01
```

---

## 3. Architecture Design

### 3.1 MCP Server Architecture

```
┌────────────────────────────────────────────────────────────┐
│                   CLIENT APPLICATIONS                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │Claude Desktop│  │   VS Code    │  │     Cursor       │ │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘ │
│         │                 │                    │           │
│         └─────────────────┼────────────────────┘           │
│                           │                                │
│                    MCP Protocol (stdio)                    │
└───────────────────────────┼────────────────────────────────┘
                            │
                   ┌────────▼─────────┐
                   │    MCP SERVER    │
                   │                  │
                   │  ┌────────────┐  │
                   │  │   Tools    │  │
                   │  ├────────────┤  │
                   │  │ Resources  │  │
                   │  └────────────┘  │
                   └────────┬─────────┘
                            │
       ┌────────────────────┼────────────────────┐
       │                    │                    │
┌──────▼───────┐   ┌────────▼────────┐   ┌──────▼───────┐
│   Sanastot   │   │   Tietomallit   │   │  Koodistot   │
│    Client    │   │     Client      │   │    Client    │
│              │   │                 │   │              │
│ • Search     │   │ • Search models │   │ • Get codes  │
│ • Get concept│   │ • Get classes   │   │ • List values│
│ • List vocabs│   │ • Get properties│   │ • Validate   │
└──────┬───────┘   └────────┬────────┘   └──────┬───────┘
       │                    │                    │
       │         HTTP/REST Requests              │
       │                    │                    │
┌──────▼────────────────────▼────────────────────▼───────┐
│              Yhteentoimivuusalusta APIs                │
│  sanastot.suomi.fi | tietomallit.suomi.fi |            │
│  koodistot.suomi.fi                                    │
└────────────────────────────────────────────────────────┘
```

### 3.2 Technology Stack

**Core:**
- **Language:** Python 3.11+ (recommended) or TypeScript
- **MCP Library:** `mcp` Python package (Anthropic official SDK)
- **HTTP Client:** `httpx` (async support)
- **Caching:** `diskcache` (local) or Redis (shared)
- **Data Models:** `pydantic` for validation

**Optional:**
- **Finnish NLP:** `voikko` for lemmatization (improves search)
- **Fuzzy Matching:** `rapidfuzz` for typo tolerance
- **Data Formats:** `openpyxl` (Excel), `rdflib` (RDF/OWL)

---

## 4. MCP Tool Definitions

### 4.1 Overview

The MCP server exposes **8 tools** organized by platform:

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

### 4.2 Terminology Tools (Sanastot)

#### Tool 1: `search_terminology`

**Purpose:** Search for standardized terms across vocabularies

```json
{
  "name": "search_terminology",
  "description": "Search for Finnish government standardized terms and concepts from sanastot.suomi.fi",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Search term in Finnish or English"
      },
      "vocabulary_id": {
        "type": "string",
        "description": "Optional: Limit to specific vocabulary (e.g., 'rakymp')"
      },
      "language": {
        "type": "string",
        "enum": ["fi", "en", "sv"],
        "default": "fi"
      },
      "max_results": {
        "type": "integer",
        "default": 10,
        "description": "Maximum results to return"
      }
    },
    "required": ["query"]
  }
}
```

**Example Usage:**
```
User: "I'm writing a design doc for a building permit system. 
       What's the correct term for 'rakennuskohde'?"

MCP Call: search_terminology(query="rakennuskohde", vocabulary_id="rakymp")

Response:
- Preferred Term: "fyysinen rakennuskohde"
- Definition: "rakennus, rakennelma tai niiden osa ja erityistä 
               toimintaa varten rakennettu alue"
- URI: https://sanastot.suomi.fi/terminology/rakymp/concept-X
- Related: rakennus, rakennelma, rakennusalue
```

#### Tool 2: `get_concept_details`

**Purpose:** Get full details of a specific concept

```json
{
  "name": "get_concept_details",
  "description": "Get detailed information about a concept including all terms, definitions, and relations",
  "inputSchema": {
    "type": "object",
    "properties": {
      "concept_id": {
        "type": "string",
        "description": "The concept identifier"
      },
      "vocabulary_id": {
        "type": "string",
        "description": "The vocabulary containing the concept"
      },
      "include_relations": {
        "type": "boolean",
        "default": true,
        "description": "Include broader/narrower/related concepts"
      }
    },
    "required": ["concept_id", "vocabulary_id"]
  }
}
```

#### Tool 3: `list_vocabularies`

**Purpose:** List available vocabularies with filtering

```json
{
  "name": "list_vocabularies",
  "description": "List all vocabularies from sanastot.suomi.fi with optional domain filtering",
  "inputSchema": {
    "type": "object",
    "properties": {
      "domain": {
        "type": "string",
        "description": "Filter by domain (e.g., 'Rakennettu ympäristö')"
      },
      "status": {
        "type": "string",
        "enum": ["VALID", "DRAFT", "INCOMPLETE"],
        "description": "Filter by status"
      }
    }
  }
}
```

### 4.3 Data Model Tools (Tietomallit)

#### Tool 4: `search_datamodel`

**Purpose:** Find relevant data models

```json
{
  "name": "search_datamodel",
  "description": "Search for data models and schemas from tietomallit.suomi.fi",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Search term for model name or content"
      },
      "model_type": {
        "type": "string",
        "enum": ["PROFILE", "LIBRARY"],
        "description": "PROFILE = application profile, LIBRARY = reusable components"
      },
      "domain": {
        "type": "string",
        "description": "Filter by domain (e.g., 'Rakennettu ympäristö')"
      }
    },
    "required": ["query"]
  }
}
```

**Example Usage:**
```
User: "What data model should I reference for building permit data?"

MCP Call: search_datamodel(query="rakennuslupa", domain="Rakennettu ympäristö")

Response:
- Model: "Rakennuslupatietomalli"
- ID: raklupa
- Status: Ehdotus (Draft)
- Description: "Rakennuslupa, Toimenpidelupa, Purkamislupa, Maisematyölupa"
- Related Vocabularies: rakymp
- Classes: Rakennuslupa, Toimenpidelupa, etc.
```

#### Tool 5: `get_datamodel_classes`

**Purpose:** Get classes and properties from a data model

```json
{
  "name": "get_datamodel_classes",
  "description": "Get class definitions from a data model including properties and associations",
  "inputSchema": {
    "type": "object",
    "properties": {
      "model_id": {
        "type": "string",
        "description": "The data model identifier (e.g., 'rytj-kaava')"
      },
      "class_name": {
        "type": "string",
        "description": "Optional: filter to specific class"
      },
      "include_properties": {
        "type": "boolean",
        "default": true
      },
      "include_associations": {
        "type": "boolean",
        "default": true
      }
    },
    "required": ["model_id"]
  }
}
```

### 4.4 Code List Tools (Koodistot)

#### Tool 6: `search_codelist`

**Purpose:** Search for code lists

```json
{
  "name": "search_codelist",
  "description": "Search for code lists from koodistot.suomi.fi",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Search term for code list name or content"
      },
      "registry": {
        "type": "string",
        "description": "Limit to specific code registry"
      }
    },
    "required": ["query"]
  }
}
```

#### Tool 7: `get_codes`

**Purpose:** Get all codes from a code list

```json
{
  "name": "get_codes",
  "description": "Get all code values from a specific code list",
  "inputSchema": {
    "type": "object",
    "properties": {
      "registry": {
        "type": "string",
        "description": "Code registry ID"
      },
      "scheme": {
        "type": "string",
        "description": "Code scheme ID"
      },
      "status": {
        "type": "string",
        "enum": ["VALID", "DRAFT", "DEPRECATED"],
        "default": "VALID"
      }
    },
    "required": ["registry", "scheme"]
  }
}
```

**Example Usage:**
```
User: "What are the valid student types for the education system?"

MCP Call: get_codes(registry="koulutus", scheme="OpiskelijaTyyppi")

Response:
Code List: OpiskelijaTyyppi
Values:
1. TUTKINTO_OPISKELIJA - Tutkinto-opiskelija (Degree student)
2. VAIHTO_OPISKELIJA - Vaihto-opiskelija (Exchange student)
3. TAYDENNYS_OPISKELIJA - Täydennyskoulutusopiskelija
[CSV Export Available]
```

### 4.5 Cross-Platform Tools

#### Tool 8: `validate_terminology`

**Purpose:** Check if text uses standardized terminology

```json
{
  "name": "validate_terminology",
  "description": "Validate terminology usage in design documentation against standards",
  "inputSchema": {
    "type": "object",
    "properties": {
      "text": {
        "type": "string",
        "description": "Text to validate",
        "maxLength": 10000
      },
      "vocabularies": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Vocabulary IDs to check against (default: all)"
      },
      "suggest_corrections": {
        "type": "boolean",
        "default": true
      }
    },
    "required": ["text"]
  }
}
```

**Example Usage:**
```
User: "Check this paragraph for correct terminology:
       'Järjestelmä käsittelee rakennuksen tietoja ja 
        tallentaa asunto-osakeyhtiön rekisteriin.'"

MCP Call: validate_terminology(text="...", vocabularies=["rakymp"])

Response:
✓ "rakennus" - Valid (standard term in rakymp)
✓ "asunto-osakeyhtiö" - Valid
✓ "tallentaa" - Valid verb form
ℹ "tietoja" - Consider more specific: "rakennustiedot", "kiinteistötiedot"
```

### 4.6 MCP Resources (Optional)

In addition to tools, the MCP server can expose **Resources** for static reference data:

```json
{
  "resources": [
    {
      "uri": "vocabulary://rakymp",
      "name": "Built Environment Vocabulary",
      "description": "Complete rakymp vocabulary for reference"
    },
    {
      "uri": "codelist://rakennustieto/RakennuksenKayttotarkoitus",
      "name": "Building Use Types",
      "description": "Code list of building use types"
    }
  ]
}
```

---

## 5. Implementation Plan

### Phase 1: Foundation (Week 1-2)

**Milestone 1.1: API Exploration**
- [ ] Test all three API endpoints with curl/Postman
- [ ] Document response structures
- [ ] Identify rate limits and caching needs
- [ ] Create example request/response library
- [ ] Verify API authentication requirements (none expected)

**Milestone 1.2: MCP Server Setup**
- [ ] Initialize MCP server project (Python)
- [ ] Set up development environment with uv/pip
- [ ] Configure basic server structure
- [ ] Test MCP connection with Claude Desktop
- [ ] Implement stdio transport

**Milestone 1.3: HTTP Clients**
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

### Phase 2: Core Tools (Week 3-4)

**Milestone 2.1: Terminology Tools**
- [ ] Implement `search_terminology`
- [ ] Implement `get_concept_details`
- [ ] Implement `list_vocabularies`
- [ ] Add multilingual support (FI/EN/SV)
- [ ] Add fuzzy matching for typos

**Milestone 2.2: Data Model Tools**
- [ ] Implement `search_datamodel`
- [ ] Implement `get_datamodel_classes`
- [ ] Parse class structures and properties
- [ ] Extract relationships and associations
- [ ] Link models to vocabularies

**Milestone 2.3: Code List Tools**
- [ ] Implement `search_codelist`
- [ ] Implement `get_codes`
- [ ] Support hierarchical code navigation
- [ ] Add CSV export capability

**Deliverables:**
- Seven working MCP tools
- Integration tests for each tool
- Tool documentation with examples

---

### Phase 3: Advanced Features (Week 5-6)

**Milestone 3.1: Text Validation**
- [ ] Implement `validate_terminology`
- [ ] Extract Finnish terms from text (tokenization)
- [ ] Match against vocabularies
- [ ] Generate suggestions for non-standard terms
- [ ] Optionally integrate Voikko for lemmatization

**Milestone 3.2: Cross-Platform Integration**
- [ ] Link vocabulary concepts to data models
- [ ] Link data model attributes to code lists
- [ ] Build unified search across platforms
- [ ] Add "suggest references" functionality

**Milestone 3.3: Caching & Performance**
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

### Phase 4: Testing & Documentation (Week 7-8)

**Milestone 4.1: Real-World Testing**
- [ ] Test with IFC Tarkistaja project documentation
- [ ] Test with building permit design docs
- [ ] Test with Finnish government integration specs
- [ ] Collect user feedback
- [ ] Performance benchmarking

**Milestone 4.2: Edge Cases & Error Handling**
- [ ] Handle missing/deprecated vocabularies
- [ ] Handle API failures gracefully
- [ ] Support offline mode (cached data)
- [ ] Handle mixed FI/EN text
- [ ] Validate all input parameters

**Milestone 4.3: Documentation**
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

## 6. Technical Specifications

### 6.1 Data Models

```python
# Core data models for the MCP server

from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict
from enum import Enum
from datetime import datetime

class Language(str, Enum):
    FI = "fi"
    EN = "en"
    SV = "sv"

class Status(str, Enum):
    DRAFT = "DRAFT"
    VALID = "VALID"
    DEPRECATED = "DEPRECATED"
    INCOMPLETE = "INCOMPLETE"

class LocalizedString(BaseModel):
    """Multi-language string"""
    fi: Optional[str] = None
    en: Optional[str] = None
    sv: Optional[str] = None

class Term(BaseModel):
    """Represents a term in a vocabulary"""
    label: str
    language: Language
    status: str  # PREFERRED, ACCEPTABLE, etc.
    scope: Optional[str] = None

class Concept(BaseModel):
    """Represents a concept in a vocabulary"""
    id: str
    uri: HttpUrl
    vocabulary_id: str
    preferred_label: LocalizedString
    definition: Optional[LocalizedString] = None
    terms: List[Term] = []
    status: Status
    broader: List[str] = []
    narrower: List[str] = []
    related: List[str] = []
    created: Optional[datetime] = None
    modified: Optional[datetime] = None

class Vocabulary(BaseModel):
    """Represents a vocabulary/terminology"""
    id: str
    uri: HttpUrl
    label: LocalizedString
    description: Optional[LocalizedString] = None
    domain: List[str] = []
    organization: Optional[str] = None
    concept_count: int = 0
    status: Status
    languages: List[Language] = []

class DataModelClass(BaseModel):
    """Represents a class in a data model"""
    id: str
    uri: HttpUrl
    label: LocalizedString
    description: Optional[LocalizedString] = None
    is_abstract: bool = False
    parent_class: Optional[str] = None
    properties: List[Dict] = []
    associations: List[Dict] = []
    vocabulary_references: List[Dict] = []

class DataModel(BaseModel):
    """Represents a data model"""
    id: str
    uri: HttpUrl
    type: str  # PROFILE or LIBRARY
    status: Status
    label: LocalizedString
    description: Optional[LocalizedString] = None
    domain: List[str] = []
    version: Optional[str] = None
    classes: List[DataModelClass] = []

class Code(BaseModel):
    """Represents a code in a code list"""
    code: str
    uri: HttpUrl
    label: LocalizedString
    definition: Optional[LocalizedString] = None
    status: Status
    broader_code: Optional[str] = None
    order: Optional[int] = None

class CodeScheme(BaseModel):
    """Represents a code list"""
    id: str
    registry: str
    uri: HttpUrl
    label: LocalizedString
    description: Optional[LocalizedString] = None
    version: Optional[str] = None
    code_count: int = 0
    codes: List[Code] = []
```

### 6.2 Caching Strategy

```python
# Caching configuration

CACHE_CONFIG = {
    "vocabularies": {
        "ttl": 86400,      # 24 hours - vocabulary list changes rarely
        "max_size": 200
    },
    "concepts": {
        "ttl": 43200,      # 12 hours - concepts may be updated
        "max_size": 5000
    },
    "data_models": {
        "ttl": 86400,      # 24 hours - models change rarely
        "max_size": 100
    },
    "classes": {
        "ttl": 43200,      # 12 hours
        "max_size": 2000
    },
    "code_schemes": {
        "ttl": 3600,       # 1 hour - code lists may update
        "max_size": 500
    },
    "codes": {
        "ttl": 3600,       # 1 hour
        "max_size": 10000
    }
}

# Cache key patterns
# vocabulary:{id}
# concept:{vocabulary_id}:{concept_id}
# model:{model_id}
# class:{model_id}:{class_id}
# scheme:{registry}:{scheme}
# codes:{registry}:{scheme}
```

### 6.3 Configuration File

```yaml
# config.yaml

server:
  name: "yhteentoimivuusalusta-mcp"
  version: "1.0.0"
  transport: "stdio"

apis:
  sanastot:
    base_url: "https://sanastot.suomi.fi/terminology-api/api/v1"
    timeout: 30
    retry_count: 3
  tietomallit:
    base_url: "https://tietomallit.suomi.fi/datamodel-api/api/v2"
    timeout: 30
    retry_count: 3
  koodistot:
    base_url: "https://koodistot.suomi.fi/codelist-api/api/v1"
    timeout: 30
    retry_count: 3

cache:
  enabled: true
  backend: "disk"  # or "redis"
  directory: "~/.cache/yhteentoimivuusalusta"
  # Redis config (if backend is redis)
  redis_url: "redis://localhost:6379/0"

defaults:
  language: "fi"
  max_results: 10
  # Default vocabularies for validation
  vocabularies:
    - "rakymp"  # Most common for building projects

logging:
  level: "INFO"
  file: "~/.local/share/yhteentoimivuusalusta/logs/server.log"

fuzzy_matching:
  enabled: true
  threshold: 0.8  # 80% similarity required

# Finnish NLP (optional)
nlp:
  voikko_enabled: false  # Requires libvoikko
  lemmatize_queries: true
```

---

## 7. Use Case Examples

### Use Case 1: Writing IFC Validation Design Document

**Scenario:** Developer is writing a design document for an IFC file validator

**Workflow:**
```
1. Developer writes: "System validates rakennusosan properties"

2. Asks Claude: "Check if I'm using the right terminology"

3. Claude uses validate_terminology:
   - Finds "rakennusosa" 
   - Checks against rakymp vocabulary
   - Confirms it's a standard term
   - Suggests related terms: "tuoteosa", "rakennuselementti"

4. Developer asks: "What data model should I reference?"

5. Claude uses search_datamodel:
   - Topic: "rakennuskohde"
   - Returns: raktkk (Fyysinen rakennuskohde)
   - Shows classes: Rakennus, Rakennusosa, etc.

6. Developer asks: "What are the valid values for building type?"

7. Claude uses get_codes:
   - Finds RakennuksenKayttotarkoitus in koodistot
   - Returns: 011 Yhden asunnon talot, 012 Kahden asunnon talot, etc.
   - Provides URIs for referencing in design doc
```

### Use Case 2: Government Integration Specification

**Scenario:** Writing API specification for Kela integration

**Workflow:**
```
1. Developer searches: "social security terminology"

2. Claude uses list_vocabularies:
   - Filters by domain containing "kela" or "sosiaaliturva"
   - Returns relevant vocabularies

3. Claude uses search_terminology:
   - vocabulary_id: "kela"
   - Returns: "etuus", "vakuutettu", "korvaava toiminta"

4. Developer asks: "What data model for social security benefits?"

5. Claude uses search_datamodel:
   - Finds relevant Kela data structures
   - Shows benefit types and relationships

6. Developer writes spec using standardized terms

7. Claude validates terminology before submission
```

### Use Case 3: Cross-Platform Discovery

**Scenario:** Finding all standards related to "kiinteistö" (real estate)

**Workflow:**
```
1. Developer asks: "Find all standards related to kiinteistö"

2. Claude makes multiple tool calls:
   - search_terminology(query="kiinteistö")
   - search_datamodel(query="kiinteistö")
   - search_codelist(query="kiinteistö")

3. Claude synthesizes results:

   Terminology (sanastot.suomi.fi):
   - kiinteistö (rakymp): Maanomistuksen perusyksikkö
   - kiinteistörekisteri: Virallinen rekisteri
   - kiinteistötunnus: Yksilöivä tunniste

   Data Models (tietomallit.suomi.fi):
   - kmr-kiinteisto: Core real estate model
   - rytj-kaava: References kiinteistö

   Code Lists (koodistot.suomi.fi):
   - KiinteistoTyyppi: Real estate type codes
   - KiinteistonKayttotarkoitus: Usage codes
```

---

## 8. Success Criteria

### 8.1 Technical Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Response Time (cached) | < 500ms | P95 latency |
| Response Time (uncached) | < 3s | P95 latency |
| API Coverage | 100% | All 3 platforms |
| Cache Hit Rate | > 80% | For repeat queries |
| Error Rate | < 1% | Failed requests |

### 8.2 User Experience Metrics

- **Time Saved:** 50% reduction in manual reference lookup
- **Accuracy:** 95% correct term suggestions
- **Ease of Use:** Zero configuration required for basic usage
- **Documentation Quality:** Measurable increase in standard references

### 8.3 Functional Requirements

- [ ] Search across ~90 vocabularies
- [ ] Access ~170 data models
- [ ] Query 700+ code lists
- [ ] Support FI, EN, SV languages
- [ ] Offline mode with cached data
- [ ] Export capabilities (CSV, JSON)

---

## 9. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **API Changes** | Medium | High | Monitor API versions, implement adapters, use versioned endpoints |
| **Rate Limiting** | Low | Medium | Aggressive caching, batch requests, exponential backoff |
| **API Downtime** | Low | High | Offline mode with cached data, graceful degradation |
| **Terminology Updates** | Medium | Low | TTL-based cache invalidation, periodic refresh |
| **Language Complexity** | High | Medium | Use Voikko for Finnish NLP, fallback to simple matching |
| **Scope Creep** | Medium | Medium | Strict phasing, MVP-first approach, clear requirements |
| **MCP Protocol Changes** | Low | Medium | Use official SDK, monitor Anthropic updates |

---

## 10. Future Enhancements (Post-MVP)

### Phase 5: Advanced Features

**A. Code Generation**
- Generate Python/TypeScript classes from data models
- Create Pydantic models from tietomallit
- Generate OpenAPI specs with proper terminology

**B. Documentation Templates**
- Pre-filled design document templates
- Auto-populate with relevant standards
- Generate bibliography/references section

**C. CI/CD Integration**
- Pre-commit hook for terminology validation
- GitHub Action for design doc checks
- Automatic reference updates

**D. IDE Extensions**
- VS Code extension with inline suggestions
- Hover tooltips with definitions
- Quick fixes for non-standard terms

**E. Comparative Analysis**
- Compare terminology across documents
- Identify inconsistencies
- Suggest harmonization

---

## 11. Deliverables

### Code Deliverables

```
yhteentoimivuusalusta-mcp/
├── README.md
├── LICENSE
├── pyproject.toml
├── config.yaml.example
├── src/
│   └── yhteentoimivuusalusta_mcp/
│       ├── __init__.py
│       ├── server.py              # MCP server entry point
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── terminology.py     # search_terminology, get_concept_details, list_vocabularies
│       │   ├── datamodel.py       # search_datamodel, get_datamodel_classes
│       │   ├── codelist.py        # search_codelist, get_codes
│       │   └── validation.py      # validate_terminology
│       ├── clients/
│       │   ├── __init__.py
│       │   ├── base.py            # Base HTTP client
│       │   ├── sanastot.py        # Sanastot API client
│       │   ├── tietomallit.py     # Tietomallit API client
│       │   └── koodistot.py       # Koodistot API client
│       ├── models/
│       │   ├── __init__.py
│       │   └── schemas.py         # Pydantic models
│       └── utils/
│           ├── __init__.py
│           ├── cache.py           # Caching utilities
│           ├── config.py          # Configuration loader
│           └── nlp.py             # Finnish NLP utilities (optional)
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Pytest fixtures
│   ├── test_tools/
│   │   ├── __init__.py
│   │   ├── test_terminology.py
│   │   ├── test_datamodel.py
│   │   └── test_codelist.py
│   ├── test_clients/
│   │   ├── __init__.py
│   │   ├── test_sanastot.py
│   │   ├── test_tietomallit.py
│   │   └── test_koodistot.py
│   └── fixtures/
│       ├── vocabulary_response.json
│       ├── concept_response.json
│       ├── model_response.json
│       └── codes_response.json
└── docs/
    ├── INSTALLATION.md
    ├── USAGE.md
    ├── API_REFERENCE.md
    ├── EXAMPLES.md
    ├── TROUBLESHOOTING.md
    └── CONTRIBUTING.md
```

### Documentation Deliverables

- [x] Installation guide (INSTALLATION.md)
- [x] User manual (USAGE.md)
- [x] API reference (API_REFERENCE.md)
- [x] Example use cases (EXAMPLES.md)
- [x] API response examples (API_RESPONSES.md)
- [ ] Troubleshooting guide (TROUBLESHOOTING.md)
- [ ] Contributing guidelines (CONTRIBUTING.md)

---

## 12. Installation & Setup (Draft)

### 12.1 Prerequisites

```bash
# Python 3.11+
python --version  # Should be 3.11 or higher

# MCP-compatible client
# - Claude Desktop
# - VS Code with MCP extension
# - Cursor
```

### 12.2 Installation

```bash
# Clone repository
git clone https://github.com/yourusername/yhteentoimivuusalusta-mcp.git
cd yhteentoimivuusalusta-mcp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Copy configuration
cp config.yaml.example config.yaml

# Test server
python -m yhteentoimivuusalusta_mcp.server
```

### 12.3 Claude Desktop Configuration

Edit `~/.config/Claude/claude_desktop_config.json` (Linux) or equivalent:

```json
{
  "mcpServers": {
    "yhteentoimivuusalusta": {
      "command": "/path/to/yhteentoimivuusalusta-mcp/venv/bin/python",
      "args": ["-m", "yhteentoimivuusalusta_mcp.server"],
      "cwd": "/path/to/yhteentoimivuusalusta-mcp"
    }
  }
}
```

---

## 13. Budget & Resources

### 13.1 Time Estimate

| Phase | Duration | Effort (hours) |
|-------|----------|----------------|
| Phase 1: Foundation | 2 weeks | 40 hours |
| Phase 2: Core Tools | 2 weeks | 40 hours |
| Phase 3: Advanced Features | 2 weeks | 40 hours |
| Phase 4: Testing & Docs | 2 weeks | 40 hours |
| **Total** | **8 weeks** | **160 hours** |

### 13.2 Resources Needed

**Development:**
- Developer time: 160 hours
- Code review: 20 hours

**Infrastructure:**
- None required (uses public APIs)
- Optional: Redis for shared caching

**Testing:**
- Access to real design documents
- Sample IFC files for validation testing
- Government integration specs for examples

---

## 14. Next Steps

### Immediate Actions (This Week)

1. **API Exploration** (2 hours)
   - Test sanastot.suomi.fi API endpoints
   - Test tietomallit.suomi.fi API endpoints
   - Test koodistot.suomi.fi API endpoints
   - Document any authentication requirements
   - Record response structures

2. **MCP Server Setup** (4 hours)
   - Create project structure
   - Set up development environment with uv
   - Configure basic MCP server
   - Test connection with Claude Desktop

3. **First Tool Implementation** (4 hours)
   - Implement basic `search_terminology`
   - Test with rakymp vocabulary
   - Validate response formatting

### Short-term Goals (Next 2 Weeks)

- Complete Phase 1 (Foundation)
- Have working API clients for all 3 platforms
- Basic MCP server operational
- One complete tool working end-to-end

### Medium-term Goals (Next 2 Months)

- Complete MVP (Phases 1-4)
- Production-ready MCP server
- Comprehensive documentation
- Real-world usage validation with IFC Tarkistaja project

---

## 15. Conclusion

This MCP tool will significantly streamline the process of writing design documentation for Finnish government and building industry projects. By providing instant access to standardized terminologies, data models, and code lists, it will:

1. **Improve Documentation Quality** - Proper use of official terms with correct definitions
2. **Save Developer Time** - No more manual reference lookup across multiple websites
3. **Ensure Compliance** - Automatic validation against Finnish government standards
4. **Enable Discovery** - Find relevant standards through AI-assisted search

The phased approach ensures steady progress with concrete deliverables at each milestone, while the MCP architecture provides seamless integration with existing AI-assisted workflows in Claude Desktop, VS Code, and other compatible tools.

---

## Appendix A: Vocabulary Domains

Quick reference for common information domains in Sanastot:

| Domain (Finnish) | Domain (English) | Vocab Count | Example IDs |
|------------------|------------------|-------------|-------------|
| Rakennettu ympäristö | Built Environment | ~32 | rakymp, raktkk |
| Yleiset tieto- ja hallintopalvelut | IT & Administration | ~32 | jhka, jhs |
| Verotus ja julkinen talous | Taxation & Finance | ~16 | vero |
| Koulutus | Education | ~11 | oksa, digione |
| Elinkeinot | Business | ~5 | yritys |
| Liikenne | Transportation | ~4 | liikenne |
| Oikeusturva | Legal | ~4 | oikeus |

## Appendix B: Common Resource IDs

### Vocabularies (Sanastot)
- `rakymp` - Built environment vocabulary (Rakennetun ympäristön sanasto)
- `jhka` - Public admin architecture (Julkisen hallinnon kokonaisarkkitehtuuri)
- `oksa` - Education vocabulary (Opetus- ja koulutussanasto)
- `kela` - Social security vocabulary

### Data Models (Tietomallit)
- `rytj-kaava` - Spatial planning data model
- `raktkk` - Physical building data model
- `isa2core` - EU core vocabularies
- `kmr` - Public admin core model
- `digione` - Education data models
- `jhs` - Public admin components

### Code Registries (Koodistot)
- `rakennustieto` - Building information codes
- `koulutus` - Education codes
- `julkishallinto` - Public administration codes

## Appendix C: API Response Examples

See separate document: [API_RESPONSES.md](./API_RESPONSES.md)

---

**Document Version Control:**

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2026-01-29 | Initial project plan |
| v1.1 | 2026-01-29 | Added missing tools, fixed inconsistencies, improved diagrams, added Tietomallit endpoints, updated Appendix B |
