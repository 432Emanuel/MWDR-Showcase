# Data Policy

This document outlines the policies governing data structure, evidence status, and documentation practices in the MWDR Showcase.

## Principles

1. **Structure over Interpretation**: Document what exists, not whether it's correct
2. **Explicit Provenance**: Every data point must have traceable origins
3. **Schema Compliance**: All documents must validate against their schemas
4. **Neutral Terminology**: Avoid subjective concepts and domain-specific jargon

## Evidence Status

### Required Fields

All documents must include:

- **`provenance.source_type`**: Type of source (transcript, book, paper, archive, website, other)
- **`provenance.source_reference`**: Citation or reference to original source

### Evidence Categories

Documents may indicate evidence status through metadata:

| Status | Description | Example |
|--------|-------------|---------|
| `primary` | Direct observation or original document | Original manuscript, field notes |
| `secondary` | Analysis or synthesis of primary sources | Academic paper, historical analysis |
| `tertiary` | Compilation or summary | Textbook, encyclopedia entry |
| `unverified` | Unconfirmed claims | Speculative content, rumors |

### Claims and Limitations

Use the `claims_and_limits` field to separate stated claims from known limitations:

```json
{
  "claims_and_limits": {
    "commonly_stated_claims": [
      "First systematic use of coordinates",
      "Latitude and longitude system"
    ],
    "known_limits": [
      "Limited to Roman world knowledge",
      "Distortion in peripheral regions"
    ]
  }
}
```

## Structure vs Interpretation

### Document Structure (Required)

Structural metadata that describes the document itself:

- `id`, `title`, `type`, `domain`, `document_kind`
- `date_range`, `creators`, `region_scope`
- `provenance`, `technical` details

### Content Claims (Documented)

What the document claims to show, not validated:

```json
{
  "claims_and_limits": {
    "commonly_stated_claims": [
      "Shows the world as known in 150 CE"
    ]
  }
}
```

### Interpretation (Avoid)

Do not include interpretive judgments in structured data:

- ❌ "Ptolemy's map was inaccurate" (interpretation)
- ✅ `"known_limits": ["Limited to Roman world knowledge"]` (documented limitation)

## Naming and Path Conventions

### File Naming

**Pattern**: `{TYPE}-{SCOPE}-{IDENTIFIER}-{YEAR}.json`

- `TYPE`: Document type (MAP, DOC, DATA, etc.)
- `SCOPE`: Geographic or domain scope (WORLD, REGION, etc.)
- `IDENTIFIER`: Unique identifier (PTOLEMY, WALDSEEMULLER, etc.)
- `YEAR`: 4-digit year

**Examples**:
- `MAP-WORLD-PTOLEMY-0150.json`
- `MAP-REGION-WALDSEEMULLER-1507.json`
- `DATA-SURVEY-GREENWICH-1851.json`

### Module Naming

**Pattern**: `{domain}_{type}/`

- Lowercase with underscores
- Descriptive but concise

**Examples**:
- `modules/demo_module/`
- `modules/historical_maps/`
- `modules/scientific_datasets/`

### ID Patterns

**Document IDs**: Match file naming (without extension)

**Pattern**: `^[A-Z]+-[A-Z]+-[A-Z]+-\d{4}$`

**Examples**:
- `MAP-WORLD-PTOLEMY-0150`
- `DOC-ATLAS-ORTELIUS-1570`

## Data Provenance Tracking

### Required Provenance Fields

Every document must include:

```json
{
  "provenance": {
    "source_type": "paper|book|archive|website|other",
    "source_reference": "Full citation or URL"
  }
}
```

### Optional Provenance Fields

```json
{
  "provenance": {
    "source_type": "archive",
    "source_reference": "Library of Congress, Map Collection",
    "notes": "Digitized from microfilm"
  }
}
```

## Linking and References

### Document Links

Use the `links` array to reference related documents:

```json
{
  "links": [
    {
      "kind": "related_document",
      "target_id": "MAP-WORLD-PTOLEMY-0150",
      "note": "Preceding cartographic tradition"
    }
  ]
}
```

### Link Types

- `related_document`: Related document
- `source_node`: Source document or reference
- `marker`: Analytical marker or pattern
- `lens`: Analytical framework

## Data Quality

### Validation

All JSON documents must:
- Parse without syntax errors
- Validate against their assigned schema
- Include all required fields
- Use correct data types and formats

### Testing

Before adding new documents:

1. **Validate locally**: `python3 src/validate/validate_json.py --path modules/your_module/`
2. **Check report**: Review `validate_report.json` for errors
3. **Verify fields**: Ensure all required fields are present
4. **Test links**: Verify linked documents exist

## Data Modification

### Versioning

When updating existing documents:
- Increment version in module metadata
- Add `updated_at` timestamp
- Document changes in commit message

### Deprecation

To mark a document as deprecated:
- Add `"status": "deprecated"` to metadata
- Include `"replaced_by": "NEW_DOCUMENT_ID"` if applicable
- Do not delete; archive instead

## Compliance Checklist

Before committing new data:

- [ ] Document validates against schema
- [ ] All required fields present
- [ ] Provenance information complete
- [ ] File naming follows convention
- [ ] ID matches filename
- [ ] Links point to valid documents
- [ ] Claims separated from facts
- [ ] No subjective terminology
