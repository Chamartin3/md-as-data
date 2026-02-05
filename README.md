# Markdown as Data

A Python library for treating markdown files as structured data objects with programmatic manipulation capabilities.

## Overview

Transform markdown documents into structured data that you can navigate, query, and modify programmatically. Perfect for documentation systems, content management, and automated markdown processing.

### Migration from Older Versions

If you're upgrading from an older version of mddata, see the [Migration Guide](docs/MIGRATION_GUIDE.md) for help transitioning to the new unified `write` command structure.

## Features

- **Unified write interface** - Single command for creating and modifying documents with intelligent auto-detection
- **Parse markdown into structured objects** with hierarchical sections and typed blocks
- **Dynamic property access** to frontmatter and content sections
- **Path-based navigation** through document structure (`section.subsection.item`)
- **Query sections** with validation, fuzzy matching, and ambiguity detection
- **Filter blocks** by type and section with unified API
- **High-level setters** for sections with automatic heading generation
- **Round-trip serialization** - markdown → objects → markdown (preserves formatting)
- **Type-safe API** with comprehensive TypedDict interfaces and NamedTuple returns
- **Extensible parser** with custom token handlers
- **Template system** with parameterized document generation and substitution
- **Schema validation** - Generate and validate documents against schemas
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

### Create a markdown file from data

```bash
# From JSON data
mddata write from -d document.json -o new.md

# From template with parameters
mddata write from -f template.yaml -p title="My Doc" -o new.md

# Generate template from schema
mddata write from -s schema.json -o template.md
```

### Modify an existing file

```bash
# Auto-detects modify mode when file exists
mddata write from -d changes.json existing.md
```

### Extract structured data

```bash
# Extract to JSON
mddata extract json document.md

# Extract to YAML
mddata extract yaml document.md
```

### Basic Usage (Python API)

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

### Create and Modify Documents

The `write` command provides a unified interface for all document operations:

```bash
# Create new document from data
mddata write --data document.json --output new.md

# Modify existing document
mddata write --data changes.json existing.md

# Create from template with parameters
mddata write --data template.yaml -p title="My Doc" -p author="John" --output doc.md

# Generate template from schema
mddata write --schema schema.json --output template.md

# Render to stdout for preview
mddata write --data document.json
```

### Extract and Query Documents

```bash
# Extract to JSON/YAML
mddata extract json document.md --pretty --output data.json
mddata extract yaml document.md --output data.yaml

# Query document structure
mddata info summary document.md
mddata info sections document.md --paths
mddata info properties document.md --verbose

# Extract only frontmatter
mddata extract frontmatter document.md --format yaml
```

### Granular Modifications

```bash
# Modify individual properties
mddata write set-property document.md title "New Title"
mddata write set-property document.md tags '["new", "tags"]' --json

# Modify individual sections
mddata write set-section document.md intro "Updated content"
mddata write set-section document.md intro "Replace all" --policy replace

# Remove properties
mddata write remove-property document.md draft
```

### Schema Validation

Infer and validate document schemas in JSON or YAML format:

```bash
# Infer schema in JSON format (default)
mddata schema infer document.md --output doc-schema.json --pretty

# Infer schema in YAML format (better readability)
mddata schema infer document.md --format yaml --output doc-schema.yaml

# Validate document against schema (format auto-detected)
mddata schema validate document.md doc-schema.json --verbose
mddata schema validate document.md doc-schema.yaml --verbose

# View schema information
mddata schema info doc-schema.json
```

**Format Compatibility:**
Both JSON and YAML formats are fully supported and interchangeable. Use YAML for better readability when manually editing schemas, or JSON for programmatic processing.

## Advanced Usage

### Content Mutation with Policies

```python
from mddata import MarkdownFile, UpdatePolicy

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