---
description: Update markdown file from JSON or YAML data structure
argument-hint: <markdown-file> <data-file>
allowed-tools: Bash(mddata:*)
---

# Update Markdown From Data

Update **$1** from data file **$2**

## Step 1: Show Current State

Display current document summary:
```bash
mddata info summary "$1"
```

## Step 2: Apply Changes

Apply updates from data file (auto-detects modify mode):
```bash
mddata write --data "$2" "$1"
```

## Step 3: Verify Changes

Display updated document summary:
```bash
mddata info summary "$1"
```

---

**Data Format:**

The data file should contain a JSON or YAML structure with `frontmatter` and/or `sections` to update:

```json
{
  "frontmatter": {
    "title": "Updated Title",
    "version": "2.0"
  },
  "sections": [
    {
      "id": "introduction",
      "content": "New introduction content",
      "policy": "replace"
    }
  ]
}
```

**Usage Examples:**

Update from JSON file:
```bash
/md-update-from-data document.md changes.json
```

Update from YAML file:
```bash
/md-update-from-data document.md changes.yaml
```

Update from stdin:
```bash
echo '{"frontmatter": {"status": "published"}}' | /md-update-from-data document.md -
```

**Section Policies:**

- `update` (default): Merge content while preserving subsections
- `replace`: Replace entire section content
- `append`: Add content to existing section

**Dry Run:**

Preview changes without applying:
```bash
mddata write --data "$2" "$1" --dry-run
```
