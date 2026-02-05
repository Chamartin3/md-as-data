# Write Command Examples

This directory contains examples for testing the `mddata write` command with different combinations of forms, data, and schemas.

## Directory Structure

```
write_from/
├── combined/          # Form + Data + Schema examples
├── data/             # Complete data files
├── forms/            # Parameterized templates (forms)
└── schemas/          # Validation schemas
```

## Example Categories

### 1. Form + Data Examples

These examples demonstrate filling parameterized templates (forms) with data.

#### Project Documentation
```bash
# Fill project documentation form with data
mddata write --form forms/project-doc.yaml --data data/project-doc-params.json --output project-doc.md

# Or using CLI parameters
mddata write --form forms/project-doc.yaml \
  -p project_name="MyProject" \
  -p project_type="library" \
  -p version="1.0.0" \
  -p maintainer="Jane Doe" \
  --output project-doc.md
```

#### Blog Post
```bash
# Fill blog post form with data
mddata write --form forms/blog-post.yaml --data data/blog-post-params.json --output blog-post.md
```

### 2. Schema + Data Examples

These examples demonstrate validating complete data against schemas.

#### User Profile
```bash
# Validate user profile data against schema
mddata schema validate data/user-profile.json schemas/user-profile.json

# Generate markdown from validated data
mddata write --data data/user-profile.json --schema schemas/user-profile.json --output user-profile.md
```

#### Product Specification
```bash
# Validate product spec data against schema
mddata schema validate data/product-spec.yaml schemas/product-spec.yaml

# Generate markdown from validated data
mddata write --data data/product-spec.yaml --schema schemas/product-spec.yaml --output product-spec.md
```

### 3. Form + Data + Schema Examples

These examples demonstrate the complete workflow: filling a form with data and validating the result against a schema.

#### API Documentation
```bash
# Fill form with data and validate against schema
mddata write --form combined/api-doc-form.yaml \
  --data data/api-doc-params.json \
  --schema schemas/api-doc-validation.json \
  --output api-doc.md
```

#### Meeting Agenda
```bash
# Fill meeting agenda form with data and validate
mddata write --form combined/meeting-agenda-form.yaml \
  --data data/meeting-agenda-params.json \
  --schema schemas/meeting-agenda-validation.json \
  --output meeting-agenda.md
```

## Testing Scenarios

### Form Validation
Test that forms reject invalid parameter values:
```bash
# This should fail - invalid project type
mddata write --form forms/project-doc.yaml \
  -p project_name="Test" \
  -p project_type="invalid_type" \
  -p version="1.0.0" \
  -p maintainer="Test" \
  --output test.md
```

### Schema Validation
Test that schemas catch validation errors:
```bash
# Create invalid data file and test validation
echo '{"frontmatter": {"name": ""}, "sections": []}' > invalid-user.json
mddata schema validate invalid-user.json schemas/user-profile.json  # Should fail
```

### Combined Validation
Test the complete pipeline:
```bash
# Fill form, validate result, generate output
mddata write --form combined/api-doc-form.yaml \
  --data data/api-doc-params.json \
  --schema schemas/api-doc-validation.json \
  --output validated-api-doc.md
```

## Form Parameter Types

### Basic Types
- `str`: String with optional min/max length, pattern, enum validation
- `int`: Integer with optional min/max values
- `float`: Float with optional min/max values
- `bool`: Boolean value

### Complex Types
- `array`: Array with `item_type` specification
- `object`: Nested object structures

### Special Features
- **Required vs Optional**: Use `required: true/false`
- **Defaults**: Provide default values
- **Validation**: Pattern matching, enum restrictions
- **Computed Parameters**: `{date}`, `{time}`, `{env.USER}`

## Schema Validation Rules

### Frontmatter Validation
```json
{
  "field_name": {
    "type": "str",
    "required": true,
    "min": 5,
    "max": 100,
    "pattern": "^[A-Z]",
    "enum": ["value1", "value2"],
    "enum_strict": true
  }
}
```

### Section Validation
```json
{
  "section_id": {
    "validation": {
      "required": true,
      "min_blocks": 1
    }
  }
}
```

## Tips for Testing

1. **Start Simple**: Begin with basic form+data examples
2. **Test Validation**: Try invalid inputs to ensure proper error handling
3. **Combine Features**: Use all three components (form + data + schema) for comprehensive testing
4. **Edge Cases**: Test boundary conditions (min/max lengths, enum values, etc.)
5. **Error Messages**: Verify that error messages are clear and helpful

## Existing Examples

- `combined/release-notes-form.yaml`: Complex form with multiple parameter types
- `forms/simple.yaml`: Basic form with common parameter patterns
- `schemas/api-documentation.json`: Schema for API documentation validation