# Technical Documentation — Schema-based

Schema-validated API/spec/dev-guide documents.

## Files

- `schema.json` — document schema
- `sample_valid.md` — valid example
- `sample_data.json` — data for generation
- `sample_invalid.json` — data that fails validation

## Document shape

**Frontmatter:** `title`, `version` (semver), `date`, `author`, `status` (draft/review/published), `tags`.

**Sections:** Overview, API Reference (Endpoints, Authentication, Rate Limiting), Examples (Basic, Advanced), Changelog.

## Run

```bash
# Generate schema from a known-good doc
mddata schema infer sample_valid.md --output schema.json
mddata schema info schema.json

# Create new doc from data + validate
mddata write --data sample_data.json --schema schema.json --output new_api_doc.md

# Validate existing
mddata schema validate sample_valid.md schema.json

# Invalid data — should fail
mddata write --data sample_invalid.json --schema schema.json --output invalid.md

# Update properties / sections
mddata write set-property sample_valid.md version 2.1.0
mddata write set-property sample_valid.md status published
mddata write set-section sample_valid.md overview "Updated overview." --policy replace

# Extract
mddata extract json sample_valid.md --pretty --output extracted.json
mddata extract frontmatter sample_valid.md --format yaml
```
