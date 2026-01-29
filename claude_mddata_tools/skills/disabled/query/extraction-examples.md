# Extraction Examples for Markdown Query

This guide provides practical examples for extracting specific information from markdown documents using the `mddata extract` command suite.

## Table of Contents

1. [Basic Extraction](#basic-extraction)
2. [Selective Data Extraction](#selective-data-extraction)
3. [Extraction Pipelines](#extraction-pipelines)
4. [Data Transformation](#data-transformation)
5. [Integration Workflows](#integration-workflows)

---

## Basic Extraction

### Example 1: Extract Complete Document to JSON

```bash
# Extract full document structure
mddata extract json documentation.md

# Pretty-printed for readability
mddata extract json documentation.md --pretty

# Save to file
mddata extract json documentation.md --output doc-data.json --pretty
```

**Output structure:**
```json
{
  "frontmatter": {
    "title": "Documentation Title",
    "author": "John Doe",
    "date": "2025-10-24"
  },
  "content": {
    "id": "",
    "title": "",
    "level": 0,
    "path": "",
    "blocks": [],
    "children": [ /* sections */ ]
  }
}
```

### Example 2: Extract to YAML Format

```bash
# Extract as YAML (more human-readable)
mddata extract yaml documentation.md

# Save to YAML file
mddata extract yaml documentation.md --output doc-data.yaml
```

**Output:**
```yaml
frontmatter:
  title: "Documentation Title"
  author: "John Doe"
  date: "2025-10-24"

content:
  id: ""
  title: ""
  level: 0
  path: ""
  blocks: []
  children:
    - id: "introduction"
      title: "Introduction"
      ...
```

### Example 3: Extract Only Frontmatter

```bash
# Extract frontmatter as JSON
mddata extract frontmatter document.md --format json

# Extract frontmatter as YAML
mddata extract frontmatter document.md --format yaml

# Save frontmatter
mddata extract frontmatter document.md --format json --output metadata.json
```

**Use case:** Extract metadata for indexing, cataloging, or filtering.

---

## Selective Data Extraction

### Example 4: Extract Specific Properties

```bash
# Extract and filter specific frontmatter properties
mddata extract frontmatter document.md --format json | jq '{title, author, tags}'

# Extract just the title
mddata extract frontmatter document.md --format json | jq -r '.title'

# Extract tags as array
mddata extract frontmatter document.md --format json | jq -r '.tags[]'
```

**Result:**
```json
{
  "title": "API Documentation",
  "author": "Development Team",
  "tags": ["api", "reference", "v2"]
}
```

### Example 5: Extract Specific Sections

```bash
# Extract full document then filter specific section
mddata extract json guide.md --pretty | jq '.content.children[] | select(.id == "installation")'

# Extract section content blocks
mddata extract json guide.md | jq '.content.children[] | select(.id == "installation") | .blocks'

# Extract nested section
mddata extract json guide.md | jq '.content.children[] | select(.id == "getting_started") | .children[] | select(.id == "prerequisites")'
```

**Use case:** Extract specific portions for separate processing.

### Example 6: Extract Code Blocks Only

```bash
# Extract all code blocks with their content
mddata extract json tutorial.md | jq -r '
  .. |
  select(.type? == "code_block") |
  "Section: \(.section_id)\nLanguage: \(.metadata.language // "none")\n\(.content)\n---"
'

# Extract code blocks from specific section
mddata extract json tutorial.md | jq -r '
  .content.children[] |
  select(.id == "examples") |
  .blocks[] |
  select(.type == "code_block") |
  .content
'

# Count code blocks by language
mddata extract json tutorial.md | jq -r '
  [.. | select(.type? == "code_block") | .metadata.language // "none"] |
  group_by(.) |
  map({language: .[0], count: length}) |
  .[]
'
```

**Output example:**
```
Section: installation
Language: bash
pip install mddata
---

Section: usage
Language: python
from mddata import MarkdownFile
doc = MarkdownFile('example.md')
---
```

### Example 7: Extract All Links

```bash
# Extract link blocks
mddata extract json documentation.md | jq -r '
  .. |
  select(.type? == "link") |
  "[\(.content)](\(.metadata.href))"
'

# Extract unique URLs
mddata extract json documentation.md | jq -r '
  [.. | select(.type? == "link") | .metadata.href] |
  unique |
  .[]
'

# Create link inventory with sections
mddata extract json documentation.md | jq -r '
  .. |
  select(.type? == "link") |
  "\(.section_id): [\(.content)](\(.metadata.href))"
'
```

---

## Extraction Pipelines

### Example 8: Build Table of Contents from Extraction

```bash
# Generate TOC from extracted data
mddata extract json guide.md | jq -r '
  def toc(level):
    .children[]? |
    (("  " * (level - 1)) + "- " + .title),
    toc(level + 1);

  .content | toc(1)
'
```

**Output:**
```
- Introduction
- Getting Started
  - Prerequisites
  - Installation
- Advanced Topics
  - Configuration
  - Troubleshooting
```

### Example 9: Extract Metadata for Search Index

```bash
# Create search index entries
for doc in docs/*.md; do
  mddata extract json "$doc" | jq -r --arg file "$doc" '{
    file: $file,
    title: .frontmatter.title,
    tags: .frontmatter.tags,
    sections: [.content.children[].title],
    content_preview: ([.. | select(.type? == "paragraph") | .content] | first)
  }'
done | jq -s '.' > search-index.json
```

**Result:**
```json
[
  {
    "file": "docs/api.md",
    "title": "API Reference",
    "tags": ["api", "reference"],
    "sections": ["Authentication", "Endpoints", "Errors"],
    "content_preview": "This API provides access to..."
  },
  ...
]
```

### Example 10: Extract Task List Summary

```bash
# Extract all tasks with status
mddata extract json project.md | jq -r '
  .. |
  select(.type? == "task_list") |
  .metadata.tasks[] |
  if .symbol == "x" then
    "✓ " + .content
  else
    "☐ " + .content
  end
'

# Calculate task completion
mddata extract json project.md | jq '
  [.. | select(.type? == "task_list") | .metadata.tasks[]] |
  {
    total: length,
    completed: ([.[] | select(.symbol == "x")] | length),
    pending: ([.[] | select(.symbol == " ")] | length)
  } |
  .percentage = ((.completed / .total) * 100 | round)
'
```

**Output:**
```json
{
  "total": 25,
  "completed": 18,
  "pending": 7,
  "percentage": 72
}
```

---

## Data Transformation

### Example 11: Convert to Different Format

```bash
# Extract and convert to CSV (section summary)
mddata extract json guide.md | jq -r '
  ["Section", "Blocks", "Level"],
  (.content.children[] | [.title, (.blocks | length), .level]) |
  @csv
'

# Extract frontmatter as environment variables
mddata extract frontmatter config.md --format json | jq -r '
  to_entries |
  .[] |
  "export \(.key | ascii_upcase)=\"\(.value)\""
'
```

**CSV Output:**
```csv
"Section","Blocks","Level"
"Introduction",5,2
"Installation",8,2
"Configuration",12,2
```

### Example 12: Extract for Static Site Generator

```bash
# Extract data for Jekyll/Hugo front matter
mddata extract frontmatter post.md --format yaml > _data/posts/$(basename post.md .md).yml

# Extract content for processing
mddata extract json post.md | jq -r '
  .content.children[] |
  "## \(.title)\n\n" +
  (.blocks[] | .content) +
  "\n"
' > _posts/$(date +%Y-%m-%d)-$(basename post.md)
```

### Example 13: Build Documentation Database

```bash
#!/bin/bash
# build-doc-db.sh - Create SQLite database from markdown docs

# Create database
sqlite3 docs.db <<EOF
CREATE TABLE IF NOT EXISTS documents (
  id INTEGER PRIMARY KEY,
  filename TEXT,
  title TEXT,
  author TEXT,
  date TEXT,
  tags TEXT,
  section_count INTEGER,
  block_count INTEGER
);

CREATE TABLE IF NOT EXISTS sections (
  id INTEGER PRIMARY KEY,
  doc_id INTEGER,
  section_id TEXT,
  title TEXT,
  level INTEGER,
  path TEXT,
  block_count INTEGER,
  FOREIGN KEY(doc_id) REFERENCES documents(id)
);
EOF

# Populate database
doc_id=1
for doc in docs/*.md; do
  # Extract document data
  data=$(mddata extract json "$doc" --pretty)

  # Insert document
  title=$(echo "$data" | jq -r '.frontmatter.title // ""')
  author=$(echo "$data" | jq -r '.frontmatter.author // ""')
  date=$(echo "$data" | jq -r '.frontmatter.date // ""')
  tags=$(echo "$data" | jq -r '.frontmatter.tags | join(",") // ""')
  section_count=$(echo "$data" | jq '[.content.children[]] | length')
  block_count=$(echo "$data" | jq '[.. | select(.type? != null)] | length')

  sqlite3 docs.db "INSERT INTO documents VALUES (
    $doc_id,
    '$doc',
    '$title',
    '$author',
    '$date',
    '$tags',
    $section_count,
    $block_count
  );"

  # Insert sections
  echo "$data" | jq -r '.content.children[] | [
    "'$doc_id'",
    .id,
    .title,
    .level,
    .path,
    (.blocks | length)
  ] | @tsv' | while IFS=$'\t' read -r did sid stitle slevel spath sblocks; do
    sqlite3 docs.db "INSERT INTO sections VALUES (
      NULL,
      $did,
      '$sid',
      '$stitle',
      $slevel,
      '$spath',
      $sblocks
    );"
  done

  doc_id=$((doc_id + 1))
done

echo "Database created: docs.db"
```

---

## Integration Workflows

### Example 14: API Response to Markdown

```bash
# Fetch API data and convert to markdown
curl -s https://api.example.com/docs | jq '{
  frontmatter: {
    title: .title,
    api_version: .version,
    generated: (now | strftime("%Y-%m-%d"))
  },
  content: {
    id: "",
    title: "",
    level: 0,
    path: "",
    blocks: [],
    children: [
      {
        id: "endpoints",
        title: "Endpoints",
        level: 2,
        path: "endpoints",
        blocks: [
          {
            section_id: "endpoints",
            type: "paragraph",
            content: .description,
            metadata: {}
          }
        ],
        children: (.endpoints | map({
          id: .name,
          title: .name,
          level: 3,
          path: ("endpoints." + .name),
          blocks: [
            {
              section_id: .name,
              type: "paragraph",
              content: .description,
              metadata: {}
            },
            {
              section_id: .name,
              type: "code_block",
              content: .example,
              metadata: {language: "json"}
            }
          ],
          children: []
        }))
      }
    ]
  }
}' | mddata write --data - --output api-docs.md
```

### Example 15: Extract for Translation Workflow

```bash
# Extract text content for translation
mddata extract json original.md | jq -r '
  .. |
  select(.type? == "paragraph" or .type? == "blockquote") |
  .content
' > content-to-translate.txt

# After translation, merge back
# (requires custom script to reconstruct)
```

### Example 16: Generate Documentation Diff

```bash
# Extract both versions
mddata extract json old-version.md --output old.json --pretty
mddata extract json new-version.md --output new.json --pretty

# Compare structures
diff <(jq -S . old.json) <(jq -S . new.json) > changes.diff

# Identify changed sections
jq -s '
  {
    old_sections: [.[0].content.children[].id],
    new_sections: [.[1].content.children[].id],
    added: ([.[1].content.children[].id] - [.[0].content.children[].id]),
    removed: ([.[0].content.children[].id] - [.[1].content.children[].id])
  }
' old.json new.json
```

### Example 17: Create Documentation Summary Page

```bash
#!/bin/bash
# generate-summary.sh

echo "# Documentation Summary"
echo ""
echo "Generated: $(date)"
echo ""

for doc in docs/**/*.md; do
  data=$(mddata extract json "$doc")

  title=$(echo "$data" | jq -r '.frontmatter.title // "Untitled"')
  sections=$(echo "$data" | jq '[.content.children[]] | length')
  blocks=$(echo "$data" | jq '[.. | select(.type? != null)] | length')

  echo "## $title"
  echo ""
  echo "- **File**: \`$doc\`"
  echo "- **Sections**: $sections"
  echo "- **Content blocks**: $blocks"

  # Extract first paragraph as summary
  summary=$(echo "$data" | jq -r '
    [.. | select(.type? == "paragraph") | .content] | first // "No description"
  ')
  echo "- **Summary**: $summary"
  echo ""
done > DOCUMENTATION_SUMMARY.md
```

### Example 18: Build Cross-Reference Index

```bash
# Extract all internal references
for doc in docs/*.md; do
  mddata extract json "$doc" | jq -r --arg file "$doc" '
    .. |
    select(.type? == "link" and (.metadata.href | startswith("#") or startswith("."))) |
    {
      source: $file,
      link_text: .content,
      target: .metadata.href,
      section: .section_id
    }
  '
done | jq -s '.' > cross-references.json

# Identify broken internal links
jq -r '.[] | select(.target | startswith(".")) | .target' cross-references.json | \
while read ref; do
  if [ ! -f "docs/$ref" ]; then
    echo "Broken link: $ref"
  fi
done
```

### Example 19: Export for Documentation Platform

```bash
# Extract for Confluence/Notion import
mddata extract json guide.md | jq '{
  title: .frontmatter.title,
  space: "DOCS",
  body: {
    storage: {
      value: ([
        .content.children[] |
        "<h\(.level)>\(.title)</h\(.level)>",
        (.blocks[] |
          if .type == "paragraph" then
            "<p>\(.content)</p>"
          elif .type == "code_block" then
            "<ac:structured-macro ac:name=\"code\"><ac:parameter ac:name=\"language\">\(.metadata.language)</ac:parameter><ac:plain-text-body><![CDATA[\(.content)]]></ac:plain-text-body></ac:structured-macro>"
          else
            ""
          end
        )
      ] | join("\n")),
      representation: "storage"
    }
  }
}' | curl -X POST \
  -H "Content-Type: application/json" \
  -d @- \
  https://your-instance.atlassian.net/wiki/rest/api/content
```

### Example 20: Create Documentation Analytics

```bash
#!/bin/bash
# doc-analytics.sh

echo "# Documentation Analytics Report"
echo "================================="
echo ""

total_docs=0
total_sections=0
total_blocks=0
total_words=0

declare -A languages

for doc in docs/**/*.md; do
  data=$(mddata extract json "$doc")

  total_docs=$((total_docs + 1))

  sections=$(echo "$data" | jq '[.content.children[]] | length')
  total_sections=$((total_sections + sections))

  blocks=$(echo "$data" | jq '[.. | select(.type? != null)] | length')
  total_blocks=$((total_blocks + blocks))

  words=$(echo "$data" | jq -r '[.. | select(.type? == "paragraph") | .content] | join(" ")' | wc -w)
  total_words=$((total_words + words))

  # Count code block languages
  echo "$data" | jq -r '.. | select(.type? == "code_block") | .metadata.language // "none"' | \
  while read lang; do
    languages[$lang]=$((${languages[$lang]:-0} + 1))
  done
done

echo "## Overall Statistics"
echo "- Total documents: $total_docs"
echo "- Total sections: $total_sections"
echo "- Total content blocks: $total_blocks"
echo "- Total words: $total_words"
echo "- Average sections per document: $((total_sections / total_docs))"
echo "- Average blocks per document: $((total_blocks / total_docs))"
echo ""

echo "## Code Block Languages"
for lang in "${!languages[@]}"; do
  echo "- $lang: ${languages[$lang]}"
done | sort -t: -k2 -rn
```

---

## Summary

These extraction examples demonstrate how to:

1. **Extract complete data** - Full document structure in JSON/YAML
2. **Filter selectively** - Extract specific sections, properties, or blocks
3. **Build pipelines** - Chain extraction with processing tools
4. **Transform formats** - Convert to CSV, SQL, HTML, etc.
5. **Integrate systems** - Connect markdown docs with external tools
6. **Generate reports** - Create analytics and summaries

Use `mddata extract` as the foundation for automated documentation workflows, content management systems, and data-driven documentation processing.
