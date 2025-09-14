# Command-Line Interface

This document describes the modern, modular command-line interface (CLI) for the markdown-as-data library, built with Typer.

## Installation

The CLI is available after installing the library:

```bash
# Clone and install with uv (recommended)
git clone <repository-url>
cd mdasdata
uv sync --dev
```

## Command Structure

All CLI commands follow the pattern:
```bash
uv run mdasdata <file_path> <command> [subcommand] [options]
```

The `file_path` is always required as the first argument since all operations need a markdown file to work with.

---

## Information Commands

Query and inspect markdown file structure using the `info` command group.

### Default Info (Quick Summary)

Display basic file statistics:

```bash
uv run mdasdata document.md info summary
uv run mdasdata document.md info summary --verbose
```

**Output:**
```
File: document.md
Frontmatter properties: 4
Sections: 8
Total blocks: 15
Block types:
  • paragraph: 10
  • code_block: 3
  • list: 2
```

### Properties

List all frontmatter properties:

```bash
uv run mdasdata document.md info properties
uv run mdasdata document.md info properties --verbose
```

**Options:**
- `--verbose, -v`: Show full property values instead of truncated

### Sections

Show document section hierarchy:

```bash
uv run mdasdata document.md info sections
uv run mdasdata document.md info sections --blocks --paths
```

**Options:**
- `--blocks, -b`: Show block count for each section
- `--paths/--no-paths, -p/-P`: Show/hide section paths (default: show)

**Sample Output:**
```
#1 Introduction (introduction)
  #2 Overview (introduction.overview)
  #2 Getting Started (introduction.getting_started)
#1 User Guide (user_guide)
  #2 Basic Usage (user_guide.basic_usage)
    #3 Examples (user_guide.basic_usage.examples)
```

### Blocks

List document content blocks with filtering:

```bash
uv run mdasdata document.md info blocks
uv run mdasdata document.md info blocks --type paragraph --limit 5
```

**Options:**
- `--type, -t`: Filter by block type (paragraph, list, code_block, etc.)
- `--limit, -l`: Limit number of blocks shown

---

## Modification Commands

Modify document content and properties using the `modify` command group.

### Set Property

Modify frontmatter properties:

```bash
# Set simple string property
uv run mdasdata document.md modify set-property title "New Title"

# Set complex property with JSON parsing
uv run mdasdata document.md modify set-property tags '["new", "tags"]' --json

# Auto-detect JSON (fallback to string)
uv run mdasdata document.md modify set-property version "2.1.0"
```

**Arguments:**
- `key`: Property key to set
- `value`: Property value (string or JSON)

**Options:**
- `--json, -j`: Force parse value as JSON

### Remove Property

Remove frontmatter properties:

```bash
uv run mdasdata document.md modify remove-property draft
```

### Set Section

Modify or create section content:

```bash
# Update section with default policy (update)
uv run mdasdata document.md modify set-section intro "New introduction content"

# Replace entire section
uv run mdasdata document.md modify set-section intro "Replacement content" --policy replace

# Append to existing section
uv run mdasdata document.md modify set-section intro "Additional content" --policy append

# Create new subsection under existing section
uv run mdasdata document.md modify set-section introduction.new_section "New subsection content"
```

**Arguments:**
- `section_id`: Section ID or path to modify/create
- `content`: New section content

**Options:**
- `--policy, -p`: Section modification policy (update|replace|append)

**Section Policies:**
- `update` (u): Merge content while preserving subsections (default)
- `replace` (r): Replace entire section content
- `append` (a): Add content to existing section

**Path-Based Access:**
- Use dot-separated paths: `parent.child.grandchild`
- Create new subsections by specifying non-existent paths under existing sections
- Automatic heading level calculation based on parent section

### Bulk Changes from JSON

Apply multiple changes from JSON input:

```bash
# From file
uv run mdasdata document.md modify from-json changes.json

# From stdin
echo '{"frontmatter": {"status": "published"}}' | uv run mdasdata document.md modify from-json -

# Dry run (preview changes)
uv run mdasdata document.md modify from-json changes.json --dry-run
```

**JSON Format:**
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

---

## Export Commands

Export structured data in various formats using the `export` command group.

### JSON Export

Export complete document structure:

```bash
# Basic JSON export
uv run mdasdata document.md export json

# Pretty-printed with syntax highlighting
uv run mdasdata document.md export json --pretty

# Save to file
uv run mdasdata document.md export json --output document.json
```

