---
description: Infer a schema from markdown file(s)
argument-hint: <path> [--format json|yaml]
allowed-tools: Bash(mddata:*), Bash(echo:*), Bash(if:*), Bash(test:*), Bash([:*), Bash(exit:*)
---

# Infer Schema

## Validation

Check if path argument is provided:
```bash
if [ -z "$1" ]; then
  echo "❌ Error: Path argument is required"
  echo ""
  echo "Usage: /mddata-tools:md-infer-schema <path> [--format json|yaml]"
  echo ""
  echo "Examples:"
  echo "  /mddata-tools:md-infer-schema document.md"
  echo "  /mddata-tools:md-infer-schema ./docs/"
  echo "  /mddata-tools:md-infer-schema document.md --format yaml"
  echo ""
  echo "⚠️  Note: Use actual file paths, not @ references"
  echo "     ❌ Don't use: /mddata-tools:md-infer-schema @examples/file.md"
  echo "     ✅ Use: /mddata-tools:md-infer-schema examples/file.md"
  echo ""
  echo "The path can be:"
  echo "  - A single markdown file"
  echo "  - A directory (will process all .md files recursively)"
  exit 1
fi
```

Infer schema from **$1** (file or directory)

**Format:** ${2:-json} (defaults to JSON if not specified)

## Run Schema Inference

Execute schema inference with pretty formatting:
```bash
if [ -d "$1" ]; then
  echo "Inferring schema from directory: $1"
  mddata schema infer "$1" --format ${2:-json} --pretty
elif [ -f "$1" ]; then
  echo "Inferring schema from file: $1"
  mddata schema infer "$1" --format ${2:-json} --pretty
else
  echo "❌ Error: Path not found: $1"
  echo ""
  echo "Please provide a valid path to:"
  echo "  - An existing markdown file (.md)"
  echo "  - An existing directory containing markdown files"
  exit 1
fi
```

---

**Save to File:**

```bash
# JSON format (default)
mddata schema infer $1 --output schema.json --pretty

# YAML format (more readable)
mddata schema infer $1 --format yaml --output schema.yaml --pretty
```

**Inference Modes:**

Permissive (default) - flexible constraints:
```bash
mddata schema infer $1 --inference-mode permissive --output schema.json
```

Strict - exact constraints:
```bash
mddata schema infer $1 --inference-mode strict --output schema.json
```

**Multi-File Schema:**

Generate from directory (recursive):
```bash
mddata schema infer ./docs/ --output docs-schema.json --pretty
```

This will:
- Process all .md files recursively
- Aggregate properties across documents
- Mark properties as required if in ≥75% of files
- Create enum types for consistent values
- Merge section hierarchies

**Use the Schema:**

Validate documents:
```bash
mddata schema validate document.md schema.json --verbose
```

Generate templates:
```bash
mddata render --schema schema.json --output template.md
```

Create validated documents:
```bash
mddata render --data data.json --schema schema.json --output doc.md
```
