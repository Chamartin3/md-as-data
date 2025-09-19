"""Global pytest fixtures and configuration."""

import tempfile
from pathlib import Path
from typing import Any

import pytest

from mddata import MarkdownFile


@pytest.fixture
def sample_frontmatter() -> dict[str, Any]:
    """Sample frontmatter data for tests."""
    return {
        "title": "Test Document",
        "author": "Test Author",
        "date": "2023-01-01",
        "tags": ["test", "sample"],
        "published": True,
    }


@pytest.fixture
def sample_markdown_content() -> str:
    """Sample markdown content without frontmatter."""
    return """# Introduction

This is a sample introduction paragraph.

## Getting Started

Here are the basic steps:

1. First step
2. Second step
3. Third step

### Code Example

```python
def hello_world():
    print("Hello, World!")
```

## Advanced Topics

> This is a blockquote with important information.

- Bullet point one
- Bullet point two
- Bullet point three

### Links and Images

[Example Link](https://example.com)

![Sample Image](image.jpg "Sample alt text")
"""


@pytest.fixture
def sample_markdown_with_frontmatter(
    sample_frontmatter: dict[str, Any], sample_markdown_content: str
) -> str:
    """Complete markdown document with frontmatter and content."""
    frontmatter_lines = ["---"]
    for key, value in sample_frontmatter.items():
        if isinstance(value, str):
            frontmatter_lines.append(f'{key}: "{value}"')
        elif isinstance(value, list):
            frontmatter_lines.append(f"{key}: {value}")
        else:
            frontmatter_lines.append(f"{key}: {value}")
    frontmatter_lines.append("---")
    frontmatter_lines.append("")

    return "\n".join(frontmatter_lines) + sample_markdown_content


@pytest.fixture
def temp_markdown_file(sample_markdown_with_frontmatter: str):
    """Create a temporary markdown file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(sample_markdown_with_frontmatter)
        temp_path = f.name

    yield Path(temp_path)

    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def markdown_file(temp_markdown_file: Path) -> MarkdownFile:
    """MarkdownFile instance loaded from temporary file."""
    return MarkdownFile(str(temp_markdown_file))


@pytest.fixture
def simple_markdown_content() -> str:
    """Simple markdown content for basic tests."""
    return """# Simple Title

Just a paragraph of text.

## Subsection

Another paragraph here.
"""


@pytest.fixture
def empty_markdown_content() -> str:
    """Empty markdown content."""
    return ""


@pytest.fixture
def markdown_with_nested_sections() -> str:
    """Markdown with deeply nested sections."""
    return """# Level 1

Content for level 1.

## Level 2

Content for level 2.

### Level 3

Content for level 3.

#### Level 4

Content for level 4.

##### Level 5

Content for level 5.

###### Level 6

Content for level 6.
"""


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def complex_frontmatter() -> dict[str, Any]:
    """Complex frontmatter with various data types for mutation testing."""
    return {
        "title": "Complex Test Document",
        "author": "Test Author",
        "tags": ["python", "testing", "markdown"],
        "published": False,
        "version": 1.0,
        "metadata": {
            "source": "test_suite",
            "priority": "high",
            "config": {"database": "localhost", "port": 5432},
        },
        "contributors": ["Alice", "Bob"],
        "dates": {"created": "2023-01-01", "modified": "2023-12-01"},
    }


@pytest.fixture
def document_with_duplicates() -> str:
    """Markdown document with duplicate section names for ambiguity testing."""
    return """# Main Document

Main document content.

## Introduction

First introduction.

### Overview

First overview section.

## Configuration

Main configuration section.

### Introduction

Second introduction - duplicate name!

### Overview

Second overview - another duplicate!

## Examples

Examples section.

### Code Examples

Code examples here.

## Testing

Testing section.

### Code Examples

More code examples - duplicate name again!
"""


@pytest.fixture
def multi_level_document() -> str:
    """Document with all heading levels for level preservation testing."""
    return """# Level 1 Main Title

Level 1 content here.

## Level 2 Section Title

Level 2 content here.

### Level 3 Subsection Title

Level 3 content here.

#### Level 4 Sub-subsection Title

Level 4 content here.

##### Level 5 Deep Section Title

Level 5 content here.

###### Level 6 Maximum Depth Title

Level 6 content here.
"""
