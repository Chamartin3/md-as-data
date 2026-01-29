---
name: md-validate
description: Infer schemas from markdown documents and validate document structure against schemas. Automatically validate documents, infer schemas from existing documents or directories, and ensure document structure consistency. Use when users need schema validation, want to enforce document structure, infer schemas, or validate markdown files against templates.
allowed-tools: Bash(mddata:*), Read, Write
---

# Markdown Validation Skill

## Purpose

Automatically infer schemas and validate markdown documents using mddata. Ensure document consistency, validate structure, and maintain documentation standards through schema-based validation.

## Prerequisites

- `mddata` command must be available in PATH
- Markdown files for schema inference
- Optional: existing schema files (JSON or YAML)

## Core Operations

### 1. Infer Schema from Single Document

Create a schema by inferring structure from an existing markdown file:

```bash
# JSON format (default)
mddata schema infer document.md --output schema.json --pretty

# YAML format (more readable)
mddata schema infer document.md --format yaml --output schema.yaml --pretty
```

**Inference Modes:**
- `--inference-mode permissive` (default): Flexible constraints allowing evolution
- `--inference-mode strict`: Exact constraints matching current structure

### 2. Infer Schema from Multiple Documents

Create a merged schema from all markdown files in a directory:

```bash
# Recursively process all .md files
mddata schema infer ./docs/ --output docs-schema.json --pretty
mddata schema infer ./docs/ --format yaml --output docs-schema.yaml
```

**Multi-file schema behavior:**
- Properties in ≥75% of files marked as required
- Enum types created for consistent single-word strings
- Union types for conflicting property types
- All section hierarchies merged

### 3. Validate Document Against Schema

Check if a document matches a schema:

```bash
# Basic validation
mddata schema validate document.md schema.json

# Verbose output with details
mddata schema validate document.md schema.yaml --verbose

# Override validation level
mddata schema validate document.md schema.json --validation-level strict
```

**Validation Levels:**
- `strict`: Fail on any validation errors
- `warnings`: Collect warnings but don't fail
- `disabled`: Skip validation

### 4. Display Schema Information

Inspect schema structure and requirements:

```bash
mddata schema info schema.json
mddata schema info schema.yaml
```

## Autonomous Validation Workflow

When working with markdown files, automatically:

### Step 1: Check for Existing Schema

```bash
# Look for common schema file names
ls -la schema.json schema.yaml doc-schema.* *.schema.*
```

### Step 2: Auto-Validate if Schema Exists

```bash
if [ -f "schema.json" ]; then
  mddata schema validate document.md schema.json --verbose
fi
```

### Step 3: Infer Schema if Missing

```bash
# For single document
mddata schema infer document.md --output schema.json --pretty

# For document collection
mddata schema infer ./docs/ --output docs-schema.json --pretty
```

## Usage Examples

### Example 1: Ensure Documentation Consistency

```
User: "Make sure all my API docs follow the same structure"

1. Infer schema from docs directory:
   mddata schema infer ./api-docs/ --output api-schema.json --pretty

2. Validate each document:
   for doc in api-docs/**/*.md; do
     mddata schema validate "$doc" api-schema.json --verbose
   done

3. Report validation results
4. Suggest fixes for non-compliant documents
```

### Example 2: Create Template from Existing Document

```
User: "I need a new document with the same structure as template.md"

1. Infer strict schema from template:
   mddata schema infer template.md --inference-mode strict --output template-schema.json --pretty

 2. Create new document from schema:
    mddata write --schema template-schema.json --output new-doc.md

3. Validate result:
   mddata schema validate new-doc.md template-schema.json --verbose
```

### Example 3: Validate Modified Documents

```
User: "I just updated several documentation files, can you verify they're still valid?"

1. Check for existing schema:
   ls schema.json docs-schema.json *.schema.*

2. If schema exists, validate all modified files:
   for file in docs/*.md; do
     echo "Validating $file..."
     mddata schema validate "$file" schema.json --verbose
   done

3. Report any validation failures with specific errors
4. Suggest fixes for each issue
```

