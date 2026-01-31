# mddata User Manual

Welcome to the complete user manual for `mddata` - a command-line tool that treats markdown files as structured data objects.

## Table of Contents

1. **[Installation & Verification](01-installation-verification.md)**
   - Installing mddata
   - Verifying installation
   - Understanding core concepts: properties, sections, and blocks
   - Document structure representation

2. **[Querying Metadata](02-querying-metadata.md)**
   - Using `mddata info` commands
   - Inspecting document structure
   - Querying properties, sections, and blocks
   - Understanding section IDs and paths
   - Task list management

3. **[Extracting Metadata](03-extracting-metadata.md)**
   - Exporting to JSON and YAML formats
   - Understanding the MarkdownDataDict structure
   - Extracting full documents vs. frontmatter only
   - Working with extracted data (jq, yq, scripts)
   - Integration patterns

4. **[Schema Management](04-schema-management.md)**
   - Understanding schema structure
   - Generating schemas from documents
   - Multi-file schema generation and merging
   - Validating documents against schemas
   - Schema inference modes (permissive vs. strict)
   - Inspection and debugging

5. **[Markdown Generation](05-markdown-generation.md)**
   - Generating markdown from JSON data
   - Creating templates from schemas
   - Combined generation with validation
   - Understanding the MarkdownDataDict format
   - Block types reference
   - Round-trip workflows

6. **[Data Transformation](06-data-transformation.md)**
   - Modifying frontmatter properties
   - Updating section content
   - Section policies (update, replace, append)
   - Creating new sections and subsections
   - Path-based section access
   - Common transformation patterns

7. **[Complex Data Transformations](07-complex-transformations.md)**
   - Bulk operations with `mddata modify from-json`
   - Adding complete subsections from templates
   - Programmatic transformation generation
   - Pipeline integration patterns
   - Multi-stage workflows
   - Best practices and error handling

## Quick Start

### Installation

```bash
uv sync --dev
```

### Basic Usage

```bash
# Check version
mddata --version

# Get document info
mddata info summary document.md

# Extract to JSON
mddata extract json document.md --pretty

# Generate schema
mddata schema generate document.md --output schema.json

# Validate document
mddata schema validate document.md schema.json

# Modify property
mddata modify set-property document.md status "published"

# Generate markdown
mddata generate --data data.json --output document.md
```

## Common Workflows

### Documentation Pipeline

```bash
# 1. Generate schema from template
mddata schema generate template.md --mode strict --output doc-schema.json

# 2. Create new document from schema
mddata generate --schema doc-schema.json --output new-doc.md

# 3. Edit document (manually)
# ... edit new-doc.md ...

# 4. Validate against schema
mddata schema validate new-doc.md doc-schema.json

# 5. Extract for publishing
mddata extract json new-doc.md --pretty --output published.json
```

### Content Management

```bash
# 1. Query current state
mddata info summary article.md --verbose

# 2. Update metadata
mddata modify set-property article.md status "published"
mddata modify set-property article.md publish_date "2025-10-23"

# 3. Update content
mddata modify set-section article.md introduction "Updated introduction text."

# 4. Verify changes
mddata info properties article.md
```

### Bulk Transformations

```bash
# 1. Extract current state
mddata extract json document.md --pretty --output current.json

# 2. Create transformation
cat > transform.json << 'EOF'
{
  "frontmatter": {
    "version": 2.0,
    "updated": "2025-10-23"
  },
  "sections": [
    {
      "id": "changelog",
      "content": "## v2.0 - Updates applied",
      "policy": "append"
    }
  ]
}
EOF

# 3. Apply transformation
mddata modify from-json document.md transform.json

# 4. Validate result
mddata schema validate document.md schema.json
```

### Schema-Driven Development

```bash
# 1. Generate schema from existing docs
mddata schema generate ./docs/ --output docs-schema.json --pretty

# 2. Create template
mddata generate --schema docs-schema.json --output template.md

# 3. Validate all documents
for doc in docs/**/*.md; do
  mddata schema validate "$doc" docs-schema.json
done
```

## Integration Examples

### CI/CD Pipeline

```yaml
# .github/workflows/validate-docs.yml
name: Validate Documentation
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install mddata
        run: uv sync --dev
      - name: Validate documentation
        run: |
          for doc in docs/**/*.md; do
            mddata schema validate "$doc" docs/schema.json
          done
```

### Build Script

```bash
#!/bin/bash
# build-docs.sh

echo "Building documentation..."

# Generate schemas
mddata schema generate docs/templates/ --output build/schema.json

# Generate docs from data
for data_file in data/*.json; do
  output="build/$(basename ${data_file%.json}).md"
  mddata generate --data "$data_file" --schema build/schema.json --output "$output"
done

# Extract for API
for doc in build/*.md; do
  mddata extract json "$doc" --pretty --output "api/$(basename ${doc%.md}).json"
done

echo "Build complete!"
```