### YAML Export

Export as YAML format:

```bash
uv run mdasdata document.md export yaml
uv run mdasdata document.md export yaml --output document.yaml
```

### Frontmatter Only

Export only frontmatter properties:

```bash
# Export as JSON (default)
uv run mdasdata document.md export frontmatter

# Export as YAML
uv run mdasdata document.md export frontmatter --format yaml
```

**Options:**
- `--format, -f`: Output format (json|yaml)
- `--output, -o`: Output file path (default: stdout)

---

## Advanced Features

### Error Handling

The CLI provides comprehensive error handling and validation:

**Invalid Paths:**
```
Error: Section 'invalid.path' not found.
Error: Use 'info sections --paths' to see available section paths.
```

**Ambiguous References:**
```
Error: Ambiguous section reference 'intro' matches multiple sections:
Error:   - Introduction (path: main.introduction)
Error:   - API Introduction (path: api.introduction)
Error: Please use a unique path to identify the section.
```

**Parent Validation:**
```
Error: Parent path 'nonexistent.section' not found for new section 'child'.
Error: Use 'info sections --paths' to see available section paths.
```

### Path Resolution

- **Exact Paths**: `final_notes.conclusion.summary`
- **Unique Partial Paths**: `conclusion` (if only one exists)
- **New Subsection Creation**: `existing.parent.new_child`
- **Heading Level Preservation**: Automatically maintains correct heading levels

### Rich Output

- **Colorized Terminal Output**: Using Rich library for enhanced readability
- **Hierarchical Display**: Proper indentation for section structures
- **Highlighted Paths**: Important path components are highlighted
- **Progress Indicators**: Clear success/error messaging

---

## Integration Examples

### Shell Scripting

Batch processing multiple files:

```bash
# Process all markdown files in a directory
for file in docs/*.md; do
  echo "Processing $file"
  uv run mdasdata "$file" export json --output "json/$(basename "$file" .md).json"
done

# Update version across multiple documents
for file in docs/*.md; do
  uv run mdasdata "$file" modify set-property version "2.0"
done
```

### Workflow Automation

```bash
#!/bin/bash
# Automated documentation update workflow

DOC_FILE="user-guide.md"

# Update document metadata
uv run mdasdata "$DOC_FILE" modify set-property last_updated "$(date -I)"
uv run mdasdata "$DOC_FILE" modify set-property status "published"

# Add changelog entry
uv run mdasdata "$DOC_FILE" modify set-section changelog.latest "$(date -I): Updated user guide" --policy append

# Generate JSON export
uv run mdasdata "$DOC_FILE" export json --pretty --output dist/user-guide.json

echo "Documentation update complete!"
```

### Command Output Integration

Pipe command output directly into markdown documents:

```bash
# Git integration - capture commit information
git log --oneline -10 | uv run mdasdata CHANGELOG.md modify from-json - <<< '{
  "frontmatter": {"last_commit": "'$(git rev-parse --short HEAD)'", "updated": "'$(date -I)'"},
  "sections": [{"id": "recent_commits", "content": "## Recent Commits\n\n```\n'$(git log --oneline -10)'\n```", "policy": "replace"}]
}'

# System information
uname -a | uv run mdasdata system-info.md modify from-json - <<< '{
  "frontmatter": {"system": "'$(uname -s)'", "kernel": "'$(uname -r)'"},
  "sections": [{"id": "system_details", "content": "## System Details\n\n```\n'$(uname -a)'\n```", "policy": "replace"}]
}'

# Package information
pip list --format=json | uv run mdasdata requirements.md modify from-json - <<< '{
  "sections": [{"id": "current_packages", "content": "## Current Packages\n\n```json\n'$(pip list --format=json)'\n```", "policy": "replace"}]
}'

# API data integration
curl -s https://api.github.com/repos/user/repo/releases/latest | \
jq '{frontmatter: {latest_release: .tag_name, release_date: .published_at}, sections: [{id: "latest_release", content: ("## Latest Release: " + .tag_name + "\n\nPublished: " + .published_at + "\n\n" + .body), policy: "replace"}]}' | \
uv run mdasdata README.md modify from-json -

# Build and CI/CD integration
npm run build 2>&1 | uv run mdasdata BUILD_LOG.md modify from-json - <<< '{
  "frontmatter": {"build_status": "completed", "build_time": "'$(date -I)'"},
  "sections": [{"id": "build_output", "content": "## Build Output\n\n```\n'$(npm run build 2>&1 | head -20)'\n```", "policy": "replace"}]
}'

# Test results integration
pytest --json-report --json-report-file=/tmp/test-report.json
cat /tmp/test-report.json | jq '{
  frontmatter: {
    tests_passed: .summary.passed,
    tests_failed: .summary.failed,
    test_date: .created
  },
  sections: [{
    id: "test_summary",
    content: ("## Test Results\n\n- Passed: " + (.summary.passed | tostring) + "\n- Failed: " + (.summary.failed | tostring) + "\n- Duration: " + (.duration | tostring) + "s"),
    policy: "replace"
  }]
}' | uv run mdasdata TEST_REPORT.md modify from-json -

# Docker container status
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | uv run mdasdata DOCKER_STATUS.md modify from-json - <<< '{
  "frontmatter": {"updated": "'$(date -I)'"},
  "sections": [{"id": "container_status", "content": "## Container Status\n\n```\n'$(docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}")'\n```", "policy": "replace"}]
}'

# Database backup and documentation
pg_dump --schema-only mydb | uv run mdasdata DATABASE_SCHEMA.md modify from-json - <<< '{
  "frontmatter": {"schema_updated": "'$(date -I)'", "database": "mydb"},
  "sections": [{"id": "schema_definition", "content": "## Database Schema\n\n```sql\n'$(pg_dump --schema-only mydb | head -50)'\n```", "policy": "replace"}]
}'
```

