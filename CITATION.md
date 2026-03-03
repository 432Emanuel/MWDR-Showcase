# Citation Guidelines

This document explains how to cite the MWDR Showcase repository and its contents.

## Repository Citation

### Basic Citation Format

```bibtex
@misc{mwdr_showcase_2026,
  title = {MWDR Showcase: Modular Research Data Repository},
  author = {{MWDR Contributors}},
  year = {2026},
  version = {0.2.0},
  url = {https://github.com/[USERNAME]/MWDR-Showcase},
  license = {MIT License / CC BY 4.0}
}
```

### APA Style

MWDR Contributors. (2026). *MWDR Showcase: Modular Research Data Repository* (Version 0.2.0) [Computer software]. GitHub. https://github.com/[USERNAME]/MWDR-Showcase

### Chicago Style

MWDR Contributors. 2026. "MWDR Showcase: Modular Research Data Repository." Version 0.2.0. GitHub. https://github.com/[USERNAME]/MWDR-Showcase.

## Document Citation

### Individual Documents

When citing specific documents from the demo module:

```bibtex
@misc{mwdr_ptolemy_2026,
  title = {Geographia (MAP-WORLD-PTOLEMY-0150)},
  author = {{MWDR Contributors}},
  year = {2026},
  howpublished = {MWDR Showcase Repository},
  url = {https://github.com/[USERNAME]/MWDR-Showcase/blob/main/modules/demo_module/documents/MAP-WORLD-PTOLEMY-0150.json}
}
```

### In-Text Citation

> The early coordinate system demonstrated in Ptolemy's *Geographia* (MWDR Showcase, 2026) represents...

## License and Attribution

### Code License

**MIT License**

The validation scripts, tooling, and infrastructure code are licensed under the MIT License. You may:

- Use the code for any purpose
- Modify the code
- Distribute the code
- Sublicense the code

**Requirement**: Include the MIT License text and copyright notice.

### Content License

**Creative Commons Attribution 4.0 International (CC BY 4.0)**

The data documents, schemas, and documentation are licensed under CC BY 4.0. You may:

- Share the material
- Adapt the material

**Requirement**: Provide appropriate attribution and indicate if changes were made.

### Attribution Statement

When using data or documents from this repository, include:

```
Source: MWDR Showcase (2026). https://github.com/[USERNAME]/MWDR-Showcase
Retrieved: [DATE]
License: CC BY 4.0
```

## Modifying and Deriving

### Modified Documents

When modifying documents from this repository:

1. **Retain original ID**: Keep the original `id` field
2. **Add modification info**: Include `modified_at` and `modified_by` fields
3. **Cite original**: Reference the original document in `provenance`

```json
{
  "id": "MAP-WORLD-PTOLEMY-0150",
  "provenance": {
    "source_type": "derivative",
    "source_reference": "Modified from MWDR Showcase MAP-WORLD-PTOLEMY-0150",
    "modified_at": "2026-03-03",
    "modifications": ["Added regional details", "Updated coastline"]
  }
}
```

### Derived Works

When creating new documents inspired by this repository:

1. **Use different IDs**: Create new unique identifiers
2. **Cite inspiration**: Reference inspiring documents in `links`
3. **Follow schema**: Use compatible schema structure

## Source Attribution

### Original Sources

Documents in the demo module reference historical sources. When using these documents, also cite the original sources where applicable:

```json
{
  "provenance": {
    "source_type": "book",
    "source_reference": "Ptolemy, C. (150 CE). Geographia"
  }
}
```

When citing, include both:

```
Source document: Ptolemy, C. (150 CE). *Geographia*.
Structured representation: MWDR Showcase MAP-WORLD-PTOLEMY-0150 (2026).
```

## Contact and Questions

For questions about citation, licensing, or attribution:

- Open an issue on GitHub
- Contact repository maintainers
- Review license files: [LICENSE](LICENSE)

## Versioning

When citing this repository, always include:

- **Version number**: e.g., 0.2.0
- **Retrieval date**: When you accessed the repository
- **Commit hash** (optional): For specific reproducibility

Example:
```
MWDR Showcase v0.2.0 (commit abc123), retrieved 2026-03-03
```
