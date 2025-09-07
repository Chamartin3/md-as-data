---
title: "Complex Document Example"
author: "Jane Smith"
date: "2024-01-20"
version: "2.1.0"
status: "published"
tags: ["complex", "demo", "advanced"]
categories: ["documentation", "examples"]
description: "A comprehensive example showcasing various markdown features"
---

# Complex Document Structure

This document demonstrates various markdown features and nested structures.

## Table of Contents

- Introduction
- Features Overview
- Code Examples
- Data Structures
- Conclusion

## Introduction

Welcome to this comprehensive markdown example. This document showcases:

- Multiple heading levels
- Various content types
- Complex nesting
- Rich metadata

### Purpose

The purpose of this document is to test the parsing capabilities.

### Scope

This covers most common markdown patterns.

## Features Overview

Here are the key features demonstrated:

1. **Frontmatter**: YAML metadata at the top
2. **Headings**: Multiple levels of organization
3. **Lists**: Both ordered and unordered
4. **Code**: Inline and block code samples
5. **Text Formatting**: Various text styles

### Technical Details

The parser handles:

- Nested sections
- Multiple paragraph blocks
- Code blocks with language specification
- List processing

## Code Examples

### Python Code

```python
class MarkdownParser:
    def __init__(self):
        self.content = ""

    def parse(self, text):
        return self.process(text)
```

### JavaScript Code

```javascript
function parseMarkdown(content) {
    const parser = new MarkdownParser();
    return parser.parse(content);
}
```

### Shell Commands

```bash
# Install dependencies
pip install markdown-it-py
pip install python-frontmatter

# Run the parser
python -m md_as_data parse document.md
```

## Data Structures

The following data structures are used:

- **MarkdownDocument**: Core document object
- **Section**: Hierarchical content sections
- **Block**: Individual content blocks
- **ContentTree**: Tree structure for navigation

### Implementation Notes

> This is a blockquote explaining the implementation approach.
>
> The parser uses a token-based approach for maximum flexibility.

## Advanced Features

### Nested Lists

1. First level item
   - Nested bullet point
   - Another nested item
     - Even deeper nesting
2. Second level item
   - More nesting
3. Final item

### Complex Paragraphs

This paragraph contains multiple sentences. It demonstrates how the parser handles longer text blocks with various punctuation marks, numbers like 123, and special characters like @#$%.

Another paragraph follows immediately after.

## Performance Considerations

The parser is designed for:

- Fast processing of large documents
- Memory-efficient tree structures
- Scalable content organization

# Final Notes
## Conclusion

This complex example demonstrates the full capabilities of the markdown-as-data parser.

### Summary

Key achievements:

- Comprehensive parsing
- Structured data output
- Maintainable architecture

### Next Steps

Future enhancements may include:

1. Table support
2. Extended metadata
3. Custom block types
4. Export formats

### References

For more information, see the project documentation.
