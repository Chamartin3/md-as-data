# Technical Documentation Use Case (Schema-based)

This example demonstrates using mddata for technical documentation with schema validation.

## Overview

This use case shows how to:
- Define a schema for technical documents (API docs, feature specs)
- Create documents with structured frontmatter and nested sections
- Allow content outside of subsections (overview sections)
- Validate documents against the schema
- Update existing documents while maintaining structure

## Files in this example

- `schema.json` - JSON schema defining the document structure
- `sample_valid.md` - Example valid document
- `sample_data.json` - Data for creating new documents
- `sample_invalid.json` - Invalid data to test validation

## Document Structure

Technical documents in this example have:

### Frontmatter
- `title` (required string)
- `version` (required string, pattern: semver)
- `date` (required string, ISO date format)
- `author` (required string)
- `status` (enum: draft, review, published)
- `tags` (array of strings)

### Sections
- **Overview** (content allowed outside subsections)
- **API Reference**
  - **Endpoints**
  - **Authentication**
  - **Rate Limiting**
- **Examples**
  - **Basic Usage**
  - **Advanced Usage**
- **Changelog**

## Step-by-step Usage

### 1. Generate Schema from Sample Document

```bash
# Generate schema from the sample document
mddata schema infer sample_valid.md --output schema.json

# View the generated schema
mddata schema info schema.json
```

### 2. Create New Document from Data

```bash
# Create a new document using data and schema validation
mddata write --data sample_data.json --schema schema.json --output new_api_doc.md

# Verify the created document structure
mddata info summary new_api_doc.md
```

### 3. Validate Documents

```bash
# Validate existing document against schema
mddata schema validate sample_valid.md schema.json

# Test with invalid data (should fail)
mddata write --data sample_invalid.json --schema schema.json --output invalid_doc.md
```

### 4. Update Existing Documents

```bash
# Update document properties
mddata write set-property sample_valid.md version "2.1.0"
mddata write set-property sample_valid.md status "published"

# Add new section
mddata write set-section sample_valid.md "troubleshooting" "## Common Issues\\n\\nList common problems here."

# Update existing section content
mddata write set-section sample_valid.md "overview" "Updated API overview content." --policy replace
```

### 5. Extract Data

```bash
# Extract to JSON for processing
mddata extract json sample_valid.md --pretty --output extracted.json

# Extract only frontmatter
mddata extract frontmatter sample_valid.md --format yaml
```

### 6. Query Document Structure

```bash
# View document sections
mddata info sections sample_valid.md

# View all content blocks
mddata info blocks sample_valid.md

# Check frontmatter properties
mddata info properties sample_valid.md
```

## Key Features Demonstrated

1. **Schema Validation**: Documents are validated against a defined structure
2. **Mixed Content**: Allows content both in subsections and at the root level
3. **Structured Frontmatter**: Rich metadata with validation rules
4. **Nested Sections**: Hierarchical organization with clear structure
5. **Date Handling**: Proper ISO date formatting and validation
6. **Enumeration**: Controlled vocabularies for status fields
7. **Arrays**: Lists of tags with proper validation