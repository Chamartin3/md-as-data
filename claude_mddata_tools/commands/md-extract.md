---
description: Extract markdown file to JSON or YAML format
argument-hint: <markdown-file> [json|yaml]
allowed-tools: Bash(mddata:*), Bash(if:*), Bash(test:*), Bash([:*)
---

# Extract Markdown to Structured Data

Extract **$1** to structured data format.

**Requested Format:** ${2:-json} (defaults to JSON if not specified)

Run the appropriate extraction command:

```bash
if [ "$2" = "yaml" ]; then
  mddata extract yaml "$1"
else
  mddata extract json "$1" --pretty
fi
```

---

**Extracted Data Structure:**
- `frontmatter`: All YAML frontmatter properties
- `content.sections`: Hierarchical section tree
  - Each section includes: id, title, level, blocks, subsections
- `blocks`: Content blocks by type (paragraph, code, list, etc.)

**Additional Options:**

Save to file:
```bash
# JSON format
mddata extract json "$1" --pretty --output data.json

# YAML format
mddata extract yaml "$1" --output data.yaml
```

Extract only frontmatter:
```bash
mddata extract frontmatter "$1" --format json
mddata extract frontmatter "$1" --format yaml
```

**Use Cases:**
- Data processing pipelines
- Documentation APIs
- Content migration
- Automated analysis
- Integration with other tools (jq, yq, etc.)
