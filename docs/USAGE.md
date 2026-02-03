# Usage Guide

This guide shows how to use the Yhteentoimivuusalusta MCP Server tools in practice.

## Table of Contents

1. [Searching for Terminology](#searching-for-terminology)
2. [Working with Data Models](#working-with-data-models)
3. [Using Code Lists](#using-code-lists)
4. [Validating Documents](#validating-documents)
5. [Cross-Platform Search](#cross-platform-search)
6. [Common Workflows](#common-workflows)

---

## Searching for Terminology

### Basic Term Search

Search for Finnish standardized terms:

```json
{
  "tool": "search_terminology",
  "arguments": {
    "query": "rakennus"
  }
}
```

**Response:**
```json
{
  "results": [
    {
      "id": "concept-123",
      "vocabulary_id": "rakymp",
      "label": "rakennus",
      "definition": "Kiinteä tai pysyväksi tarkoitettu rakennelma",
      "score": 1.0
    }
  ],
  "total_count": 15,
  "query": "rakennus"
}
```

### Search in Specific Vocabulary

Limit search to the built environment vocabulary:

```json
{
  "tool": "search_terminology",
  "arguments": {
    "query": "kerrosala",
    "vocabulary_id": "rakymp",
    "language": "fi",
    "max_results": 5
  }
}
```

### Get Concept Details

Get full details including relations:

```json
{
  "tool": "get_concept_details",
  "arguments": {
    "vocabulary_id": "rakymp",
    "concept_id": "concept-123",
    "include_relations": true
  }
}
```

**Response:**
```json
{
  "id": "concept-123",
  "vocabulary_id": "rakymp",
  "preferred_label": {
    "fi": "rakennus",
    "en": "building",
    "sv": "byggnad"
  },
  "definition": {
    "fi": "Kiinteä tai pysyväksi tarkoitettu rakennelma",
    "en": "A permanent or intended to be permanent structure"
  },
  "terms": [
    {"label": "rakennus", "language": "fi", "status": "PREFERRED"},
    {"label": "talo", "language": "fi", "status": "SYNONYM"}
  ],
  "broader": ["concept-100"],
  "narrower": ["concept-124", "concept-125"],
  "related": []
}
```

### List Vocabularies

Find available vocabularies:

```json
{
  "tool": "list_vocabularies",
  "arguments": {
    "status": "VALID"
  }
}
```

---

## Working with Data Models

### Search Data Models

Find data models related to spatial planning:

```json
{
  "tool": "search_datamodel",
  "arguments": {
    "query": "kaava",
    "max_results": 10
  }
}
```

### Get Model Classes

Retrieve classes from a specific data model:

```json
{
  "tool": "get_datamodel_classes",
  "arguments": {
    "model_id": "rytj-kaava",
    "include_properties": true,
    "include_associations": true
  }
}
```

**Response:**
```json
{
  "model_id": "rytj-kaava",
  "model_name": "Kaavatietomalli",
  "classes": [
    {
      "id": "Kaava",
      "label": {"fi": "Kaava"},
      "description": {"fi": "Maankäytön suunnitelma"},
      "properties": [
        {
          "id": "nimi",
          "label": {"fi": "nimi"},
          "datatype": "xsd:string",
          "min_count": 1,
          "max_count": 1
        }
      ],
      "associations": [
        {
          "id": "koskeeAluetta",
          "label": {"fi": "koskee aluetta"},
          "target_class": "Alue"
        }
      ]
    }
  ],
  "total_classes": 25
}
```

### Get Specific Class

Filter to a specific class:

```json
{
  "tool": "get_datamodel_classes",
  "arguments": {
    "model_id": "rytj-kaava",
    "class_name": "Kaava"
  }
}
```

### Link Models to Vocabularies

Find vocabulary concepts used by a data model:

```json
{
  "tool": "get_model_vocabulary_links",
  "arguments": {
    "model_id": "rytj-kaava"
  }
}
```

---

## Using Code Lists

### Search Code Lists

Find code lists for building types:

```json
{
  "tool": "search_codelist",
  "arguments": {
    "query": "rakennustyyppi",
    "max_results": 10
  }
}
```

### Get Codes from a Code List

Retrieve all codes:

```json
{
  "tool": "get_codes",
  "arguments": {
    "registry": "rakennustieto",
    "scheme": "rakennusluokitus",
    "status": "VALID",
    "max_results": 100
  }
}
```

**Response:**
```json
{
  "registry": "rakennustieto",
  "scheme": "rakennusluokitus",
  "codes": [
    {
      "code_value": "0110",
      "label": {"fi": "Omakotitalot"},
      "definition": {"fi": "Yhden asunnon talot"},
      "status": "VALID",
      "broader_code": "01",
      "order": 1
    },
    {
      "code_value": "0111",
      "label": {"fi": "Paritalot"},
      "definition": {"fi": "Kahden asunnon talot"},
      "status": "VALID",
      "broader_code": "01",
      "order": 2
    }
  ],
  "total_count": 150
}
```

### Export Codes to CSV

Export for use in spreadsheets:

```json
{
  "tool": "export_codes_csv",
  "arguments": {
    "registry": "rakennustieto",
    "scheme": "rakennusluokitus",
    "include_header": true
  }
}
```

**Response:**
```json
{
  "csv_content": "code_value,label_fi,definition_fi,status,broader_code\n0110,Omakotitalot,Yhden asunnon talot,VALID,01\n0111,Paritalot,Kahden asunnon talot,VALID,01\n...",
  "row_count": 150
}
```

---

## Validating Documents

### Validate Terminology in Text

Check if a document uses standardized terms:

```json
{
  "tool": "validate_terminology",
  "arguments": {
    "text": "Rakennuksen kerrosala lasketaan ulkoseinien ulkopintojen mukaan. Tontin pinta-ala on 500 neliömetriä.",
    "vocabularies": ["rakymp"],
    "suggest_corrections": true,
    "fuzzy_threshold": 0.8
  }
}
```

**Response:**
```json
{
  "valid_terms": [
    {
      "term": "rakennus",
      "vocabulary": "rakymp",
      "concept_id": "concept-123",
      "definition": "Kiinteä rakennelma"
    },
    {
      "term": "kerrosala",
      "vocabulary": "rakymp",
      "concept_id": "concept-456"
    }
  ],
  "unknown_terms": [
    {
      "term": "neliömetriä",
      "suggestions": [
        {"term": "neliömetri", "vocabulary": "rakymp", "score": 0.95}
      ]
    }
  ],
  "statistics": {
    "total_terms": 8,
    "valid_terms": 6,
    "unknown_terms": 2,
    "validation_rate": 0.75
  }
}
```

---

## Cross-Platform Search

### Unified Search

Search all platforms simultaneously:

```json
{
  "tool": "unified_search",
  "arguments": {
    "query": "rakennus",
    "search_terminologies": true,
    "search_datamodels": true,
    "search_codelists": true,
    "max_results_per_platform": 5
  }
}
```

**Response:**
```json
{
  "query": "rakennus",
  "terminology_results": [
    {"id": "concept-123", "label": "rakennus", "vocabulary": "rakymp"}
  ],
  "datamodel_results": [
    {"id": "raktkk", "name": "Rakennuksen tietomalli"}
  ],
  "codelist_results": [
    {"registry": "rakennustieto", "scheme": "rakennusluokitus"}
  ],
  "total_results": 15
}
```

### Suggest References for Documentation

Analyze text and suggest relevant standards:

```json
{
  "tool": "suggest_references",
  "arguments": {
    "text": "Järjestelmä käsittelee rakennuslupahakemuksia ja tonttijakoja. Käyttäjä voi tarkastella kaavan määräyksiä.",
    "max_suggestions": 10
  }
}
```

**Response:**
```json
{
  "suggested_vocabularies": [
    {
      "id": "rakymp",
      "name": "Rakennetun ympäristön sanasto",
      "matched_terms": ["rakennus", "tontti", "kaava"],
      "relevance_score": 0.92
    }
  ],
  "suggested_datamodels": [
    {
      "id": "rytj-kaava",
      "name": "Kaavatietomalli",
      "relevance_score": 0.85
    }
  ],
  "suggested_codelists": [
    {
      "registry": "rakennustieto",
      "scheme": "lupa-tyyppi",
      "relevance_score": 0.78
    }
  ]
}
```

### Find Code Lists for Data Model Attributes

Discover which code lists can be used with model attributes:

```json
{
  "tool": "get_codelist_for_attribute",
  "arguments": {
    "model_id": "rytj-kaava",
    "class_name": "Kaava"
  }
}
```

---

## Common Workflows

### Workflow 1: Writing a Technical Specification

1. **Search for relevant terms:**
   ```json
   {"tool": "search_terminology", "arguments": {"query": "your domain term"}}
   ```

2. **Get detailed definitions:**
   ```json
   {"tool": "get_concept_details", "arguments": {"vocabulary_id": "...", "concept_id": "..."}}
   ```

3. **Find related data models:**
   ```json
   {"tool": "search_datamodel", "arguments": {"query": "relevant model"}}
   ```

4. **Validate your document:**
   ```json
   {"tool": "validate_terminology", "arguments": {"text": "your document text"}}
   ```

### Workflow 2: Designing a Data Schema

1. **Find existing models:**
   ```json
   {"tool": "search_datamodel", "arguments": {"query": "domain"}}
   ```

2. **Get class structures:**
   ```json
   {"tool": "get_datamodel_classes", "arguments": {"model_id": "selected-model"}}
   ```

3. **Find code lists for enumerations:**
   ```json
   {"tool": "get_codelist_for_attribute", "arguments": {"model_id": "selected-model"}}
   ```

4. **Export codes for implementation:**
   ```json
   {"tool": "export_codes_csv", "arguments": {"registry": "...", "scheme": "..."}}
   ```

### Workflow 3: Quick Reference Check

Use unified search to quickly find all related resources:

```json
{
  "tool": "unified_search",
  "arguments": {
    "query": "your search term",
    "max_results_per_platform": 3
  }
}
```

---

## Tips

1. **Use vocabulary IDs** when you know which domain you're working in:
   - `rakymp` - Built environment
   - `jhka` - Public administration
   - `oksa` - Education

2. **Start with unified search** when exploring a new topic

3. **Validate your documents** before finalizing to ensure terminology consistency

4. **Export code lists** for use in dropdown menus, validation rules, etc.

5. **Check data model links** to understand how concepts relate to technical implementations
