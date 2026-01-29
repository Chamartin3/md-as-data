# Complex Data Transformations

## Overview

The `mddata modify from-json` command enables sophisticated bulk transformations by applying multiple changes from a single JSON specification. This is ideal for:
- **Batch updates** - Apply many changes at once
- **Template-based additions** - Add complete subsections
- **Scripted workflows** - Programmatic document manipulation
- **Complex restructuring** - Coordinated multi-part changes

## Command Structure

```bash
mddata modify from-json <file_path> <json_source> [options]
```

**Arguments:**
- `file_path` - Target markdown document
- `json_source` - JSON file path or `-` for stdin
- `--dry-run` - Preview changes without applying

## Transformation Format

JSON transformation specifications follow this structure:

```json
{
  "frontmatter": {
    "property_name": "new_value",
    "another_property": 42,
    "complex_value": {"key": "value"}
  },
  "sections": [
    {
      "id": "section_id",
      "content": "New section content",
      "policy": "update"
    },
    {
      "id": "parent.new_subsection",
      "content": "Complete new subsection",
      "policy": "update"
    }
  ]
}
```

### Frontmatter Changes

All properties in the `frontmatter` object will be set:

```json
{
  "frontmatter": {
    "title": "Updated Title",
    "version": 2.0,
    "status": "published",
    "tags": ["updated", "v2"],
    "metadata": {
      "author": "John Doe",
      "date": "2025-10-23"
    }
  }
}
```

**Behavior:**
- Properties are created or updated
- Existing properties not mentioned are preserved
- Values can be any valid JSON type
- To remove a property, use `null` value (see below)

### Section Changes

Each section change specifies:

```json
{
  "id": "section_path",           // Required: section identifier or path
  "content": "Section content",   // Required: new content
  "policy": "update"              // Optional: update|replace|append (default: update)
}
```

**Policy options:**
- `update` (default) - Replace content, preserve subsections
- `replace` - Replace entire section including subsections
- `append` - Add content to end

## Basic Examples

### Example 1: Simple Bulk Update

**Transform file (changes.json):**
```json
{
  "frontmatter": {
    "version": 2.0,
    "status": "published",
    "last_updated": "2025-10-23"
  },
  "sections": [
    {
      "id": "introduction",
      "content": "Welcome to version 2.0 of our documentation.",
      "policy": "update"
    }
  ]
}
```

**Apply changes:**
```bash
mddata modify from-json document.md changes.json
```

### Example 2: From stdin

```bash
cat changes.json | mddata modify from-json document.md -
```

```bash
echo '{"frontmatter": {"status": "draft"}}' | mddata modify from-json document.md -
```

### Example 3: Dry Run Preview

```bash
mddata modify from-json document.md changes.json --dry-run
```

**Output:**
```
Dry run mode: No changes will be applied

Frontmatter changes (3):
  version: 1.0 → 2.0
  status: "draft" → "published"
  last_updated: (new) → "2025-10-23"

Section changes (1):
  introduction:
    Policy: update
    Content preview: "Welcome to version 2.0 of..."

No changes applied (dry run mode)
```

## Adding Complete Subsections

Create entire new subsections with full content:

### Example 4: Add New Feature Section

**Transform (add-feature.json):**
```json
{
  "frontmatter": {
    "features": ["auth", "api", "webhooks"]
  },
  "sections": [
    {
      "id": "features.webhooks",
      "content": "# Webhooks\n\nWebhooks allow real-time notifications.\n\n## Configuration\n\nConfigure webhooks in settings.\n\n## Events\n\nAvailable events:\n- user.created\n- user.updated\n- user.deleted",
      "policy": "update"
    }
  ]
}
```

**Apply:**
```bash
mddata modify from-json document.md add-feature.json
```

**Result structure:**
```markdown
---
features: ["auth", "api", "webhooks"]
---

# Features

## Webhooks

Webhooks allow real-time notifications.

### Configuration

Configure webhooks in settings.

### Events

Available events:
- user.created
- user.updated
- user.deleted
```

**Note:** The content includes heading markup, which gets parsed and creates proper subsections.

### Example 5: Template-Based Section Addition

