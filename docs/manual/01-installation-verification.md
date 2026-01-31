# Installation & Verification

## Overview

`mddata` is a command-line tool that treats markdown files as structured data objects. It allows you to query, extract, validate, modify, and generate markdown documents programmatically.

## Installation

Install the project and its dependencies using uv:

```bash
uv sync --dev
```

This installs the project in development mode along with all development dependencies (pytest, ruff, pyright).

## Verifying Installation

Check that `mddata` is installed correctly by running:

```bash
mddata --version
```

You should see output showing the installed version:

```
mddata version 0.1.0
```

## Getting Help

Display available commands:

```bash
mddata --help
```

Get help for a specific command:

```bash
mddata info --help
mddata extract --help
mddata schema --help
```

## Core Concepts

Understanding these concepts is essential for working with `mddata`:

### Properties (Frontmatter)

Properties are metadata stored at the beginning of a markdown file in YAML format, enclosed by `---` delimiters:

```markdown
---
title: "User Guide"
author: "John Doe"
version: 1.0
tags: ["documentation", "guide"]
---
```

Properties can be:
- **Strings**: `title: "User Guide"`
- **Numbers**: `version: 1.0`
- **Booleans**: `published: true`
- **Lists**: `tags: ["doc", "guide"]`
- **Objects**: `author: {name: "John", email: "john@example.com"}`

### Sections

Sections are hierarchical divisions of content defined by headings:

```markdown
# Introduction

This is the introduction section.

## Getting Started

This is a subsection of Introduction.

### Prerequisites

This is a sub-subsection.

# Configuration

This is a new top-level section.
```

**Section Structure:**
- Each heading creates a new section
- Section hierarchy follows heading levels (# → ## → ###)
- Sections are identified by IDs (slugified heading text)
- Sections can contain subsections, forming a tree structure

**Section IDs:**
- Generated from heading text: "Getting Started" → `getting_started`
- Used for programmatic access: `doc.query_section('getting_started')`
- Support path notation: `introduction.getting_started.prerequisites`

### Blocks

Blocks are individual content units within sections:

```markdown
# Section Title

This is a paragraph block.

Another paragraph block.

- This is a list block
- With multiple items

```python
# This is a code block
print("Hello, world!")
```

> This is a blockquote block.
```

**Block Types:**
- `paragraph` - Regular text paragraphs
- `heading` - Section headings (# ## ###)
- `list` - Ordered and unordered lists
- `code_block` - Fenced code blocks
- `blockquote` - Quoted text (>)
- `thematic_break` - Horizontal rules (---)
- `html_block` - Raw HTML content

**Block Attributes:**
- `type` - The block type (paragraph, list, etc.)
- `content` - The actual text/code content
- `section_id` - Which section contains this block
- `attributes` - Additional metadata (language for code blocks, etc.)

## Document Structure Representation

A complete markdown document is represented as:

```
MarkdownDocument
├── Frontmatter (Properties)
│   ├── title: "Document Title"
│   ├── author: "Author Name"
│   └── tags: ["tag1", "tag2"]
└── Content (Sections & Blocks)
    ├── Section: "introduction"
    │   ├── Block: paragraph
    │   ├── Block: list
    │   └── Subsection: "getting_started"
    │       ├── Block: paragraph
    │       └── Block: code_block
    └── Section: "configuration"
        ├── Block: paragraph
        └── Block: paragraph
```

## Example Document

Here's a complete example showing all concepts:

```markdown
---
title: "API Documentation"
version: 2.1
status: "published"
tags: ["api", "reference"]
---

# Introduction

Welcome to the API documentation. This paragraph is a block.

## Overview

The API provides RESTful endpoints. This is another block.

- Feature 1
- Feature 2
- Feature 3

# Authentication

All requests require an API key.

```python
# Code block example
import requests
headers = {"Authorization": "Bearer YOUR_TOKEN"}
```

# Endpoints

## Users API

Manage user resources.
```

**Structure breakdown:**
- **Properties**: `title`, `version`, `status`, `tags`
- **Sections**: `introduction`, `introduction.overview`, `authentication`, `endpoints`, `endpoints.users_api`
- **Blocks**: 7 blocks total (paragraphs, list, code block) distributed across sections

## Next Steps

Now that you understand the basic concepts, you can:

1. [Query document metadata](02-querying-metadata.md) - Learn to inspect document structure
2. [Extract data](03-extracting-metadata.md) - Export documents to JSON/YAML
3. [Validate schemas](04-schema-management.md) - Enforce document structure
4. [Generate documents](05-markdown-generation.md) - Create files from templates
5. [Transform data](06-data-transformation.md) - Modify documents programmatically