### Python Integration

```python
#!/usr/bin/env python3
import subprocess
import json
from pathlib import Path

def update_document(doc_path, updates):
    """Update markdown document with Python dict."""
    transform = {
        "frontmatter": updates.get("frontmatter", {}),
        "sections": updates.get("sections", [])
    }

    # Apply transformation
    proc = subprocess.run(
        ["mddata", "modify", "from-json", doc_path, "-"],
        input=json.dumps(transform),
        text=True,
        capture_output=True
    )

    if proc.returncode != 0:
        raise Exception(f"Update failed: {proc.stderr}")

# Usage
updates = {
    "frontmatter": {
        "version": 2.0,
        "status": "published"
    },
    "sections": [
        {
            "id": "changelog",
            "content": "## v2.0\n- Updated",
            "policy": "append"
        }
    ]
}

update_document("document.md", updates)
```

## Command Reference

### Info Commands

| Command | Description |
|---------|-------------|
| `info summary <file>` | Document overview |
| `info properties <file>` | List frontmatter properties |
| `info sections <file>` | Show section hierarchy |
| `info blocks <file>` | List content blocks |
| `info tasks <file>` | Display task lists |

### Extract Commands

| Command | Description |
|---------|-------------|
| `extract json <file>` | Export as JSON |
| `extract yaml <file>` | Export as YAML |
| `extract frontmatter <file>` | Export frontmatter only |

### Schema Commands

| Command | Description |
|---------|-------------|
| `schema generate <source>` | Generate schema |
| `schema validate <file> <schema>` | Validate document |
| `schema info <schema>` | Display schema info |

### Generate Commands

| Command | Description |
|---------|-------------|
| `generate --data <file>` | Generate from JSON data |
| `generate --schema <file>` | Generate template from schema |
| `generate --data <data> --schema <schema>` | Generate with validation |

### Modify Commands

| Command | Description |
|---------|-------------|
| `modify set-property <file> <name> <value>` | Set property |
| `modify remove-property <file> <name>` | Remove property |
| `modify set-section <file> <id> <content>` | Update section |
| `modify from-json <file> <json>` | Bulk transformation |

## Getting Help

### Command Help

```bash
# General help
mddata --help

# Command-specific help
mddata info --help
mddata extract --help
mddata schema --help
mddata generate --help
mddata modify --help

# Subcommand help
mddata info sections --help
mddata schema generate --help
```

### Documentation

- **This manual**: Comprehensive guide to all features
- **CLI Reference**: Detailed command documentation
- **CLAUDE.md**: Project architecture and development guide
- **README.md**: Quick start and overview

### Support

For issues, questions, or contributions:
- GitHub Issues: [Report bugs or request features]
- Documentation: Read through manual sections
- Examples: Check `examples/` directory

## Best Practices

### 1. Version Control

Always use version control when modifying documents:
```bash
git commit -am "Before modifications"
mddata modify set-property doc.md status "published"
git diff doc.md
```

### 2. Schema Validation

Validate documents against schemas to ensure consistency:
```bash
mddata schema generate template.md --output schema.json
mddata schema validate document.md schema.json
```

### 3. Dry Run

Preview changes before applying:
```bash
mddata modify from-json doc.md changes.json --dry-run
```

### 4. Backup Strategy

Backup before bulk operations:
```bash
cp document.md document.backup.md
mddata modify from-json document.md transform.json
```

### 5. Incremental Changes

Break complex transformations into smaller steps:
```bash
mddata modify from-json doc.md step1.json
mddata modify from-json doc.md step2.json
mddata modify from-json doc.md step3.json
```

## Common Patterns

### Update-Validate-Extract

```bash
# Update document
mddata modify set-property doc.md version 2.0

# Validate
mddata schema validate doc.md schema.json

# Extract
mddata extract json doc.md --pretty --output updated.json
```

### Generate-Validate-Publish

```bash
# Generate from data
mddata generate --data content.json --schema schema.json --output doc.md

# Validate
mddata schema validate doc.md schema.json

# Extract for publishing
mddata extract json doc.md --output published.json
```

### Extract-Transform-Apply

```bash
# Extract current state
mddata extract json source.md --output current.json

# Transform with external tool
jq '.frontmatter.version = 2.0' current.json > updated.json

# Generate new document
mddata generate --data updated.json --output target.md
```

## Next Steps

Start with the basics:
1. Read [Installation & Verification](01-installation-verification.md) to understand core concepts
2. Learn [Querying Metadata](02-querying-metadata.md) to inspect documents
3. Practice [Extracting Metadata](03-extracting-metadata.md) to export data
4. Explore [Schema Management](04-schema-management.md) for validation
5. Master [Data Transformation](06-data-transformation.md) for modifications
6. Advance to [Complex Transformations](07-complex-transformations.md) for sophisticated workflows

Happy documenting! 📝
