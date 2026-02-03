# Examples

Real-world examples demonstrating how to use the Yhteentoimivuusalusta MCP Server for Finnish government and construction industry documentation.

## Table of Contents

1. [Building Permit Documentation](#building-permit-documentation)
2. [Spatial Planning (Kaavoitus)](#spatial-planning-kaavoitus)
3. [Public Administration Integration](#public-administration-integration)
4. [Education System Documentation](#education-system-documentation)
5. [Data Schema Design](#data-schema-design)
6. [Document Validation Workflow](#document-validation-workflow)

---

## Building Permit Documentation

### Scenario
Writing technical specifications for a building permit application system.

### Step 1: Find Relevant Terminology

```json
{
  "tool": "search_terminology",
  "arguments": {
    "query": "rakennuslupa",
    "vocabulary_id": "rakymp",
    "max_results": 10
  }
}
```

**Use case:** Ensure you're using the correct official term for "building permit".

### Step 2: Get Full Definition

```json
{
  "tool": "get_concept_details",
  "arguments": {
    "vocabulary_id": "rakymp",
    "concept_id": "c123",
    "include_relations": true
  }
}
```

**Result:** Get the official definition, synonyms, and related concepts like "toimenpidelupa" (action permit).

### Step 3: Find Related Code Lists

```json
{
  "tool": "search_codelist",
  "arguments": {
    "query": "rakennuslupa",
    "registry": "rakennustieto"
  }
}
```

**Use case:** Find standardized code values for permit types, building classes, etc.

### Step 4: Export Codes for Implementation

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

**Result:** CSV file ready for database seeding or dropdown population.

---

## Spatial Planning (Kaavoitus)

### Scenario
Implementing a spatial planning data exchange system.

### Step 1: Find the Kaava Data Model

```json
{
  "tool": "search_datamodel",
  "arguments": {
    "query": "kaava",
    "max_results": 5
  }
}
```

### Step 2: Explore Model Structure

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

**Result:** Complete class structure with properties like:
- `Kaava` (Plan)
- `Kaavamääräys` (Plan regulation)
- `Kaavakohde` (Plan object)

### Step 3: Find Code Lists for Plan Types

```json
{
  "tool": "get_codelist_for_attribute",
  "arguments": {
    "model_id": "rytj-kaava",
    "class_name": "Kaava"
  }
}
```

**Result:** Discover which code lists are used for plan type, status, etc.

### Step 4: Link to Terminology

```json
{
  "tool": "get_model_vocabulary_links",
  "arguments": {
    "model_id": "rytj-kaava"
  }
}
```

**Use case:** Understand the semantic meaning of each class through vocabulary links.

---

## Public Administration Integration

### Scenario
Building an integration between government systems.

### Step 1: Unified Search Across All Platforms

```json
{
  "tool": "unified_search",
  "arguments": {
    "query": "henkilötunnus",
    "search_terminologies": true,
    "search_datamodels": true,
    "search_codelists": true,
    "max_results_per_platform": 5
  }
}
```

**Result:** Find all standards related to personal identification numbers across vocabularies, data models, and code lists.

### Step 2: Find Public Admin Vocabulary

```json
{
  "tool": "list_vocabularies",
  "arguments": {
    "status": "VALID"
  }
}
```

Look for `jhka` (Julkisen hallinnon kokonaisarkkitehtuuri).

### Step 3: Search Architecture Terms

```json
{
  "tool": "search_terminology",
  "arguments": {
    "query": "rajapinta",
    "vocabulary_id": "jhka"
  }
}
```

**Use case:** Find the correct term for "API" or "interface" in government context.

---

## Education System Documentation

### Scenario
Writing specifications for an education management system.

### Step 1: Find Education Vocabulary

```json
{
  "tool": "search_terminology",
  "arguments": {
    "query": "oppilas",
    "vocabulary_id": "oksa"
  }
}
```

### Step 2: Explore Education Data Models

```json
{
  "tool": "search_datamodel",
  "arguments": {
    "query": "koulutus"
  }
}
```

### Step 3: Find Education Code Lists

```json
{
  "tool": "search_codelist",
  "arguments": {
    "query": "koulutus",
    "registry": "koulutus"
  }
}
```

### Step 4: Get Degree Classification Codes

```json
{
  "tool": "get_codes",
  "arguments": {
    "registry": "koulutus",
    "scheme": "koulutusaste",
    "max_results": 50
  }
}
```

**Result:** Official education level codes (peruskoulu, lukio, ammattikoulu, etc.)

---

## Data Schema Design

### Scenario
Designing a database schema that aligns with Finnish standards.

### Step 1: Suggest References for Your Domain

```json
{
  "tool": "suggest_references",
  "arguments": {
    "text": "Järjestelmä hallinnoi rakennusten energiatodistuksia ja niiden liitteitä. Käyttäjä voi hakea todistuksia osoitteen tai kiinteistötunnuksen perusteella.",
    "max_suggestions": 10
  }
}
```

**Result:** Automatic suggestions for:
- Relevant vocabularies (rakymp for buildings, energy terms)
- Data models (building data model)
- Code lists (energy efficiency classes)

### Step 2: Explore Suggested Data Model

```json
{
  "tool": "get_datamodel_classes",
  "arguments": {
    "model_id": "raktkk",
    "class_name": "Rakennus"
  }
}
```

### Step 3: Align Your Schema

Use the returned properties to ensure your schema uses:
- Correct field names
- Appropriate data types
- Standard code lists for enumerations

---

## Document Validation Workflow

### Scenario
Validating a technical specification document for terminology compliance.

### Step 1: Validate Full Document

```json
{
  "tool": "validate_terminology",
  "arguments": {
    "text": "Rakennuksen kerrosala lasketaan ulkoseinien ulkopintojen mukaan. Tontin pinta-ala mitataan kiinteistörekisteristä. Rakennusoikeus määräytyy asemakaavan mukaan.",
    "vocabularies": ["rakymp"],
    "suggest_corrections": true,
    "fuzzy_threshold": 0.8
  }
}
```

**Result:**
```json
{
  "valid_terms": [
    {"term": "rakennus", "vocabulary": "rakymp", "definition": "..."},
    {"term": "kerrosala", "vocabulary": "rakymp", "definition": "..."},
    {"term": "tontti", "vocabulary": "rakymp", "definition": "..."},
    {"term": "asemakaava", "vocabulary": "rakymp", "definition": "..."}
  ],
  "unknown_terms": [
    {
      "term": "rakennusoikeus",
      "suggestions": [
        {"term": "rakennusoikeus", "vocabulary": "rakymp", "score": 1.0}
      ]
    }
  ],
  "statistics": {
    "total_terms": 8,
    "valid_terms": 7,
    "unknown_terms": 1,
    "validation_rate": 0.875
  }
}
```

### Step 2: Fix Terminology Issues

Review suggestions and update document to use standardized terms.

### Step 3: Re-validate

Run validation again to confirm 100% compliance.

---

## Integration Patterns

### Pattern 1: Pre-commit Hook

Use `validate_terminology` in CI/CD to ensure documentation compliance:

```python
# validate_docs.py
import subprocess
import json

def validate_markdown_files():
    # Read all markdown files
    # Call validate_terminology for each
    # Fail build if validation_rate < 0.9
    pass
```

### Pattern 2: Real-time Suggestions

Integrate `suggest_references` into documentation editors:

```python
# As user types, periodically call:
suggest_references(text=current_paragraph)
# Show suggested standards in sidebar
```

### Pattern 3: Schema Generation

Use `get_datamodel_classes` to generate code:

```python
# Fetch model classes
classes = get_datamodel_classes(model_id="rytj-kaava")

# Generate Python dataclasses
for cls in classes:
    generate_dataclass(cls)
```

---

## Tips for Effective Use

1. **Start broad, then narrow:** Use `unified_search` first, then specific tools

2. **Cache results:** The server caches API responses - repeated queries are fast

3. **Use vocabulary IDs:** When you know your domain, specify vocabulary_id for precise results

4. **Validate iteratively:** Run validation during writing, not just at the end

5. **Export for implementation:** Use `export_codes_csv` to get data for your systems

6. **Link models to vocabularies:** Use `get_model_vocabulary_links` to understand semantic meaning
