# Usage Guide

This document provides comprehensive examples for using the markdown-as-data library through both the CLI and SDK interfaces.

## Table of Contents

- [CLI Usage](#cli-usage)
- [SDK Usage](#sdk-usage)
- [Advanced Examples](#advanced-examples)
- [Common Use Cases](#common-use-cases)

---

# CLI Usage

The command-line interface provides quick access to parsing and exporting markdown documents.

## Basic Commands

### Parse and Export Full Document

```bash
# Export complete document as JSON
uv run mdasdata parse document.md

# Save output to file
uv run mdasdata parse document.md > output.json
```

**Example Output:**
```json
{
  "frontmatter": {
    "title": "My Document",
    "author": "John Doe",
    "date": "2024-01-15"
  },
  "content": {
    "id": "",
    "title": "",
    "level": 0,
    "path": "",
    "blocks": [],
    "subsections": [
      {
        "id": "introduction",
        "title": "Introduction",
        "level": 1,
        "path": "introduction",
        "blocks": [...]
      }
    ]
  }
}
```

### Extract Frontmatter Only

```bash
# Get only frontmatter properties
uv run mdasdata parse document.md --frontmatter-only
```

**Example Output:**
```json
{
  "title": "My Document",
  "author": "John Doe",
  "date": "2024-01-15",
  "tags": ["example", "documentation"]
}
```

### Extract Sections Only

```bash
# Get only content structure (no frontmatter)
uv run mdasdata parse document.md --sections-only
```

**Example Output:**
```json
{
  "sections": [
    {
      "id": "introduction",
      "title": "Introduction",
      "level": 1,
      "path": "introduction",
      "blocks": [...],
      "subsections": [...]
    }
  ],
  "sections_by_id": {
    "introduction": {...}
  }
}
```

## CLI Use Cases

### 1. Document Analysis

```bash
# Count sections in a document
uv run mdasdata parse doc.md --sections-only | jq '.sections | length'

# Extract all headings
uv run mdasdata parse doc.md --sections-only | jq -r '.sections[].title'

# Get document metadata
uv run mdasdata parse doc.md --frontmatter-only | jq -r '.title, .author, .date'
```

### 2. Content Migration

```bash
# Extract content for migration to another system
uv run mdasdata parse legacy-doc.md --sections-only > content-export.json

# Extract frontmatter for metadata processing
uv run mdasdata parse *.md --frontmatter-only | jq -s '.'
```

### 3. Batch Processing

```bash
# Process multiple documents
for file in docs/*.md; do
  echo "Processing $file"
  uv run mdasdata parse "$file" > "json/$(basename "$file" .md).json"
done

# Extract all document titles
find docs -name "*.md" -exec uv run mdasdata parse {} --frontmatter-only \; | jq -r '.title'
```

---

# SDK Usage

The Python SDK provides programmatic access to markdown documents as structured objects.

## Basic SDK Operations

### 1. Loading and Accessing Documents

```python
from md_as_data import MarkdownFile
# For advanced content manipulation, also available:
# from md_as_data import Section, Block, BlockType, HeadingLevel, SectionPolicy

# Load a markdown file
file = MarkdownFile('document.md')
doc = file.mddata

# Access frontmatter properties dynamically
print(f"Title: {doc.title}")
print(f"Author: {doc.author}")
print(f"Tags: {doc.tags}")

# Access with defaults
status = doc.get_property('status', 'draft')
version = doc.get_property('version', '1.0')
```

### 2. Navigating Content Structure

```python
# Access content tree
content = doc.content

# Get sections by ID (dynamic property access)
intro = content.introduction
overview = content.overview
conclusion = content.conclusion

# Get sections by path
purpose = content.get_section('introduction.purpose')
summary = content.get_section('conclusion.summary')

# List all available sections
print("Available sections:")
for section in content.get_all_sections():
    print(f"  - {section.title} ({section.path})")
```

### 3. Working with Sections and Blocks

```python
# Examine section details
intro = content.introduction
print(f"Section: {intro.title}")
print(f"Level: {intro.level.name}")  # H1, H2, etc.
print(f"Path: {intro.path}")
print(f"Blocks: {len(intro.blocks)}")
print(f"Subsections: {len(intro.subsections)}")

# Iterate through blocks
for block in intro.blocks:
    print(f"Block type: {block.type.value}")
    print(f"Content: {block.content[:100]}...")
    if block.metadata:
        print(f"Metadata: {block.metadata}")
```

### 4. Data Export and Serialization

```python
# Export to different formats
json_data = file.to_json()
markdown_text = file.to_markdown()

# Get structured data
frontmatter = file.mddata.frontmatter           # Direct property access
sections_data = file.mddata.get_sections()      # Structured data method
blocks_data = file.mddata.get_blocks()          # Structured data method

# Access content tree directly
all_sections = file.mddata.content.get_all_sections()
all_blocks = file.mddata.content.get_all_blocks()

# Export specific sections
intro_blocks = file.mddata.get_blocks('introduction')
intro_section = file.mddata.content.get_section('introduction')
```

## Advanced SDK Examples

The SDK provides powerful programmatic modification capabilities, including the new dynamic content setting API that allows you to modify sections using simple assignment syntax with automatic parsing and policy-based merging.

### 1. Document Modification

```python
from md_as_data import MarkdownFile, Section, Block, BlockType, HeadingLevel, SectionPolicy

# Load document
file = MarkdownFile('document.md')
doc = file.mddata

# Modify frontmatter
doc.status = "published"
doc.last_modified = "2024-01-20"
doc.version = "2.0"

# Add new content programmatically
new_section = Section("Updates", HeadingLevel.H2)

# Add paragraph
paragraph = Block(new_section.id, BlockType.PARAGRAPH,
                 "This section contains the latest updates.")
new_section.add_block(paragraph)

# Add list
updates = ["Fixed parsing bugs", "Added save functionality", "Improved docs"]
list_block = Block(new_section.id, BlockType.LIST, updates)
new_section.add_block(list_block)

# Add code block
code = "# Check version\nprint(f'Version: {doc.version}')"
code_block = Block(new_section.id, BlockType.CODE_BLOCK, code)
code_block.metadata['language'] = 'python'
new_section.add_block(code_block)

# Add to document
doc.content.add_section(new_section)

# Save changes
file.save()  # Save to original file
# Or save to new file
file.save_as('updated_document.md')
```

### 2. Dynamic Content Setting

The new content setting API allows you to dynamically add and modify sections using simple assignment syntax with various content formats and policies.

#### Setting Content with Strings

```python
from md_as_data import MarkdownFile

# Load document
file = MarkdownFile('document.md')
doc = file.mddata

# Set section content with raw markdown string
doc.introduction = """# Welcome

This is the introduction to our documentation.

- Point 1: Getting started
- Point 2: Basic concepts
- Point 3: Advanced features

```python
print("Hello, World!")
```
"""

# Verify section was created and content parsed
intro = doc.get_section("introduction")
print(f"Section: {intro.title}")
print(f"Blocks: {len(intro.blocks)}")  # Multiple blocks from parsed markdown

# Save changes
file.save()
```

#### Setting Content with Structured Data

```python
from md_as_data import MarkdownFile, SectionPolicy

file = MarkdownFile('document.md')
doc = file.mddata

# Set section using dictionary with raw content
section_data = {
    "id": "overview",
    "title": "Overview",
    "level": 1,
    "path": "overview",
    "content": "Overview text.\n\n- Item 1\n- Item 2",  # Raw markdown
    "subsections": None
}
doc.overview = section_data

# Set section using dictionary with structured blocks
blocks_data = {
    "id": "details",
    "title": "Details",
    "level": 2,
    "path": "details",
    "blocks": [  # Pre-structured blocks
        {
            "section_id": "details",
            "type": "paragraph",
            "content": "Detailed information here.",
            "metadata": {}
        },
        {
            "section_id": "details",
            "type": "list",
            "content": ["Feature A", "Feature B", "Feature C"],
            "metadata": {}
        }
    ],
    "subsections": []
}
doc.details = blocks_data

file.save()
```

#### Policy-Based Content Operations

The new system supports three mutation policies for controlling how content is merged:

```python
from md_as_data import MarkdownFile, SectionPolicy

file = MarkdownFile('document.md')
doc = file.mddata

# Create initial section
doc.updates = "Original content\n\n- Original item"

# UPDATE policy (default) - replaces content and specified subsections
doc.updates = ("Updated content\n\n- Updated item", SectionPolicy.UPDATE)

# APPEND policy - adds content without removing existing
doc.updates = ("Additional content\n\n- Additional item", SectionPolicy.APPEND)

# REPLACE policy - completely replaces section and all subsections
doc.updates = ("Replacement content", SectionPolicy.REPLACE)

# View the final content
updates_section = doc.get_section("updates")
print(f"Final content has {len(updates_section.blocks)} blocks")

file.save()
```

#### Frontmatter vs Section Content Detection

The system intelligently distinguishes between frontmatter properties and section content:

```python
from md_as_data import MarkdownFile

file = MarkdownFile('document.md')
doc = file.mddata

# Simple values become frontmatter properties
doc.author = "John Doe"
doc.version = "2.1"
doc.status = "published"

# Complex content becomes sections
doc.changelog = """## Version 2.1

- Added new features
- Fixed important bugs
- Updated documentation
"""

doc.api_reference = {
    "id": "api",
    "title": "API Reference",
    "level": 1,
    "path": "api",
    "content": "Complete API documentation here..."
}

# Check what was created
print("Frontmatter properties:", list(doc.frontmatter.keys()))
print("Section IDs:", doc.content.keys)

file.save()
```

#### Error Handling and Validation

```python
from md_as_data import MarkdownFile, SectionPolicy

file = MarkdownFile('document.md')
doc = file.mddata

try:
    # This raises ValueError - cannot set None content
    doc.invalid_section = None
except ValueError as e:
    print(f"Content error: {e}")

try:
    # This raises ValueError - cannot specify both formats
    invalid_data = {
        "id": "bad",
        "title": "Bad",
        "level": 1,
        "path": "bad",
        "content": "text",  # Raw markdown
        "blocks": []       # Structured blocks - conflict!
    }
    doc.bad_section = invalid_data
except ValueError as e:
    print(f"Format error: {e}")

# If trying to set existing section with simple value
doc.introduction = "Simple intro text"  # Creates section initially
try:
    # This raises NotImplementedError - can't overwrite with simple value
    doc.introduction = "Different text"
except NotImplementedError as e:
    print(f"Update error: {e}")

    # But policy-based updates work fine
    doc.introduction = ("Updated intro text", SectionPolicy.UPDATE)
```

### 3. Content Analysis

```python
from collections import Counter
from md_as_data import MarkdownFile

file = MarkdownFile('document.md')
content = file.mddata.content

# Analyze block types
all_blocks = content.get_all_blocks()
block_counts = Counter(block.type.value for block in all_blocks)
print("Block distribution:")
for block_type, count in block_counts.items():
    print(f"  {block_type}: {count}")

# Find sections with most content
section_sizes = [(s.title, len(s.blocks)) for s in content.get_all_sections()]
section_sizes.sort(key=lambda x: x[1], reverse=True)
print("\nSections by content size:")
for title, size in section_sizes[:5]:
    print(f"  {title}: {size} blocks")

# Extract all code blocks with language info
for section in content.get_all_sections():
    for block in section.blocks:
        if block.type == BlockType.CODE_BLOCK:
            language = block.metadata.get('language', 'none')
            print(f"Code in {section.title} ({language}):")
            print(f"  {block.content[:50]}...")
```

### 4. Parser Extension

```python
import tempfile
from md_as_data import MarkdownFile, Block, BlockType
from md_as_data.tokens import TokenType

def custom_hr_handler(token, state):
    """Custom handler for horizontal rule tokens."""
    block = Block(
        state["current_section"].id,
        BlockType.PARAGRAPH,
        "---HORIZONTAL RULE---"
    )
    block.metadata["language"] = "horizontal_rule"
    state["current_section"].add_block(block)
    return 1

# Create document with horizontal rules
content = """---
title: Test Document
---

# Section One

First paragraph.

---

Second paragraph after horizontal rule.
"""

with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
    f.write(content)
    temp_file = f.name

# Load file and register custom handler
file = MarkdownFile(temp_file)
file.register_handler(TokenType.HR, custom_hr_handler)

# Re-parse with custom handler
data = file._parser.parse(file._raw_content)
file.mddata = MarkdownData(data)

# Verify custom blocks were created
for section in file.mddata.content.get_all_sections():
    for block in section.blocks:
        if "horizontal_rule" in str(block.metadata):
            print(f"Custom HR block found: {block.content}")
```

## Common Use Cases

### 1. Documentation Site Generator

```python
import os
from pathlib import Path
from md_as_data import MarkdownFile

def process_docs_directory(docs_path: str, output_path: str):
    """Convert markdown docs to structured JSON for site generator."""
    docs_dir = Path(docs_path)
    output_dir = Path(output_path)
    output_dir.mkdir(exist_ok=True)

    for md_file in docs_dir.glob("**/*.md"):
        # Load and parse
        file = MarkdownFile(str(md_file))

        # Extract metadata and structure
        data = {
            'metadata': file.mddata.frontmatter,
            'sections': file.mddata.get_sections(),
            'toc': [s.title for s in file.mddata.content.get_all_sections()],
            'word_count': sum(len(str(b.content).split())
                            for b in file.mddata.content.get_all_blocks())
        }

        # Save structured data
        output_file = output_dir / f"{md_file.stem}.json"
        with open(output_file, 'w') as f:
            import json
            json.dump(data, f, indent=2)

        print(f"Processed: {md_file} -> {output_file}")

# Usage
process_docs_directory('docs/', 'site/data/')
```

### 2. Content Migration Tool

```python
from md_as_data import MarkdownFile

def migrate_frontmatter(file_path: str, field_mappings: dict):
    """Migrate frontmatter fields according to mapping."""
    file = MarkdownFile(file_path)
    doc = file.mddata

    # Apply field mappings
    for old_field, new_field in field_mappings.items():
        if hasattr(doc, old_field):
            value = getattr(doc, old_field)
            setattr(doc, new_field, value)
            # Remove old field
            del doc.frontmatter[old_field]

    # Add migration metadata
    doc.migrated_at = "2024-01-20"
    doc.migration_version = "1.0"

    # Save changes
    file.save()
    print(f"Migrated: {file_path}")

# Usage
mappings = {
    'date': 'created_date',
    'modified': 'updated_date',
    'category': 'section'
}

for md_file in Path('content/').glob('*.md'):
    migrate_frontmatter(str(md_file), mappings)
```

### 3. Content Validation

```python
from md_as_data import MarkdownFile, HeadingLevel

def validate_document_structure(file_path: str):
    """Validate document follows content guidelines."""
    file = MarkdownFile(file_path)
    doc = file.mddata
    issues = []

    # Check required frontmatter
    required_fields = ['title', 'author', 'date']
    for field in required_fields:
        if not hasattr(doc, field):
            issues.append(f"Missing required field: {field}")

    # Check heading hierarchy
    sections = doc.content.get_all_sections()
    for section in sections:
        if section.level == HeadingLevel.ROOT:
            continue

        # No sections should skip levels (H1 -> H3)
        if section.parent_path:
            parent = doc.content.get_section(section.parent_path.split('.')[-1])
            if parent and section.level.value - parent.level.value > 1:
                issues.append(f"Heading level skip in section: {section.title}")

        # Sections should have content
        if not section.blocks and not section.subsections:
            issues.append(f"Empty section: {section.title}")

    # Check for minimum content
    total_blocks = len(doc.content.get_all_blocks())
    if total_blocks < 3:
        issues.append(f"Document too short: only {total_blocks} blocks")

    return issues

# Usage
for md_file in Path('content/').glob('*.md'):
    issues = validate_document_structure(str(md_file))
    if issues:
        print(f"\n{md_file}:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print(f"✅ {md_file}: Valid")
```

---

## New Features Summary

### Dynamic Content Setting API

The library now provides a powerful dynamic content setting API that allows you to modify markdown documents using simple assignment syntax:

- **Multiple Content Formats**: Set content using raw markdown strings, structured dictionaries, or Section objects
- **Automatic Format Detection**: The system intelligently distinguishes between frontmatter properties and section content
- **Policy-Based Merging**: Three policies (UPDATE, APPEND, REPLACE) give you precise control over content merging
- **Intelligent Parsing**: Raw markdown content is automatically parsed into structured blocks with full CommonMark support

### Key Components

- **`SectionPolicy`** enum: Control how content merges (UPDATE/APPEND/REPLACE)
- **Dynamic Assignment**: Use `doc.section_name = content` syntax for intuitive content setting
- **Type Safety**: Built-in validation prevents common errors and ensures data integrity
- **Backward Compatibility**: All existing APIs continue to work unchanged

### Quick Reference

```python
from md_as_data import MarkdownFile, SectionPolicy

doc = MarkdownFile('file.md').mddata

# Frontmatter (simple values)
doc.author = "Jane Doe"
doc.version = "2.0"

# Section content (complex content)
doc.introduction = "# Welcome\n\nThis is the introduction..."
doc.overview = {"id": "overview", "title": "Overview", "content": "..."}
doc.updates = ("New content", SectionPolicy.APPEND)
```

---

This usage guide covers the most common patterns and use cases for working with markdown-as-data. For more interactive examples and development patterns, see [SDK_EXAMPLES.md](SDK_EXAMPLES.md).