**Template data (api-section.json):**
```json
{
  "sections": [
    {
      "id": "api_reference",
      "content": "Complete API reference documentation.",
      "policy": "update"
    },
    {
      "id": "api_reference.authentication",
      "content": "## Authentication\n\nAll requests require authentication.\n\n### API Keys\n\nGenerate API keys in the dashboard.\n\n```bash\ncurl -H \"Authorization: Bearer YOUR_TOKEN\" https://api.example.com\n```",
      "policy": "update"
    },
    {
      "id": "api_reference.endpoints",
      "content": "## Endpoints\n\n### Users\n\n- GET /users - List users\n- POST /users - Create user\n- GET /users/:id - Get user\n\n### Projects\n\n- GET /projects - List projects\n- POST /projects - Create project",
      "policy": "update"
    }
  ]
}
```

**Apply:**
```bash
mddata modify from-json document.md api-section.json
```

**Result:** Complete API reference section with authentication and endpoints subsections.

## Advanced Transformations

### Example 6: Coordinated Updates

**Migration transform (migrate-v2.json):**
```json
{
  "frontmatter": {
    "schema_version": 2.0,
    "migrated_at": "2025-10-23T10:30:00Z",
    "deprecated_field": null,
    "new_config": {
      "enabled": true,
      "mode": "production"
    }
  },
  "sections": [
    {
      "id": "migration_notes",
      "content": "## Migration to v2.0\n\nThis document was migrated on 2025-10-23.\n\n### Changes\n\n- Updated schema to v2.0\n- Removed deprecated fields\n- Added new configuration",
      "policy": "update"
    },
    {
      "id": "changelog",
      "content": "## v2.0 - 2025-10-23\n\n- Migrated to new schema\n- Enhanced configuration options",
      "policy": "append"
    }
  ]
}
```

**Apply:**
```bash
mddata modify from-json document.md migrate-v2.json
```

**Result:**
- Schema version updated
- Migration timestamp added
- Deprecated field removed (null value)
- New config added
- Migration notes section created
- Changelog appended

### Example 7: Content Restructuring

**Restructure (reorganize.json):**
```json
{
  "frontmatter": {
    "restructured": true,
    "structure_version": "2025-10-23"
  },
  "sections": [
    {
      "id": "getting_started",
      "content": "Everything you need to get started quickly.",
      "policy": "update"
    },
    {
      "id": "getting_started.installation",
      "content": "## Installation\n\n```bash\nnpm install package-name\n```",
      "policy": "update"
    },
    {
      "id": "getting_started.quick_start",
      "content": "## Quick Start\n\n1. Install the package\n2. Configure settings\n3. Run your first command",
      "policy": "update"
    },
    {
      "id": "getting_started.examples",
      "content": "## Examples\n\nSee the examples directory for sample projects.",
      "policy": "update"
    }
  ]
}
```

**Apply:**
```bash
mddata modify from-json document.md reorganize.json
```

**Result:** Complete new "Getting Started" section with three subsections.

## Programmatic Generation

### Example 8: Script-Generated Transformations

**Python script (generate-updates.py):**
```python
#!/usr/bin/env python3
import json
import sys
from datetime import datetime

# Build transformation
transform = {
    "frontmatter": {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "build_number": 42,
        "status": "automated"
    },
    "sections": []
}

# Add sections programmatically
features = ["authentication", "authorization", "logging"]
for feature in features:
    transform["sections"].append({
        "id": f"features.{feature}",
        "content": f"## {feature.title()}\n\nDocumentation for {feature}.",
        "policy": "update"
    })

# Output JSON
print(json.dumps(transform, indent=2))
```

**Usage:**
```bash
python generate-updates.py | mddata modify from-json document.md -
```

### Example 9: Dynamic Content Injection

**JavaScript (inject-api-docs.js):**
```javascript
#!/usr/bin/env node
const fs = require('fs');

// Read API spec
const apiSpec = JSON.parse(fs.readFileSync('api-spec.json', 'utf8'));

// Build transformation
const transform = {
  frontmatter: {
    api_version: apiSpec.version,
    last_generated: new Date().toISOString()
  },
  sections: []
};

// Generate endpoint sections
apiSpec.endpoints.forEach(endpoint => {
  const sectionId = `api.${endpoint.name.toLowerCase().replace(/\s+/g, '_')}`;
  const content = `
## ${endpoint.name}

**${endpoint.method}** \`${endpoint.path}\`

${endpoint.description}

### Parameters

${endpoint.parameters.map(p => `- \`${p.name}\` (${p.type}): ${p.description}`).join('\n')}

### Response

