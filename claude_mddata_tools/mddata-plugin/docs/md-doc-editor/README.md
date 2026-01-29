# Markdown Document Editor Agent

A Claude Code agent specializing in markdown document editing and manipulation using the mddata CLI tool.

## Agent Name

`markdown-doc-editor`

## Specializations

- **Nested Data Editing**: Navigate and edit deeply nested sections and frontmatter properties
- **Document Creation**: Create new documents from schemas or structured data
- **Content Verification**: Always verify changes before and after operations
- **Schema Validation**: Ensure structural integrity with comprehensive validation

## Core Capabilities

### 1. Document Inspection
- Inspect document structure and metadata
- Query sections and blocks with filters
- Extract data in JSON/YAML formats

### 2. Nested Data Editing
- Edit deeply nested sections using dot-path notation (`api.endpoints.users`)
- Modify nested frontmatter properties
- Preserve or replace subsections with policy controls

### 3. Document Creation
- **From Schema**: Generate template documents from schema definitions
- **From Data**: Render markdown from structured JSON/YAML data
- **With Validation**: Create documents with automatic schema validation

### 4. Verification Workflows
- Inspect-Edit-Verify pattern for all operations
- Before/after comparisons
- Schema validation after changes
- Diff-based verification for complex edits

## Usage Examples

### Edit Nested Section with Verification

```bash
# Inspect current state
mddata info sections doc.md --paths

# Edit nested section
mddata modify set-section doc.md api.endpoints.users "## Users Endpoint..." --policy update

# Verify change
mddata info blocks doc.md --section api.endpoints.users
```

### Create Document from Schema

```bash
# Generate schema from template
mddata schema infer template.md --output schema.json --pretty

# Create new document
mddata render --schema schema.json --output new-doc.md

# Verify and validate
mddata info summary new-doc.md --verbose
mddata schema validate new-doc.md schema.json --verbose
```

### Create Document from Data

```bash
# Prepare structured data
cat > content.json <<'DATA'
{
  "frontmatter": {
    "title": "API Documentation",
    "version": "1.0"
  },
  "content": {
    "sections": [
      {
        "id": "introduction",
        "title": "Introduction",
        "level": 2,
        "blocks": [...]
      }
    ]
  }
}
DATA

# Render markdown
mddata render --data content.json --output api-doc.md

# Verify creation
mddata info summary api-doc.md --verbose
```

## Section Modification Policies

- **`update`** (default): Merge content while preserving subsections
- **`replace`**: Replace entire section content (removes subsections)
- **`append`**: Add content to end of existing section

## Verification Strategies

1. **Quick Verification**: `mddata info summary doc.md --verbose`
2. **Section Verification**: `mddata info blocks doc.md --section <path>`
3. **Property Verification**: `mddata extract frontmatter doc.md --format json`
4. **Schema Validation**: `mddata schema validate doc.md schema.json --verbose`
5. **Diff Verification**: Extract before/after, compare with `diff`

## Available Tools

- `Bash`: Execute mddata commands
- `Bash(mddata:*)`: Pre-approved mddata operations
- `Read`: Read markdown files and schemas
- `Write`: Create new documents
- `Edit`: Modify existing documents

## Files

- `AGENT.md`: Complete agent definition and system prompt
- `transformation-guide.md`: Basic transformation patterns (legacy)
- `advanced-guide.md`: Complex transformation workflows (legacy)
- `README.md`: This file

## Best Practices

1. Always verify before and after changes
2. Inspect structure before editing
3. Use schema validation for integrity
4. Test with dry-run for bulk changes
5. Leverage creation commands for new documents
6. Use appropriate policies for section edits
7. Provide clear verification proof to users

## Related Resources

- [mddata CLI Reference](../../docs/CLI_REFERENCE.md)
- [mddata README](../../README.md)
- [Claude Code Tools](../README.md)
