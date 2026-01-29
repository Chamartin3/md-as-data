---
title: Generation Examples
description: Examples demonstrating markdown file generation from schemas and data
---

# Generation Examples

This folder contains examples demonstrating various markdown file generation scenarios using the `mddata generate` command.

## Files Overview

### Schemas

- **`blog_post_schema.json`** - JSON schema for blog post structure with defaults
- **`project_spec_schema.yaml`** - YAML schema for project specification documents

### Data Files

- **`blog_post_data.json`** - Complete blog post data matching the blog_post_schema
- **`simple_note_data.json`** - Meeting notes data (no schema validation)
- **`invalid_data.json`** - Data that intentionally doesn't match blog_post_schema

## Usage Examples

### 1. Generate Template from Schema (with defaults)

Generate a markdown template file using only a schema. The generated file will contain default values for all required properties.

```bash
# From JSON schema
mddata generate --schema blog_post_schema.json --output generated_blog_template.md

# From YAML schema
mddata generate --schema project_spec_schema.yaml --output generated_project_template.md
```

**Expected result**: Markdown files with:
- Frontmatter populated with default values
- Section structure matching the schema
- Placeholder content for each section

### 2. Generate from Data Only

Generate markdown from JSON data without schema validation.

```bash
# Generate blog post from data
mddata generate --data blog_post_data.json --output generated_blog_post.md

# Generate meeting notes from data
mddata generate --data simple_note_data.json --output generated_meeting_notes.md

# Print to stdout instead of file
mddata generate --data simple_note_data.json
```

**Expected result**: Markdown files with complete content from the data structure.

### 3. Generate from Data with Schema Validation

Generate markdown from data while validating against a schema.

```bash
# Valid data - should succeed
mddata generate \
  --data blog_post_data.json \
  --schema blog_post_schema.json \
  --output generated_validated_blog.md

# Invalid data - may show validation warnings
mddata generate \
  --data invalid_data.json \
  --schema blog_post_schema.json \
  --output generated_invalid.md
```

**Expected behavior**:
- With valid data: Generates successfully with schema validation
- With invalid data: May generate but show validation warnings/errors

### 4. Overwrite Existing Files

Force overwrite of existing files using the `--force` flag.

```bash
# Generate and overwrite if exists
mddata generate \
  --schema blog_post_schema.json \
  --output generated_blog_template.md \
  --force
```

### 5. Pipeline Usage with stdin

Generate markdown from piped JSON data.

```bash
# Pipe JSON data
cat blog_post_data.json | mddata generate --data - --output from_stdin.md

# Generate from inline JSON
echo '{
  "frontmatter": {"title": "Quick Note", "date": "2025-10-21"},
  "content": {
    "id": "", "title": "", "level": 0,
    "blocks": [{"type": "paragraph", "content": "A quick note."}],
    "children": []
  }
}' | mddata generate --data - --output inline_note.md
```

## Schema Structure

### JSON Schema Format

```json
{
  "version": "1.0.0",
  "properties": {
    "property_name": {
      "type": "str|int|bool|list|dict",
      "required": true|false,
      "default": "default_value",
      "enum": ["option1", "option2"]
    }
  },
  "sections": {
    "section_id": {
      "children": {
        "child_section_id": {}
      }
    }
  }
}
```

### YAML Schema Format

```yaml
version: "1.0.0"
properties:
  property_name:
    type: str
    required: true
    default: "default_value"
sections:
  section_id:
    children:
      child_section_id:
        children: {}
```

## Data Structure

Data files must follow the `MarkdownDataDict` format:

```json
{
  "frontmatter": {
    "property_name": "value"
  },
  "content": {
    "id": "",
    "title": "",
    "level": 0,
    "blocks": [
      {
        "type": "paragraph|list|code_block|task_list|heading",
        "content": "block content"
      }
    ],
    "children": [
      {
        "id": "section_id",
        "title": "Section Title",
        "level": 2,
        "blocks": [],
        "children": []
      }
    ]
  }
}
```

## Testing Scenarios

### Test 1: Template Generation
```bash
mddata generate --schema blog_post_schema.json --output test1_template.md
```
**Verify**: File contains default frontmatter values and empty section structure.

### Test 2: Data-Only Generation
```bash
mddata generate --data blog_post_data.json --output test2_from_data.md
```
**Verify**: File contains complete blog post with all content from JSON.

### Test 3: Validated Generation
```bash
mddata generate \
  --data blog_post_data.json \
  --schema blog_post_schema.json \
  --output test3_validated.md
```
**Verify**: File matches data, validation passes without errors.

### Test 4: Invalid Data Handling
```bash
mddata generate \
  --data invalid_data.json \
  --schema blog_post_schema.json \
  --output test4_invalid.md
```
**Verify**: Check if validation warnings/errors are displayed for type mismatches and extra fields.

### Test 5: Round-Trip Workflow
```bash
# Extract existing markdown to JSON
mddata extract json ../task_lists/project_tasks.md --output roundtrip_data.json

# Generate markdown from extracted data
mddata generate --data roundtrip_data.json --output roundtrip_recreated.md

# Compare (should be similar structure)
diff ../task_lists/project_tasks.md roundtrip_recreated.md
```

## Expected Output Files

After running the examples, you should have:

- `generated_blog_template.md` - Template from blog schema
- `generated_project_template.md` - Template from project spec schema
- `generated_blog_post.md` - Full blog post from data
- `generated_meeting_notes.md` - Meeting notes from data
- `generated_validated_blog.md` - Validated blog post
- `generated_invalid.md` - Document from invalid data (with warnings)

## Common Issues

### Issue: "Must provide either --schema or --data"
**Solution**: Provide at least one of `--schema` or `--data` flags.

### Issue: "Output file path is required when generating from schema"
**Solution**: When using `--schema` alone, always specify `--output`.

### Issue: File already exists error
**Solution**: Use `--force` flag to overwrite existing files.

### Issue: Invalid JSON format
**Solution**: Validate your JSON using `jq` or a JSON validator before using with `mddata generate`.

```bash
# Validate JSON
cat blog_post_data.json | jq empty
```

## See Also

- [CLI Reference](../../docs/CLI_REFERENCE.md#generate-commands)
- [CLAUDE.md](../../CLAUDE.md#generate-commands)
- [Schema Examples](../schemas/)
- [Task List Examples](../task_lists/)