### Example 4: Enforce Team Standards

```
User: "Create a schema from our standard template and validate all team docs"

1. Infer schema from team template:
   mddata schema infer templates/team-standard.md --inference-mode strict --output team-schema.json --pretty

2. Validate all team documents:
   find ./team-docs -name "*.md" -exec mddata schema validate {} team-schema.json --verbose \;

3. Generate compliance report:
   - List compliant documents (✓)
   - List non-compliant documents with errors (✗)
   - Provide specific fixes needed

4. Optionally offer to fix common issues automatically
```

### Example 5: Schema Evolution Tracking

```
User: "Our documentation has evolved - update the schema to reflect current structure"

1. Infer new schema from current docs:
   mddata schema infer ./docs/ --inference-mode permissive --output updated-schema.json --pretty

2. Compare with existing schema:
   # Using jq to show differences
   diff <(jq -S . schema.json) <(jq -S . updated-schema.json)

3. Identify changes:
   - New properties added
   - Properties that became required
   - New sections or structure changes

4. Validate all docs against updated schema:
   mddata schema validate ./docs/*.md updated-schema.json

5. Report compatibility and any breaking changes
```

### Example 6: Pre-commit Validation

```
User: "Validate my changes before committing"

1. Find modified markdown files:
   git diff --cached --name-only --diff-filter=ACM | grep '\.md$'

2. Check for project schema:
   if [ -f "schema.json" ]; then
     # Validate each modified file
     for file in $(git diff --cached --name-only | grep '\.md$'); do
       mddata schema validate "$file" schema.json --verbose || exit 1
     done
   else
     echo "No schema found - consider running: mddata schema infer ./docs/ -o schema.json"
   fi

3. Report validation status before commit
```

### Example 7: Multi-Format Schema Workflow

```
User: "I prefer YAML for editing schemas but need JSON for CI/CD"

1. Infer schema in YAML format:
   mddata schema infer ./docs/ --format yaml --output docs-schema.yaml --pretty

2. Edit YAML schema manually (easier to read and modify)
   vim docs-schema.yaml

3. Convert to JSON for CI/CD:
   yq -o json docs-schema.yaml > docs-schema.json

4. Validate using either format:
   mddata schema validate document.md docs-schema.yaml  # Auto-detects YAML
   mddata schema validate document.md docs-schema.json  # Auto-detects JSON
```

## Schema Structure Understanding

**Key schema components:**

1. **Frontmatter Schema**
   - Property names and types (`str`, `int`, `float`, `bool`, `list`, `dict`)
   - Required vs optional properties
   - Default values
   - Validation rules (min_length, max_length, pattern, enum, etc.)

2. **Section Schema**
   - Section IDs and hierarchy
   - Required sections
   - Content constraints (min/max blocks)
   - Allowed block types

3. **Validation Level**
   - `strict` - Fail on any validation errors
   - `warnings` - Collect warnings but don't fail
   - `disabled` - Skip validation

## Best Practices

1. **Use YAML for Human Editing**: More readable than JSON for manual schema work
2. **Permissive Mode for Collections**: When inferring from multiple files
3. **Strict Mode for Templates**: When creating exact template schemas
4. **Version Control Schemas**: Track schema changes alongside documents
5. **Validate in CI/CD**: Automate validation in build pipelines
6. **Infer from Good Examples**: Use well-structured documents as schema sources

## Proactive Behavior

When the user modifies markdown files, automatically:

1. Check if a schema exists in the project
2. Validate the modified file against the schema
3. Report validation results
4. Suggest fixes if validation fails
5. Offer to update schema if structural changes are intentional

## Error Handling

- **Schema not found**: Offer to infer one from existing documents
- **Validation failures**: Provide specific error messages with property paths
- **Format errors**: Report invalid JSON/YAML syntax
- **Type mismatches**: Show expected vs actual types
- **Missing required properties**: List all missing properties
- **Section violations**: Explain which sections are missing or invalid

