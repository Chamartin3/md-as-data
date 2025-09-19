# Example Validation Schemas

This folder contains example schemas generated from the markdown files in the `examples/` directory.

## Schema Files

### Permissive Schemas (Flexible)
- `minimal_permissive.json` - Basic schema with minimal constraints
- `simple_permissive.json` - Simple document schema
- `complex_permissive.json` - Complex document schema (3.4KB)

### Strict Schemas (Exact)
- `minimal_strict.json` - Minimal schema with exact constraints
- `simple_strict.json` - Simple document with exact structure (6.9KB)
- `complex_strict.json` - Complex document with full validation (21KB)

## Permissive vs Strict Mode

### Permissive Mode
- **Frontmatter**: Only validates types and required fields
- **Sections**: No validation constraints (omitted entirely)
- **Use case**: Flexible documents where structure can vary

Example:
```json
{
  "properties": {
    "title": {
      "type": "str",
      "required": true
    }
  },
  "sections": {
    "introduction": {}
  }
}
```

### Strict Mode
- **Frontmatter**: Includes default values, min/max length, pattern validation
- **Sections**: Enforces exact block counts and allowed content types
- **Use case**: Strict templates where structure must match exactly

Example:
```json
{
  "properties": {
    "title": {
      "type": "str",
      "required": true,
      "default": "Document Title",
      "validations": [
        {
          "type": "min_length",
          "value": 1,
          "message": "Value must not be empty"
        }
      ]
    }
  },
  "sections": {
    "introduction": {
      "validation": {
        "required": false,
        "min_blocks": 2,
        "max_blocks": 2,
        "allowed_content": ["BlockType.PARAGRAPH"]
      }
    }
  }
}
```

## Usage Examples

### Generate schemas
```bash
# Permissive mode (default)
uv run mdasdata examples/simple.md schema generate --output my_schema.json

# Strict mode
uv run mdasdata examples/complex.md schema generate \
  --inference-mode strict \
  --output strict_schema.json
```

### Validate documents
```bash
# Validate against permissive schema
uv run mdasdata my_document.md schema validate \
  examples/schemas/simple_permissive.json

# Validate against strict schema
uv run mdasdata my_document.md schema validate \
  examples/schemas/complex_strict.json --verbose
```

### View schema information
```bash
uv run mdasdata examples/simple.md schema info \
  examples/schemas/simple_permissive.json
```

## Testing

These schemas are useful for testing validation functionality:

```bash
# Test that valid documents pass
uv run mdasdata examples/complex.md schema validate \
  examples/schemas/complex_permissive.json

# Test strict validation
uv run mdasdata examples/complex.md schema validate \
  examples/schemas/complex_strict.json
```