\`\`\`json
${JSON.stringify(endpoint.example_response, null, 2)}
\`\`\`
`.trim();

  transform.sections.push({
    id: sectionId,
    content: content,
    policy: 'update'
  });
});

// Output
console.log(JSON.stringify(transform, null, 2));
```

**Usage:**
```bash
node inject-api-docs.js | mddata modify from-json api-reference.md -
```

## Pipeline Integration

### Example 10: Multi-Stage Pipeline

```bash
#!/bin/bash
# update-docs-pipeline.sh

DOC="user-guide.md"

# Stage 1: Update metadata
echo "Stage 1: Updating metadata..."
cat > /tmp/stage1.json << 'EOF'
{
  "frontmatter": {
    "pipeline_run": "2025-10-23T10:00:00Z",
    "status": "processing"
  }
}
EOF
mddata modify from-json "$DOC" /tmp/stage1.json

# Stage 2: Add generated content
echo "Stage 2: Adding generated content..."
python generate-content.py > /tmp/stage2.json
mddata modify from-json "$DOC" /tmp/stage2.json

# Stage 3: Finalize
echo "Stage 3: Finalizing..."
cat > /tmp/stage3.json << 'EOF'
{
  "frontmatter": {
    "status": "completed",
    "completed_at": "2025-10-23T10:05:00Z"
  },
  "sections": [
    {
      "id": "generated_notice",
      "content": "This document was automatically generated.",
      "policy": "update"
    }
  ]
}
EOF
mddata modify from-json "$DOC" /tmp/stage3.json

# Cleanup
rm /tmp/stage*.json

echo "Pipeline complete!"
```

### Example 11: Extract-Transform-Apply

```bash
#!/bin/bash
# transform-pipeline.sh

SOURCE="source.md"
TARGET="target.md"

# Extract current data
mddata extract json "$SOURCE" > /tmp/source-data.json

# Transform with jq
jq '{
  frontmatter: .frontmatter | .status = "migrated" | .version = 2.0,
  sections: [
    {
      id: "migration_info",
      content: "Migrated from \(.frontmatter.title)",
      policy: "update"
    }
  ]
}' /tmp/source-data.json > /tmp/transform.json

# Apply to target
mddata modify from-json "$TARGET" /tmp/transform.json

