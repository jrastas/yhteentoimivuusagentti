# API Reference

Complete reference for all MCP tools provided by the Yhteentoimivuusalusta server.

## Table of Contents

- [Terminology Tools](#terminology-tools)
  - [search_terminology](#search_terminology)
  - [get_concept_details](#get_concept_details)
  - [list_vocabularies](#list_vocabularies)
- [Data Model Tools](#data-model-tools)
  - [search_datamodel](#search_datamodel)
  - [get_datamodel_classes](#get_datamodel_classes)
  - [get_model_vocabulary_links](#get_model_vocabulary_links)
- [Code List Tools](#code-list-tools)
  - [search_codelist](#search_codelist)
  - [get_codes](#get_codes)
  - [export_codes_csv](#export_codes_csv)
- [Cross-Platform Tools](#cross-platform-tools)
  - [validate_terminology](#validate_terminology)
  - [unified_search](#unified_search)
  - [suggest_references](#suggest_references)
  - [get_codelist_for_attribute](#get_codelist_for_attribute)

---

## Terminology Tools

Tools for accessing sanastot.suomi.fi terminologies.

### search_terminology

Search for standardized terms and concepts across vocabularies.

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `query` | string | Yes | - | Search term in Finnish, English, or Swedish |
| `vocabulary_id` | string | No | null | Limit to specific vocabulary (e.g., 'rakymp') |
| `language` | string | No | "fi" | Search language: "fi", "en", or "sv" |
| `max_results` | integer | No | 10 | Maximum results (1-1000) |

**Returns:**

```typescript
{
  results: Array<{
    id: string;
    vocabulary_id: string;
    label: string;
    definition: string | null;
    status: "VALID" | "DRAFT" | "RETIRED";
    score: number;  // Relevance score 0-1
  }>;
  total_count: number;
  query: string;
  vocabulary_id: string | null;
}
```

**Example:**

```json
{
  "query": "rakennus",
  "vocabulary_id": "rakymp",
  "max_results": 5
}
```

---

### get_concept_details

Get detailed information about a specific concept.

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `vocabulary_id` | string | Yes | - | The vocabulary containing the concept |
| `concept_id` | string | Yes | - | The concept identifier |
| `include_relations` | boolean | No | true | Include broader/narrower/related concepts |

**Returns:**

```typescript
{
  id: string;
  uri: string;
  vocabulary_id: string;
  preferred_label: {
    fi?: string;
    en?: string;
    sv?: string;
  };
  definition: {
    fi?: string;
    en?: string;
    sv?: string;
  };
  terms: Array<{
    label: string;
    language: "fi" | "en" | "sv";
    status: "PREFERRED" | "SYNONYM" | "NOT_RECOMMENDED";
    scope?: string;
  }>;
  status: "VALID" | "DRAFT" | "RETIRED";
  broader: string[];   // Parent concept IDs
  narrower: string[];  // Child concept IDs
  related: string[];   // Related concept IDs
}
```

**Errors:**

- Returns `{"error": "Concept not found", ...}` if concept doesn't exist

---

### list_vocabularies

List all available vocabularies.

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `domain` | string | No | null | Filter by domain/category |
| `status` | string | No | null | Filter by status: "VALID", "DRAFT", "RETIRED" |

**Returns:**

```typescript
{
  vocabularies: Array<{
    id: string;
    prefix: string;
    label: {
      fi?: string;
      en?: string;
      sv?: string;
    };
    description: {
      fi?: string;
      en?: string;
      sv?: string;
    };
    status: string;
    uri: string;
    concept_count: number;
  }>;
  total_count: number;
}
```

---

## Data Model Tools

Tools for accessing tietomallit.suomi.fi data models.

### search_datamodel

Search for data models by name or description.

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `query` | string | Yes | - | Search term |
| `model_type` | string | No | null | Filter by type: "PROFILE", "LIBRARY" |
| `domain` | string | No | null | Filter by domain |
| `max_results` | integer | No | 10 | Maximum results (1-1000) |

**Returns:**

```typescript
{
  results: Array<{
    id: string;
    prefix: string;
    label: {
      fi?: string;
      en?: string;
    };
    description: {
      fi?: string;
      en?: string;
    };
    type: string;
    status: string;
    uri: string;
  }>;
  total_count: number;
  query: string;
}
```

---

### get_datamodel_classes

Get classes and their properties from a data model.

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `model_id` | string | Yes | - | Data model identifier/prefix |
| `class_name` | string | No | null | Filter to specific class |
| `include_properties` | boolean | No | true | Include class properties |
| `include_associations` | boolean | No | true | Include associations to other classes |

**Returns:**

```typescript
{
  model_id: string;
  model_name: string;
  classes: Array<{
    id: string;
    label: {
      fi?: string;
      en?: string;
    };
    description: {
      fi?: string;
      en?: string;
    };
    uri: string;
    properties: Array<{
      id: string;
      label: {
        fi?: string;
        en?: string;
      };
      description: {
        fi?: string;
        en?: string;
      };
      datatype: string;
      min_count: number;
      max_count: number | null;
      codelist_uri?: string;  // If property uses a code list
    }>;
    associations: Array<{
      id: string;
      label: {
        fi?: string;
        en?: string;
      };
      target_class: string;
      min_count: number;
      max_count: number | null;
    }>;
  }>;
  total_classes: number;
}
```

---

### get_model_vocabulary_links

Find vocabulary concepts linked to a data model.

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `model_id` | string | Yes | - | Data model identifier/prefix |

**Returns:**

```typescript
{
  model_id: string;
  vocabulary_links: Array<{
    vocabulary_id: string;
    vocabulary_name: string;
    concept_id: string;
    concept_label: string;
    linked_element: string;  // Class or property that uses this concept
    link_type: "definition" | "subject" | "concept";
  }>;
  linked_vocabularies: string[];  // Unique vocabulary IDs
}
```

---

## Code List Tools

Tools for accessing koodistot.suomi.fi code lists.

### search_codelist

Search for code lists by name or description.

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `query` | string | Yes | - | Search term |
| `registry` | string | No | null | Filter by code registry |
| `max_results` | integer | No | 10 | Maximum results (1-1000) |

**Returns:**

```typescript
{
  results: Array<{
    registry: string;
    scheme: string;
    label: {
      fi?: string;
      en?: string;
    };
    description: {
      fi?: string;
      en?: string;
    };
    status: string;
    code_count: number;
  }>;
  total_count: number;
  query: string;
}
```

---

### get_codes

Get codes from a specific code list.

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `registry` | string | Yes | - | Code registry identifier |
| `scheme` | string | Yes | - | Code scheme identifier |
| `status` | string | No | "VALID" | Filter by status |
| `max_results` | integer | No | 100 | Maximum results (1-1000) |

**Returns:**

```typescript
{
  registry: string;
  scheme: string;
  scheme_label: string;
  codes: Array<{
    code_value: string;
    label: {
      fi?: string;
      en?: string;
    };
    definition: {
      fi?: string;
      en?: string;
    };
    status: string;
    broader_code: string | null;  // Parent code for hierarchical lists
    order: number;
  }>;
  total_count: number;
}
```

**Errors:**

- Returns `{"error": "Code scheme not found", ...}` if registry/scheme doesn't exist

---

### export_codes_csv

Export codes to CSV format.

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `registry` | string | Yes | - | Code registry identifier |
| `scheme` | string | Yes | - | Code scheme identifier |
| `status` | string | No | "VALID" | Filter by status |
| `include_header` | boolean | No | true | Include CSV header row |

**Returns:**

```typescript
{
  csv_content: string;  // CSV formatted string
  row_count: number;
  columns: string[];    // Column names
}
```

**CSV Columns:**

- `code_value` - The code identifier
- `label_fi` - Finnish label
- `label_en` - English label (if available)
- `definition_fi` - Finnish definition
- `status` - Code status
- `broader_code` - Parent code (for hierarchical lists)

---

## Cross-Platform Tools

Tools that work across multiple platforms.

### validate_terminology

Validate text against standardized vocabularies.

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `text` | string | Yes | - | Text to validate (max 50,000 chars) |
| `vocabularies` | string[] | No | null | Limit to specific vocabularies |
| `suggest_corrections` | boolean | No | true | Suggest alternatives for unknown terms |
| `fuzzy_threshold` | number | No | 0.8 | Similarity threshold for suggestions (0-1) |

**Returns:**

```typescript
{
  valid_terms: Array<{
    term: string;
    vocabulary: string;
    concept_id: string;
    definition: string | null;
  }>;
  unknown_terms: Array<{
    term: string;
    suggestions: Array<{
      term: string;
      vocabulary: string;
      concept_id: string;
      score: number;  // Similarity score 0-1
    }>;
  }>;
  statistics: {
    total_terms: number;
    valid_terms: number;
    unknown_terms: number;
    validation_rate: number;  // Ratio of valid terms
  };
}
```

---

### unified_search

Search all platforms simultaneously.

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `query` | string | Yes | - | Search term |
| `search_terminologies` | boolean | No | true | Search sanastot.suomi.fi |
| `search_datamodels` | boolean | No | true | Search tietomallit.suomi.fi |
| `search_codelists` | boolean | No | true | Search koodistot.suomi.fi |
| `max_results_per_platform` | integer | No | 5 | Max results per platform (1-50) |

**Returns:**

```typescript
{
  query: string;
  terminology_results: Array<{
    id: string;
    vocabulary_id: string;
    label: string;
    definition: string | null;
    score: number;
  }>;
  datamodel_results: Array<{
    id: string;
    prefix: string;
    label: string;
    type: string;
  }>;
  codelist_results: Array<{
    registry: string;
    scheme: string;
    label: string;
    code_count: number;
  }>;
  total_results: number;
  search_time_ms: number;
}
```

---

### suggest_references

Analyze text and suggest relevant standards to reference.

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `text` | string | Yes | - | Text to analyze (max 50,000 chars) |
| `max_suggestions` | integer | No | 10 | Maximum suggestions per category (1-100) |

**Returns:**

```typescript
{
  suggested_vocabularies: Array<{
    id: string;
    prefix: string;
    name: string;
    matched_terms: string[];
    relevance_score: number;
  }>;
  suggested_datamodels: Array<{
    id: string;
    prefix: string;
    name: string;
    relevance_score: number;
  }>;
  suggested_codelists: Array<{
    registry: string;
    scheme: string;
    name: string;
    relevance_score: number;
  }>;
  extracted_terms: string[];  // Terms found in the text
}
```

---

### get_codelist_for_attribute

Find code lists that can be used with data model attributes.

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `model_id` | string | Yes | - | Data model identifier/prefix |
| `class_name` | string | No | null | Filter to specific class |

**Returns:**

```typescript
{
  model_id: string;
  attribute_codelists: Array<{
    class_name: string;
    attribute_name: string;
    attribute_label: string;
    codelist_uri: string;
    codelist_registry: string | null;
    codelist_scheme: string | null;
    codes_preview: Array<{
      code_value: string;
      label: string;
    }>;
  }>;
  total_attributes_with_codelists: number;
}
```

---

## Error Handling

All tools return errors in a consistent format:

```typescript
{
  error: string;        // Error message
  tool: string;         // Tool name that failed
  arguments: object;    // Arguments that were passed
  details?: string;     // Additional error details (optional)
}
```

**Common Errors:**

| Error | Cause |
|-------|-------|
| `"Missing required parameter: 'X'"` | Required parameter was not provided |
| `"Parameter 'X' cannot be empty"` | String parameter was empty |
| `"Concept not found"` | Requested concept doesn't exist |
| `"Code scheme not found"` | Requested code list doesn't exist |
| `"API request failed"` | Network or API error |

---

## Rate Limits

The server implements rate limiting to protect the underlying APIs:

- **Default limit:** 10 requests per second (shared across all platforms)
- **Retry behavior:** Failed requests are retried up to 3 times with exponential backoff

## Caching

Responses are cached to improve performance:

| Data Type | Cache TTL |
|-----------|-----------|
| Vocabularies list | 24 hours |
| Vocabulary details | 24 hours |
| Concepts | 12 hours |
| Search results | 1 hour |
| Data models | 24 hours |
| Classes | 12 hours |
| Code lists | 1 hour |
| Codes | 1 hour |

**Offline Mode:** When APIs are unavailable, the server can return cached data (up to 7 days old) as a fallback.
