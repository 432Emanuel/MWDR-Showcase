# MWDR Showcase

**Modular Research Data Repository Showcase**

A technical demonstration of modular research data structures, JSON validation patterns, and schema-based documentation systems.

## Overview

This showcase demonstrates a systematic approach to managing structured research data with:

- **Schema-based validation**: JSON documents validated against typed schemas
- **Modular architecture**: Self-contained modules with clear interfaces
- **CI/CD integration**: Automated validation on every commit
- **Documentation patterns**: Clear separation of structure, interpretation, and provenance

## Project Structure

```
MWDR-Showcase/
├── .github/workflows/     # CI/CD pipeline for validation
├── modules/demo_module/   # Demonstration module with example documents
│   ├── index.json         # Module metadata
│   └── documents/         # Example epistemic documents
├── shared/schemas/        # JSON schema definitions
├── src/validate/          # Validation scripts and routing config
├── REPRO_STEPS/           # Reproducible use case instructions
├── project_overview.json  # Project metadata and structure
└── README.md, QUICKSTART.md, DATA_POLICY.md, CITATION.md
```

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run validation locally:**
   ```bash
   python3 src/validate/validate_json.py --path .
   ```

3. **Expected output:**
   ```
   Validation Summary
   ==================
   total_files_scanned: 5
   parsed_ok: 5
   syntax_errors: 0
   schema_valid: 5
   schema_invalid: 0
   Result: PASS
   ```

## Key Features

### Schema-Based Validation

All JSON documents are validated against schemas defined in `shared/schemas/`. The validation system uses:

- **Schema routing**: File patterns mapped to specific schemas
- **Strict typing**: Required fields, value constraints, and patterns
- **Automated CI**: GitHub Actions workflow validates every push

### Demo Module

The `modules/demo_module/` directory contains example documents demonstrating:

- Epistemic documents (maps, surveys, datasets)
- Metadata provenance tracking
- Temporal and geographic scoping
- Document relationships and links

### Documentation

- **[README.md](README.md)**: Project overview and structure
- **[QUICKSTART.md](QUICKSTART.md)**: Get running in <10 minutes
- **[DATA_POLICY.md](DATA_POLICY.md)**: Evidence status and naming conventions
- **[CITATION.md](CITATION.md)**: Attribution guidelines
- **[REPRO_STEPS/](REPRO_STEPS/)**: Step-by-step use cases

## Use Cases

1. **UC-01**: Validate JSON structure and schema compliance
2. **UC-02**: Add a new document to the demo module
3. **UC-03**: Create a new module with custom schema

See [REPRO_STEPS/](REPRO_STEPS/) for detailed instructions.

## Technical Details

### Validation System

The validation system (`src/validate/validate_json.py`) supports:

- **Schema routing**: Pattern-based schema selection
- **JSON Schema compliance**: Full JSON Schema validation
- **Detailed reporting**: Syntax errors, schema validation, missing schemas
- **Fallback validation**: Basic validation without jsonschema library

### Schema Routing Configuration

File patterns are mapped to schemas in `src/validate/schema_routing.json`:

```json
{
  "version": "1.0",
  "rules": [
    {
      "glob": "modules/demo_module/documents/*.json",
      "schema": "shared/schemas/epistemic_documents/epistemic_document.schema.json",
      "comment": "Demo module epistemic documents"
    }
  ]
}
```

## License

- **Code**: MIT License
- **Content**: Creative Commons Attribution 4.0 International (CC BY 4.0)

## Repository

- **URL**: https://github.com/[USERNAME]/MWDR-Showcase (placeholder)
- **Version**: 0.2.0
- **Last Updated**: 2026-03-03