# Cleanup
rm /tmp/source-data.json /tmp/transform.json
```

## Complex Content Patterns

### Example 12: Multi-Level Subsections

**Transform (deep-structure.json):**
```json
{
  "sections": [
    {
      "id": "guide",
      "content": "Complete user guide.",
      "policy": "update"
    },
    {
      "id": "guide.basics",
      "content": "## Basics\n\nLearn the basics first.",
      "policy": "update"
    },
    {
      "id": "guide.basics.concepts",
      "content": "### Concepts\n\nCore concepts explained.",
      "policy": "update"
    },
    {
      "id": "guide.basics.concepts.terminology",
      "content": "#### Terminology\n\n- **Term 1**: Definition\n- **Term 2**: Definition",
      "policy": "update"
    },
    {
      "id": "guide.advanced",
      "content": "## Advanced\n\nAdvanced topics.",
      "policy": "update"
    },
    {
      "id": "guide.advanced.patterns",
      "content": "### Patterns\n\nDesign patterns.",
      "policy": "update"
    }
  ]
}
```

**Result structure:**
```
guide (level 1: #)
  basics (level 2: ##)
    concepts (level 3: ###)
      terminology (level 4: ####)
  advanced (level 2: ##)
    patterns (level 3: ###)
```

### Example 13: Mixed Content Types

**Transform (rich-content.json):**
```json
{
  "sections": [
    {
      "id": "tutorial.setup",
      "content": "## Setup\n\nFollow these steps:\n\n1. Install dependencies\n2. Configure environment\n3. Run initialization\n\n```bash\nnpm install\ncp .env.example .env\nnpm run init\n```\n\n> **Note:** Ensure Node.js 18+ is installed.\n\n### Troubleshooting\n\nCommon issues:\n\n- **Port already in use**: Change PORT in .env\n- **Permission denied**: Run with sudo\n\n---\n\nNext: [Configuration](configuration.md)",
      "policy": "update"
    }
  ]
}
```

**Result:** Section with paragraphs, ordered lists, code blocks, blockquotes, subsections, and thematic breaks.

## Validation and Error Handling

### Example 14: With Schema Validation

```bash
# Generate with validation
mddata modify from-json document.md transform.json

# Validate after changes
mddata schema validate document.md schema.json --verbose
```

**Workflow:**
1. Apply transformations
2. Validate against schema
3. Fix any validation errors
4. Reapply if needed

### Example 15: Safe Transformation Script

```bash
#!/bin/bash
# safe-transform.sh

DOC="$1"
TRANSFORM="$2"

# Backup
cp "$DOC" "${DOC}.backup"

# Dry run first
echo "Previewing changes..."
mddata modify from-json "$DOC" "$TRANSFORM" --dry-run

# Confirm
read -p "Apply changes? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted"
    rm "${DOC}.backup"
    exit 1
fi

# Apply
echo "Applying changes..."
if mddata modify from-json "$DOC" "$TRANSFORM"; then
    echo "Success!"
    rm "${DOC}.backup"
else
    echo "Failed! Restoring backup..."
    mv "${DOC}.backup" "$DOC"
    exit 1
fi
```

## Best Practices

### 1. Use Dry Run

Always preview complex changes:
```bash
mddata modify from-json doc.md changes.json --dry-run
```

### 2. Version Control

Commit before bulk transformations:
```bash
git commit -am "Before bulk transformation"
mddata modify from-json doc.md transform.json
git diff doc.md
```

### 3. Modular Transforms

Break complex changes into smaller transforms:
```bash
# Instead of one large transform
mddata modify from-json doc.md metadata-updates.json
mddata modify from-json doc.md content-updates.json
mddata modify from-json doc.md structure-updates.json
```

### 4. Validate Inputs

Validate JSON before applying:
```bash
# Validate JSON syntax
cat transform.json | jq . > /dev/null && echo "Valid JSON"

# Then apply
mddata modify from-json doc.md transform.json
```

### 5. Error Recovery

Always have a rollback strategy:
```bash
# Backup
cp document.md document.backup.md

# Transform
mddata modify from-json document.md transform.json

# Verify
mddata info summary document.md

# Rollback if needed
# mv document.backup.md document.md
```

### 6. Document Transforms

Keep transformation files with clear names:
```
transforms/
├── 01-initial-setup.json
├── 02-add-api-docs.json
├── 03-migrate-to-v2.json
└── README.md
```

### 7. Template Reuse

Create reusable transformation templates:
```json
{
  "frontmatter": {
    "template_version": "1.0",
    "author": "${AUTHOR}",
    "date": "${DATE}"
  },
  "sections": [
    {
      "id": "introduction",
      "content": "${INTRO_TEXT}",
      "policy": "update"
    }
  ]
}
```

Use with substitution:
```bash
cat template.json | \
  sed "s/\${AUTHOR}/John Doe/g" | \
  sed "s/\${DATE}/$(date +%Y-%m-%d)/g" | \
  sed "s/\${INTRO_TEXT}/Welcome to the guide/g" | \
  mddata modify from-json document.md -
```

## Complete Workflow Example

### Example 16: Documentation Release Process

```bash
#!/bin/bash
# release-docs.sh

VERSION="$1"
RELEASE_DATE="$(date +%Y-%m-%d)"

if [ -z "$VERSION" ]; then
    echo "Usage: $0 <version>"
    exit 1
fi

echo "Releasing documentation v${VERSION}..."

# Generate transformation
cat > /tmp/release-transform.json << EOF
{
  "frontmatter": {
    "version": "${VERSION}",
    "release_date": "${RELEASE_DATE}",
    "status": "released"
  },
  "sections": [
    {
      "id": "changelog",
      "content": "## Version ${VERSION} - ${RELEASE_DATE}\n\n- Released version ${VERSION}\n- Updated documentation",
      "policy": "append"
    },
    {
      "id": "download",
      "content": "## Download\n\nDownload version ${VERSION}:\n\n[Download v${VERSION}](https://releases.example.com/v${VERSION})",
      "policy": "update"
    }
  ]
}
EOF

# Apply to all docs
for doc in docs/**/*.md; do
    echo "Processing: $doc"
    mddata modify from-json "$doc" /tmp/release-transform.json
done

# Cleanup
rm /tmp/release-transform.json

echo "Documentation release complete!"
```

**Usage:**
```bash
./release-docs.sh 2.1.0
```

## Next Steps

- [Schema validation](04-schema-management.md) - Validate transformed documents
- [Extract data](03-extracting-metadata.md) - Create transformation sources
- [Generate documents](05-markdown-generation.md) - Combine with generation
