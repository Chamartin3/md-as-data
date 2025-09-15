# Markdown as Data

A Python library for treating markdown files as structured data objects with programmatic manipulation capabilities.

## Overview

Transform markdown documents into structured data that you can navigate, query, and modify programmatically. Perfect for documentation systems, content management, and automated markdown processing.

## Features

- **Parse markdown into structured objects** with hierarchical sections and typed blocks
- **Dynamic property access** to frontmatter and content sections
- **Path-based navigation** through document structure (`section.subsection.item`)
- **Query sections** with validation, fuzzy matching, and ambiguity detection
- **Filter blocks** by type and section with unified API
- **High-level setters** for sections with automatic heading generation
- **Round-trip serialization** - markdown → objects → markdown (preserves formatting)
- **Type-safe API** with comprehensive TypedDict interfaces and NamedTuple returns
- **Extensible parser** with custom token handlers
- **CLI and SDK** interfaces for different use cases

## Quick Start

### Installation

```bash
# Clone and install with uv (recommended)
git clone <repository-url>
cd mdasdata
uv sync --dev

# Or install from PyPI (when published)
pip install md-as-data
```

### Basic Usage

```python
from md_as_data import MarkdownFile

# Load and parse a markdown file
file = MarkdownFile('document.md')
doc = file.mddata

# Access frontmatter properties dynamically
print(doc.title)        # "My Document"
print(doc.author)       # "John Doe"
print(doc.tags)         # ["python", "markdown"]

# Navigate content structure
intro = doc.content.introduction
overview = doc.content.introduction.overview
conclusion = doc.content.get_section('conclusion.summary')

# Query sections with validation
query = doc.query_section('introduction')
if query.section:
    print(f"Found: {query.section.title}")

# Filter blocks
paragraphs = doc.find_blocks(block_type='paragraph')
intro_blocks = doc.find_blocks(section_id='introduction')

# Modify content with high-level setter
doc.set_section('updates', 'New update content')
doc.set_section('intro.overview', 'Overview text')  # Creates subsection

# Modify frontmatter and save
doc.status = "published"
doc.last_modified = "2024-01-20"
file.save()
```

## Project Structure

```
md_as_data/
   src/
      md_as_data/
          __init__.py         # Public API exports
          models.py           # Pure data models and type definitions
          source.py           # File I/O operations (MarkdownFile)
          data.py             # Data manipulation and dynamic access (MarkdownData)
          processor.py        # Markdown parsing and serialization
      cli/
          cli.py              # Command-line interface
   examples/                   # Example markdown files and demos
   tests/                      # Test suite
   scripts/                    # Development scripts
   pyproject.toml             # Project configuration
   README.md                  # This file
   CLAUDE.md                  # Development guidelines
   USAGE.md                   # Detailed usage examples
   SDK_EXAMPLES.md            # Interactive development examples
```

## Core Concepts

### Document Structure
- **MarkdownFile**: Main entry point for file operations
- **MarkdownData**: Parsed document with frontmatter and content
- **ContentTree**: Hierarchical structure of sections
- **Section**: Individual content sections with blocks and subsections
- **Block**: Individual content elements (paragraphs, code, lists, etc.)

### Path-Based Navigation
```python
# Access sections by ID
intro = content.introduction

# Access by hierarchical path
purpose = content.get_section('introduction.purpose')
summary = content.get_section('conclusion.summary')

# Get all available paths
paths = content.paths  # ['introduction', 'introduction.purpose', 'conclusion', 'conclusion.summary']
```

### Dynamic Property Access
```python
# Frontmatter properties
doc.title = "Updated Title"
doc.tags.append("new-tag")

# Content sections
doc.introduction = "New introduction text"
doc.conclusion.summary = "Updated summary"
```

## CLI Usage

### Parse to JSON
```bash
# Parse entire document
mdasdata parse document.md

# Pretty print with syntax highlighting
mdasdata parse document.md --pretty

# Extract only frontmatter
mdasdata parse document.md --frontmatter

# Extract only section structure
mdasdata parse document.md --sections

# Save to file
mdasdata parse document.md --output parsed.json
```

### Document Info
```bash
# Show document statistics
mdasdata info document.md
```

## Advanced Usage

### Content Mutation with Policies

```python
from md_as_data import MarkdownFile, SectionPolicy

file = MarkdownFile('document.md')
doc = file.mddata

# Append content to existing section
doc.append_to_section('introduction', 'Additional paragraph')

# Replace entire section content
doc.replace_section('conclusion', 'Completely new conclusion')

# Update section while preserving subsections
doc.update_section('methodology', 'Updated methodology content')
```

### Custom Token Handlers

```python
from md_as_data import MarkdownProcessor, TokenType

processor = MarkdownProcessor()

# Add custom handler for specific token types
def custom_code_handler(token):
    # Custom processing for code blocks
    return modified_token

processor.token_handlers[TokenType.FENCE] = custom_code_handler
```

## Development

### Running Tests
```bash
uv run pytest
```

### Linting
```bash
uv run python scripts/lint.py
```

### Type Checking
```bash
uv run pyright
```

## Architecture

The library follows a clean modular architecture:

- **models.py**: Pure data structures with no dependencies
- **processor.py**: Handles markdown parsing and serialization
- **data.py**: Provides the main interface for document manipulation
- **source.py**: Manages file I/O operations
- **cli/**: Command-line interface implementation

This separation ensures:
- Clear responsibilities for each module
- No circular dependencies
- Easy testing and maintenance
- Extensibility for custom use cases

## Contributing

Contributions are welcome! Please ensure:
- All tests pass
- Code follows the project's style guidelines
- Type hints are provided for all public APIs
- Documentation is updated as needed

## License

[License information to be added]