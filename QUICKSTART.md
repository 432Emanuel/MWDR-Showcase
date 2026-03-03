# Quick Start Guide

Get MWDR Showcase running in under 10 minutes.

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git (optional, for cloning)

## Installation

### 1. Clone or Download

```bash
git clone https://github.com/[USERNAME]/MWDR-Showcase.git
cd MWDR-Showcase
```

Or download and extract the ZIP file.

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `jsonschema` - JSON Schema validation
- (Other dependencies if present)

## Run Validation

### Validate Everything

```bash
python3 src/validate/validate_json.py --path .
```

**Expected Output:**
```
Validation Summary
==================
total_files_scanned: 5
parsed_ok: 5
syntax_errors: 0
schema_valid: 5
schema_invalid: 0
schema_missing: 0

Result: PASS
```

### Validate Demo Module Only

```bash
python3 src/validate/validate_json.py --path modules/demo_module/ --json-report validate_demo.json
```

## Explore the Demo Module

```bash
ls modules/demo_module/documents/
```

Contains 5 example documents:
- `MAP-WORLD-PTOLEMY-0150.json` - Historical world map (Ptolemy)
- `MAP-REGION-WALDSEEMULLER-1507.json` - Early printed map (Waldseemüller)
- `DATA-SURVEY-GREENWICH-1851.json` - Geodetic survey campaign
- `DOC-ATLAS-ORTELIUS-1570.json` - First modern atlas (Ortelius)
- `DATASET-CLIMATE-HADLEY-2020.json` - Climate dataset (HadCRUT5)

## View Document Structure

```bash
cat modules/demo_module/documents/MAP-WORLD-PTOLEMY-0150.json
```

Each document contains:
- `type`: Document type identifier
- `id`: Unique identifier (pattern: `XXX-XXX-XXX-YYYY`)
- `title`: Document title
- `domain`: Knowledge domain (cartography, geodesy, etc.)
- `document_kind`: Type (map, survey_campaign, dataset, etc.)
- `date_range`: Temporal scope
- `provenance`: Source information
- Optional: `creators`, `region_scope`, `technical`, `claims_and_limits`, `links`, `tags`

## Troubleshooting

### Import Error: No module named 'jsonschema'

```bash
pip install jsonschema
```

The validator falls back to basic validation, but full validation requires jsonschema.

### Schema File Not Found

Check the schema routing configuration:
```bash
cat src/validate/schema_routing.json
```

Ensure schema paths exist:
```bash
ls shared/schemas/epistemic_documents/
```

### Syntax Error in JSON

Check JSON syntax:
```bash
python3 -m json.tool modules/demo_module/documents/YOUR_FILE.json
```

## Next Steps

- Read [DATA_POLICY.md](DATA_POLICY.md) for evidence status and naming conventions
- Read [CITATION.md](CITATION.md) for attribution guidelines
- Explore [REPRO_STEPS/](REPRO_STEPS/) for use cases
- Review [project_overview.json](project_overview.json) for project metadata