### Data Processing with jq

Extract and process structured data:

```bash
# Count sections by level
uv run mdasdata doc.md export json | jq '.sections[] | group_by(.level) | map({level: .[0].level, count: length})'

# Extract all section titles
uv run mdasdata doc.md export json | jq -r '.sections[].title'

# Find sections containing specific content
uv run mdasdata doc.md export json | jq -r '.sections[] | select(.content | contains("example")) | .title'

# Export frontmatter from multiple files
find docs -name "*.md" -exec uv run mdasdata {} export frontmatter \; | jq -s '.'

# Complex data transformation and reinjection
uv run mdasdata source.md export json | \
jq '{
  frontmatter: (.frontmatter + {processed_date: now | strftime("%Y-%m-%d")}),
  sections: [.sections[] | select(.level <= 2) | {id, content: (.content + "\n\n*Auto-processed*"), policy: "replace"}]
}' | \
uv run mdasdata target.md modify from-json -
```

### Continuous Integration Integration

```yaml
# GitHub Actions example (.github/workflows/docs.yml)
name: Update Documentation
on: [push, pull_request]
jobs:
  update-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python and uv
        run: |
          curl -LsSf https://astral.sh/uv/install.sh | sh
          uv sync
      - name: Update build info
        run: |
          echo '{"frontmatter": {"build_number": "${{ github.run_number }}", "commit_sha": "${{ github.sha }}", "updated": "'$(date -I)'"}}' | \
          uv run mdasdata docs/BUILD_INFO.md modify from-json -
      - name: Update API docs
        run: |
          # Extract API endpoints and update documentation
          grep -r "app.get\|app.post" src/ | \
          awk '{print $2}' | \
          jq -R -s 'split("\n") | map(select(. != "")) | {sections: [{id: "api_endpoints", content: ("## API Endpoints\n\n" + (map("- " + .) | join("\n"))), policy: "replace"}]}' | \
          uv run mdasdata docs/API.md modify from-json -
```

---

## Quick Reference

### Common Commands

```bash
# File overview
uv run mdasdata doc.md info

# Section structure
uv run mdasdata doc.md info sections --paths

# Update frontmatter
uv run mdasdata doc.md modify set-property title "New Title"

# Modify section
uv run mdasdata doc.md modify set-section intro "New content"

# Export as JSON
uv run mdasdata doc.md export json --pretty
```

### Help System

Get detailed help for any command:

```bash
uv run mdasdata --help
uv run mdasdata doc.md info --help
uv run mdasdata doc.md modify --help
uv run mdasdata doc.md modify set-section --help
uv run mdasdata doc.md export --help
```

---

## Performance & Limits

- **File Size**: Efficiently handles files up to several MB
- **Memory Usage**: Scales with document complexity (sections and blocks)
- **Processing Speed**: Sub-second response for typical documentation files
- **Output Format**: Optimized JSON/YAML streaming for large documents

The modern CLI provides a comprehensive interface for markdown manipulation with strong type safety, validation, and user-friendly error handling.