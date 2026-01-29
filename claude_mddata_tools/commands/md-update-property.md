---
description: Set or update a frontmatter property in a markdown file
argument-hint: <markdown-file> <property-name> <value>
allowed-tools: Bash(mddata:*)
---

# Update Frontmatter Property

Update property **$2** in file **$1** with value: **$3**

## Step 1: Show Current State

Display current frontmatter properties:
```bash
mddata info properties "$1" --verbose
```

## Step 2: Apply the Change

Detect value type and apply the update:
```bash
if echo "$3" | grep -qE '^\[|^\{|^[0-9]+$|^true$|^false$'; then
  mddata modify set-property "$1" "$2" "$3" --json
else
  mddata modify set-property "$1" "$2" "$3"
fi
```

## Step 3: Verify the Change

Display updated frontmatter:
```bash
mddata info properties "$1" --verbose
```

---

**Value Types:**

String value:
```bash
/md-update-property doc.md title "New Title"
```

Number value:
```bash
/md-update-property doc.md version 2.0
```

Boolean value:
```bash
/md-update-property doc.md published true
```

Array value:
```bash
/md-update-property doc.md tags '["api", "docs", "v2"]'
```

Object value:
```bash
/md-update-property doc.md author '{"name": "John", "email": "john@example.com"}'
```

**Remove Property:**
```bash
mddata modify remove-property $1 $2
```

**Bulk Updates:**

For multiple property changes, use transformation JSON:
```bash
echo '{"frontmatter": {"version": 2.0, "status": "published"}}' | \
  mddata modify from-json $1 -
```
