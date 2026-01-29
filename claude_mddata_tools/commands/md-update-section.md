---
description: Update or create a section in a markdown file
argument-hint: <markdown-file> <section-path> <content> [--policy update|replace|append]
allowed-tools: Bash(mddata:*), Bash(if:*), Bash(test:*), Bash([:*)
---

# Update Section Content

Update section **$2** in file **$1**

**Content:** $3
**Policy:** ${4:-update} (default: update)

## Step 1: Show Current Structure

Display current section hierarchy:
```bash
mddata info sections "$1" --paths
```

## Step 2: Apply Update

Apply section update with specified policy:
```bash
if [ -z "$4" ]; then
  mddata modify set-section "$1" "$2" "$3" --policy update
else
  mddata modify set-section "$1" "$2" "$3" --policy "$4"
fi
```

## Step 3: Verify Updated Structure

Display updated section hierarchy:
```bash
mddata info sections "$1" --paths --blocks
```

---

**Section Policies:**

**update** (default) - Merge content, preserve subsections:
```bash
/md-update-section doc.md introduction "New intro text"
```

**replace** - Replace entire section (removes subsections):
```bash
/md-update-section doc.md changelog "## v2.0\n- New release" --policy replace
```

**append** - Add to end of section:
```bash
/md-update-section doc.md notes "Additional note" --policy append
```

**Path-Based Section Access:**

Top-level section:
```bash
/md-update-section doc.md introduction "Content"
```

Nested section (dot-separated path):
```bash
/md-update-section doc.md introduction.overview "Overview content"
```

Create new subsection:
```bash
/md-update-section doc.md api.endpoints.new_endpoint "Endpoint docs"
```

**View Section Before Modifying:**
```bash
mddata info sections $1 --paths
```

**Bulk Section Updates:**

For multiple section changes, use transformation JSON:
```json
{
  "sections": [
    {"id": "intro", "content": "Updated intro", "policy": "update"},
    {"id": "conclusion", "content": "New conclusion", "policy": "replace"}
  ]
}
```

Apply with:
```bash
mddata modify from-json $1 changes.json
```
