# Complex Research Examples for Markdown Query

This guide provides advanced examples for researching markdown document structure using the `mddata info` command suite.

## Table of Contents

1. [Document Structure Analysis](#document-structure-analysis)
2. [Content Discovery Workflows](#content-discovery-workflows)
3. [Multi-Document Analysis](#multi-document-analysis)
4. [Targeted Information Extraction](#targeted-information-extraction)
5. [Quality Assurance Checks](#quality-assurance-checks)
6. [Documentation Auditing](#documentation-auditing)

---

## Document Structure Analysis

### Example 1: Complete Document Inventory

**Scenario:** Understanding the full structure of a complex technical document.

```bash
# Step 1: Get high-level overview
mddata info summary technical-guide.md --verbose

# Step 2: Map all sections with paths
mddata info sections technical-guide.md --paths --blocks

# Step 3: Analyze block distribution
mddata info blocks technical-guide.md

# Step 4: Check frontmatter metadata
mddata info properties technical-guide.md --verbose
```

**What this reveals:**
- Total content volume (sections, blocks)
- Document organization (section hierarchy)
- Content type distribution (paragraphs, code, lists)
- Metadata completeness

**Example output interpretation:**
```
Summary:
  Title: "Advanced Python Programming"
  Sections: 12 (4 top-level, 8 nested)
  Blocks: 87 total
    - 45 paragraphs
    - 23 code_blocks
    - 12 lists
    - 7 blockquotes

Sections with paths:
  introduction (2 blocks)
  getting_started (15 blocks)
    ├─ getting_started.prerequisites (5 blocks)
    └─ getting_started.installation (10 blocks)
  advanced_topics (35 blocks)
    ├─ advanced_topics.async_programming (18 blocks)
    └─ advanced_topics.decorators (17 blocks)
```

### Example 2: Identifying Documentation Gaps

**Scenario:** Finding sections with insufficient content.

```bash
# List all sections with block counts
mddata info sections documentation.md --blocks | grep -E "^\s+\w+.*\(0 blocks\)"

# Find sections with minimal content (1-2 blocks)
mddata info sections documentation.md --blocks | grep -E "^\s+\w+.*\([1-2] blocks\)"

# Get detailed view of specific sparse section
mddata info blocks documentation.md --section "installation"
```

**Use case:** Identify incomplete sections that need more content.

### Example 3: Code Example Distribution Analysis

**Scenario:** Ensuring each tutorial section has sufficient code examples.

```bash
# Count code blocks per section
for section in $(mddata info sections tutorial.md --paths | awk '{print $1}'); do
  count=$(mddata info blocks tutorial.md --section "$section" --type code_block | wc -l)
  echo "$section: $count code blocks"
done

# Find sections without code examples
mddata info sections tutorial.md --paths | while read section rest; do
  if [ -z "$(mddata info blocks tutorial.md --section "$section" --type code_block)" ]; then
    echo "⚠️  No code examples in: $section"
  fi
done
```

**Result:** List of sections needing code examples.

---

## Content Discovery Workflows

### Example 4: Finding Specific Content Patterns

**Scenario:** Locate all sections discussing a specific topic.

```bash
# Find sections with "authentication" in title
mddata info sections api-docs.md | grep -i "authentication"

# Extract all code blocks from authentication sections
mddata info blocks api-docs.md --section "authentication" --type code_block

# Get all properties related to API configuration
mddata info properties api-docs.md --verbose | grep -i "api\|config\|endpoint"
```

### Example 5: Task Management Analysis

**Scenario:** Tracking task completion across project documentation.

```bash
# Count total tasks
mddata info tasks project-plan.md

# Count completed vs pending
completed=$(mddata info tasks project-plan.md --completed | wc -l)
pending=$(mddata info tasks project-plan.md --pending | wc -l)
total=$((completed + pending))
percentage=$((completed * 100 / total))

echo "Progress: $completed/$total ($percentage% complete)"

# Find sections with pending tasks
for section in $(mddata info sections project-plan.md --paths | awk '{print $1}'); do
  pending_count=$(mddata info tasks project-plan.md --section "$section" --pending | wc -l)
  if [ $pending_count -gt 0 ]; then
    echo "📋 $section: $pending_count pending tasks"
  fi
done
```

### Example 6: Content Type Profiling

**Scenario:** Understanding the composition of documentation.

```bash
# Profile content types
echo "Content Type Distribution:"
echo "=========================="

for type in paragraph code_block list blockquote; do
  count=$(mddata info blocks guide.md --type $type | wc -l)
  echo "$type: $count"
done

# Calculate code-to-text ratio
code_blocks=$(mddata info blocks guide.md --type code_block | wc -l)
paragraphs=$(mddata info blocks guide.md --type paragraph | wc -l)
ratio=$(echo "scale=2; $code_blocks / $paragraphs" | bc)

echo ""
echo "Code-to-text ratio: $ratio"
echo "(Ideal for tutorials: 0.3-0.5)"
```

---

## Multi-Document Analysis

### Example 7: Cross-Document Comparison

**Scenario:** Comparing structure across multiple API documentation files.

```bash
# Compare section structure
echo "Section counts across API docs:"
for doc in api-docs/*.md; do
  sections=$(mddata info sections "$doc" | wc -l)
  printf "%-30s: %3d sections\n" "$(basename $doc)" "$sections"
done

# Find common sections across all docs
# (sections that appear in every document)
first_doc=$(ls api-docs/*.md | head -1)
mddata info sections "$first_doc" --paths | awk '{print $1}' | while read section; do
  found_in_all=true
  for doc in api-docs/*.md; do
    if ! mddata info sections "$doc" --paths | grep -q "^$section"; then
      found_in_all=false
      break
    fi
  done
  if $found_in_all; then
    echo "Common section: $section"
  fi
done
```

### Example 8: Documentation Consistency Check

**Scenario:** Ensuring all tutorial files have required sections.

```bash
# Required sections for tutorials
required_sections="introduction prerequisites installation usage examples troubleshooting"

for tutorial in tutorials/*.md; do
  echo "Checking: $(basename $tutorial)"

  for required in $required_sections; do
    if ! mddata info sections "$tutorial" --paths | grep -q "^$required"; then
      echo "  ❌ Missing: $required"
    else
      echo "  ✓ Has: $required"
    fi
  done
  echo ""
done
```

### Example 9: Metadata Aggregation

**Scenario:** Collecting all unique tags across documentation.

```bash
# Extract all tags from all markdown files
all_tags=$(for doc in docs/*.md; do
  mddata info properties "$doc" | grep "^tags:" | sed 's/tags: //'
done | sort -u)

echo "Unique tags across all documentation:"
echo "$all_tags" | tr ',' '\n' | sed 's/^\[//;s/\]$//;s/^ *//;s/ *$//' | sort -u

# Count documents per tag
for tag in $all_tags; do
  count=$(grep -l "tags:.*$tag" docs/*.md | wc -l)
  echo "$tag: $count documents"
done
```

---

## Targeted Information Extraction

### Example 10: Extract All URLs/Links

**Scenario:** Build a link inventory from documentation.

```bash
# Extract all link blocks
mddata info blocks documentation.md --type link

# Combine with grep to extract actual URLs
mddata info blocks documentation.md --type link | grep -oE 'https?://[^ )"]+'

# Create link report with context
echo "Link Inventory"
echo "=============="
mddata info blocks documentation.md --type link | while read -r line; do
  if [[ $line =~ https?:// ]]; then
    section=$(echo "$line" | grep -oP 'Section: \K[^,]+')
    url=$(echo "$line" | grep -oP 'https?://[^ )]+')
    echo "[$section] $url"
  fi
done
```

### Example 11: Code Language Analysis

**Scenario:** Identify programming languages used in code examples.

```bash
# Extract all code blocks with metadata
mddata info blocks tutorial.md --type code_block --verbose

# Count code blocks by language
echo "Code blocks by language:"
mddata info blocks tutorial.md --type code_block --verbose \
  | grep "language:" \
  | sed 's/.*language: //' \
  | sort | uniq -c | sort -rn

# Find code blocks without language specification
echo ""
echo "Code blocks missing language specification:"
mddata info blocks tutorial.md --type code_block --verbose \
  | grep -B5 "language: none\|language: $" \
  | grep "Section:" \
  | sed 's/Section: //'
```

### Example 12: Extracting Structured Data

**Scenario:** Build a table of contents with block counts.

```bash
# Generate detailed TOC
echo "# Table of Contents"
echo ""

mddata info sections guide.md --paths --blocks | while read line; do
  # Extract section info
  section=$(echo "$line" | awk '{print $1}')
  blocks=$(echo "$line" | grep -oP '\(\K[0-9]+(?= blocks\))')

  # Calculate indentation from path
  depth=$(echo "$section" | tr -cd '.' | wc -c)
  indent=$(printf '%*s' $((depth * 2)) '')

  # Clean section name
  name=$(echo "$section" | sed 's/.*\.//')

  echo "${indent}- $name ($blocks blocks)"
done
```

---

## Quality Assurance Checks

### Example 13: Documentation Completeness Audit

**Scenario:** Verify documentation meets quality standards.

```bash
#!/bin/bash
# doc-quality-check.sh

DOC="$1"

echo "Documentation Quality Report: $DOC"
echo "======================================"
echo ""

# Check 1: Has frontmatter
if mddata info properties "$DOC" | grep -q "No frontmatter"; then
  echo "❌ FAIL: No frontmatter metadata"
else
  echo "✓ PASS: Has frontmatter metadata"
fi

# Check 2: Has title
if mddata info properties "$DOC" | grep -q "^title:"; then
  echo "✓ PASS: Has title property"
else
  echo "❌ FAIL: Missing title property"
fi

# Check 3: Minimum content requirement
block_count=$(mddata info blocks "$DOC" | wc -l)
if [ $block_count -ge 10 ]; then
  echo "✓ PASS: Sufficient content ($block_count blocks)"
else
  echo "⚠️  WARN: Limited content ($block_count blocks < 10 minimum)"
fi

# Check 4: Has code examples
code_count=$(mddata info blocks "$DOC" --type code_block | wc -l)
if [ $code_count -gt 0 ]; then
  echo "✓ PASS: Contains code examples ($code_count)"
else
  echo "⚠️  WARN: No code examples found"
fi

# Check 5: Section organization
section_count=$(mddata info sections "$DOC" | wc -l)
if [ $section_count -ge 3 ]; then
  echo "✓ PASS: Well-organized ($section_count sections)"
else
  echo "⚠️  WARN: Limited organization ($section_count sections)"
fi

echo ""
echo "Quality Score:"
passes=$(grep "✓ PASS" | wc -l)
total=5
percentage=$((passes * 100 / total))
echo "$passes/$total checks passed ($percentage%)"
```

### Example 14: Finding Empty or Stub Sections

**Scenario:** Identify sections that need content.

```bash
# Find sections with no blocks
echo "Empty sections that need content:"
mddata info sections documentation.md --blocks \
  | grep "(0 blocks)" \
  | awk '{print $1}' \
  | while read section; do
      echo "  - $section"
  done

# Find sections with only one paragraph (likely stubs)
echo ""
echo "Stub sections (single paragraph):"
mddata info sections documentation.md --paths | awk '{print $1}' | while read section; do
  block_count=$(mddata info blocks documentation.md --section "$section" | wc -l)
  para_count=$(mddata info blocks documentation.md --section "$section" --type paragraph | wc -l)

  if [ $block_count -eq 1 ] && [ $para_count -eq 1 ]; then
    echo "  - $section (expand this section)"
  fi
done
```

### Example 15: Link Validation Preparation

**Scenario:** Extract all links for validation.

```bash
# Extract all URLs for validation
echo "Extracting URLs for validation..."

# From link blocks
mddata info blocks documentation.md --type link \
  | grep -oE 'https?://[^ )]+' \
  | sort -u > urls_to_check.txt

# From code blocks (often contain URLs in examples)
mddata info blocks documentation.md --type code_block \
  | grep -oE 'https?://[^ )]+' \
  | sort -u >> urls_to_check.txt

# From paragraphs (inline links)
mddata extract json documentation.md \
  | grep -oE 'https?://[^ )]+' \
  | sort -u >> urls_to_check.txt

# Deduplicate
sort -u urls_to_check.txt -o urls_to_check.txt

echo "Found $(wc -l < urls_to_check.txt) unique URLs"
echo "URLs saved to: urls_to_check.txt"

# Optional: Quick check for broken links
while read url; do
  if curl --output /dev/null --silent --head --fail "$url"; then
    echo "✓ $url"
  else
    echo "❌ $url (may be broken)"
  fi
done < urls_to_check.txt
```

---

## Documentation Auditing

### Example 16: Change Detection Between Versions

**Scenario:** Compare documentation before and after updates.

```bash
# Extract structure from both versions
mddata info sections old-version.md --paths > old-structure.txt
mddata info sections new-version.md --paths > new-structure.txt

# Find added sections
echo "Added sections:"
diff old-structure.txt new-structure.txt | grep "^>" | sed 's/^> /  + /'

# Find removed sections
echo ""
echo "Removed sections:"
diff old-structure.txt new-structure.txt | grep "^<" | sed 's/^< /  - /'

# Compare content volume
old_blocks=$(mddata info blocks old-version.md | wc -l)
new_blocks=$(mddata info blocks new-version.md | wc -l)
diff_blocks=$((new_blocks - old_blocks))

echo ""
echo "Content changes:"
echo "  Old version: $old_blocks blocks"
echo "  New version: $new_blocks blocks"
echo "  Difference: $diff_blocks blocks"
```

### Example 17: Documentation Coverage Matrix

**Scenario:** Create a matrix showing content coverage across topics.

```bash
#!/bin/bash
# coverage-matrix.sh

TOPICS="authentication authorization api_keys webhooks rate_limiting"
DOCS=$(ls api-docs/*.md)

echo "Coverage Matrix"
echo "==============="
echo ""

printf "%-30s" "Document"
for topic in $TOPICS; do
  printf " %-15s" "$topic"
done
echo ""

for doc in $DOCS; do
  printf "%-30s" "$(basename $doc .md)"

  for topic in $TOPICS; do
    # Check if topic appears in section names or content
    if mddata info sections "$doc" --paths | grep -qi "$topic"; then
      printf " %-15s" "✓"
    else
      # Check in block content
      if mddata info blocks "$doc" | grep -qi "$topic"; then
        printf " %-15s" "~"
      else
        printf " %-15s" "✗"
      fi
    fi
  done
  echo ""
done

echo ""
echo "Legend: ✓=Full section, ~=Mentioned, ✗=Not covered"
```

### Example 18: Extract Metadata for Reporting

**Scenario:** Generate a documentation inventory report.

```bash
#!/bin/bash
# doc-inventory.sh

echo "Documentation Inventory Report"
echo "==============================="
echo "Generated: $(date)"
echo ""

for doc in docs/**/*.md; do
  echo "Document: $doc"
  echo "---"

  # Extract key metadata
  title=$(mddata info properties "$doc" | grep "^title:" | sed 's/title: //')
  author=$(mddata info properties "$doc" | grep "^author:" | sed 's/author: //')
  date=$(mddata info properties "$doc" | grep "^date:" | sed 's/date: //')

  # Count content
  sections=$(mddata info sections "$doc" | wc -l)
  blocks=$(mddata info blocks "$doc" | wc -l)
  code_blocks=$(mddata info blocks "$doc" --type code_block | wc -l)

  # Display
  echo "  Title: ${title:-N/A}"
  echo "  Author: ${author:-N/A}"
  echo "  Date: ${date:-N/A}"
  echo "  Sections: $sections"
  echo "  Blocks: $blocks (including $code_blocks code blocks)"

  # File size
  size=$(du -h "$doc" | cut -f1)
  echo "  Size: $size"
  echo ""
done
```

---

## Advanced Research Techniques

### Example 19: Deep Section Analysis

**Scenario:** Analyze specific section in detail.

```bash
SECTION="getting_started.installation"

echo "Deep analysis of section: $SECTION"
echo "===================================="

# Section info
echo "Section structure:"
mddata info sections guide.md --paths --blocks | grep "^$SECTION"

# Block breakdown
echo ""
echo "Content breakdown:"
for type in paragraph code_block list blockquote; do
  count=$(mddata info blocks guide.md --section "$SECTION" --type $type | wc -l)
  if [ $count -gt 0 ]; then
    echo "  $type: $count"
  fi
done

# Extract actual content for review
echo ""
echo "Content preview:"
mddata info blocks guide.md --section "$SECTION" --limit 3
```

### Example 20: Build Documentation Metrics Dashboard

**Scenario:** Create comprehensive metrics for documentation health.

```bash
#!/bin/bash
# doc-metrics.sh

DOC="${1:-README.md}"

echo "Documentation Metrics Dashboard"
echo "================================"
echo "Document: $DOC"
echo "Analyzed: $(date)"
echo ""

# Metadata completeness
echo "📊 Metadata"
echo "----------"
props=$(mddata info properties "$DOC" --verbose | grep -v "^$" | wc -l)
echo "Properties defined: $props"

# Content volume
echo ""
echo "📏 Content Volume"
echo "----------------"
sections=$(mddata info sections "$DOC" | wc -l)
blocks=$(mddata info blocks "$DOC" | wc -l)
words=$(mddata extract json "$DOC" | jq -r '.. | select(type == "string")' | wc -w)

echo "Sections: $sections"
echo "Blocks: $blocks"
echo "Approx. words: $words"

# Content composition
echo ""
echo "📝 Content Types"
echo "---------------"
for type in paragraph code_block list ordered_list blockquote; do
  count=$(mddata info blocks "$DOC" --type $type | wc -l)
  percentage=$((count * 100 / blocks))
  printf "%-15s: %3d (%2d%%)\n" "$type" "$count" "$percentage"
done

# Section depth
echo ""
echo "🌳 Structure"
echo "-----------"
max_depth=$(mddata info sections "$DOC" --paths | awk '{print $1}' | tr -cd '.\n' | wc -L)
echo "Maximum nesting depth: $max_depth"

# Tasks if present
if mddata info tasks "$DOC" 2>/dev/null | grep -q .; then
  echo ""
  echo "✅ Tasks"
  echo "-------"
  total_tasks=$(mddata info tasks "$DOC" | wc -l)
  completed_tasks=$(mddata info tasks "$DOC" --completed | wc -l)
  pending_tasks=$(mddata info tasks "$DOC" --pending | wc -l)

  echo "Total: $total_tasks"
  echo "Completed: $completed_tasks"
  echo "Pending: $pending_tasks"

  if [ $total_tasks -gt 0 ]; then
    completion=$((completed_tasks * 100 / total_tasks))
    echo "Completion rate: $completion%"
  fi
fi

# Health score
echo ""
echo "💚 Health Score"
echo "--------------"
score=0
max_score=5

# Has frontmatter
if [ $props -gt 0 ]; then
  score=$((score + 1))
  echo "✓ Has metadata"
else
  echo "✗ Missing metadata"
fi

# Sufficient content
if [ $blocks -ge 10 ]; then
  score=$((score + 1))
  echo "✓ Sufficient content"
else
  echo "✗ Limited content"
fi

# Has code examples
code_count=$(mddata info blocks "$DOC" --type code_block | wc -l)
if [ $code_count -gt 0 ]; then
  score=$((score + 1))
  echo "✓ Has code examples"
else
  echo "✗ No code examples"
fi

# Well organized
if [ $sections -ge 3 ]; then
  score=$((score + 1))
  echo "✓ Well organized"
else
  echo "✗ Limited organization"
fi

# Not too deep
if [ $max_depth -le 3 ]; then
  score=$((score + 1))
  echo "✓ Good structure depth"
else
  echo "⚠ Very deep nesting"
fi

percentage=$((score * 100 / max_score))
echo ""
echo "Overall Score: $score/$max_score ($percentage%)"

if [ $percentage -ge 80 ]; then
  echo "Grade: A (Excellent)"
elif [ $percentage -ge 60 ]; then
  echo "Grade: B (Good)"
elif [ $percentage -ge 40 ]; then
  echo "Grade: C (Adequate)"
else
  echo "Grade: D (Needs improvement)"
fi
```

---

## Summary

These examples demonstrate how to:

1. **Analyze structure** - Understand document organization
2. **Discover content** - Find specific information patterns
3. **Compare documents** - Ensure consistency across files
4. **Extract data** - Pull specific information for processing
5. **Audit quality** - Check documentation standards
6. **Generate reports** - Create comprehensive documentation metrics

Use these patterns as building blocks for custom documentation research workflows.