## Integration Patterns

### CI/CD Validation

```yaml
# .github/workflows/validate.yml
name: Validate Documentation
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install mddata
        run: pip install mddata
      - name: Validate all docs
        run: |
          mddata schema validate README.md docs-schema.json --verbose
          mddata schema validate CONTRIBUTING.md docs-schema.json --verbose
          find ./docs -name "*.md" -exec mddata schema validate {} docs-schema.json \;
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Find schema file
SCHEMA=$(ls schema.json docs-schema.json *.schema.json 2>/dev/null | head -1)

if [ -z "$SCHEMA" ]; then
  echo "Warning: No schema found. Consider creating one with:"
  echo "  mddata schema infer ./docs/ -o schema.json --pretty"
  exit 0
fi

# Validate modified markdown files
echo "Validating modified markdown files against $SCHEMA..."
for file in $(git diff --cached --name-only --diff-filter=ACM | grep '\.md$'); do
  if ! mddata schema validate "$file" "$SCHEMA" --verbose; then
    echo "❌ Validation failed for $file"
    exit 1
  fi
  echo "✓ $file validated successfully"
done

echo "✓ All markdown files validated successfully"
```

### Build Script

```bash
#!/bin/bash
# build.sh - Regenerate schema and validate all docs

echo "Inferring schema from templates..."
mddata schema infer ./templates/ --output build/schema.json --pretty

echo "Validating all documentation..."
for doc in docs/**/*.md; do
  if ! mddata schema validate "$doc" build/schema.json --verbose; then
    echo "❌ Validation failed for $doc"
    exit 1
  fi
  echo "✓ $doc"
done

echo "✓ All documents validated successfully"
```

## Advanced Features

### Enum Type Inference

Automatically creates enum types for properties with consistent values:

```json
{
  "status": {
    "type": "str",
    "enum": ["draft", "review", "published", "archived"]
  }
}
```

### Union Type Handling

Handles properties with multiple types across documents:

```json
{
  "version": {
    "type": "int|str"  // Some docs use "1.0", others use 1
  }
}
```

### Frequency-Based Requirements

Properties appearing in most documents become required:

```
Property appears in 15/20 docs (75%) → required: true
Property appears in 10/20 docs (50%) → required: false
```

### Section Hierarchy Merging

When inferring from multiple documents, all section paths are preserved:

```json
{
  "sections": {
    "introduction": { ... },
    "getting_started": {
      "children": {
        "prerequisites": { ... },
        "installation": { ... }
      }
    }
  }
}
```

## When to Use This Skill

Use md-validate skill when:

1. **Validating documents** - Check if markdown files match expected structure
2. **Ensuring consistency** - Verify all docs in a collection follow same pattern
3. **Creating templates** - Infer strict schema from template documents
4. **Pre-commit checks** - Validate changes before committing
5. **CI/CD validation** - Automate structure validation in pipelines
6. **Schema evolution** - Track how document structure changes over time
7. **Team standards** - Enforce consistent documentation across team

## Integration with Other Skills

Works well with other mddata skills:

```
md-prepare (check installation & formats)
    ↓
md-validate (infer schemas & validate)
    ↓
md-query (inspect validated documents)
md-generator (create compliant documents)
```

## Output

When using this skill:

1. **Report validation results** clearly (✓ valid / ✗ invalid)
2. **Show specific errors** with property/section paths
3. **Suggest fixes** for validation failures
4. **Offer to infer schema** if none exists
5. **Explain schema structure** when requested
6. **Provide compliance reports** for multiple documents

## Summary

The md-validate skill ensures document quality by:

1. **Inferring schemas** from existing documents
2. **Validating structure** against schemas
3. **Ensuring consistency** across document collections
4. **Automating validation** in workflows
5. **Tracking evolution** of document structure
6. **Enforcing standards** for teams

**Remember:** Infer schemas from good examples, validate proactively, and maintain schemas alongside documents.
