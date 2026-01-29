# DataTemplate Design Patterns

Common datatemplate patterns for markdown documents with parameters (YAML/JSON format).

## Pattern 1: Simple Document

Minimal datatemplate for basic documents.

```yaml
parameters:
  title:
    type: str
    required: true
    description: "Document title"

  date:
    type: str
    required: true
    description: "Creation date (YYYY-MM-DD)"
    default: "{{current_date}}"

frontmatter:
  title: "{{title}}"
  date: "{{date}}"

content:
  id: ""
  title: ""
  level: 0
  path: ""
  blocks: []
  children:
    - id: content
      title: Content
      level: 2
      path: content
      blocks:
        - section_id: content
          type: paragraph
          content: "Main content here."
          metadata: {}
      children: []
```

## Pattern 2: Documentation DataTemplate

Complete documentation datatemplate with installation and usage sections.

```yaml
parameters:
  title:
    type: str
    required: true
    description: "Documentation title"

  author:
    type: str
    required: true
    description: "Author name"

  version:
    type: str
    required: true
    description: "Version number"
    default: "1.0.0"

  date:
    type: str
    required: true
    description: "Creation date (YYYY-MM-DD)"
    default: "{{current_date}}"

  package_name:
    type: str
    required: true
    description: "Package name for installation"

frontmatter:
  title: "{{title}}"
  author: "{{author}}"
  version: "{{version}}"
  date: "{{date}}"
  tags: ["documentation"]

content:
  id: ""
  title: ""
  level: 0
  path: ""
  blocks: []
  children:
    - id: overview
      title: Overview
      level: 2
      path: overview
      blocks:
        - section_id: overview
          type: paragraph
          content: "This documentation covers {{title}}."
          metadata: {}
      children: []

    - id: installation
      title: Installation
      level: 2
      path: installation
      blocks:
        - section_id: installation
          type: code_block
          content: "pip install {{package_name}}"
          metadata:
            language: bash
      children: []

    - id: usage
      title: Usage
      level: 2
      path: usage
      blocks:
        - section_id: usage
          type: paragraph
          content: "Basic usage examples for {{package_name}}."
          metadata: {}
      children:
        - id: examples
          title: Examples
          level: 3
          path: usage.examples
          blocks:
            - section_id: examples
              type: code_block
              content: "# Example code here"
              metadata:
                language: python
          children: []
```

## Pattern 3: Blog Post Template

Blog post with introduction, content, and conclusion.

```yaml
parameters:
  title:
    type: str
    required: true
    description: "Blog post title"

  author:
    type: str
    required: true
    description: "Author name"

  date:
    type: str
    required: true
    description: "Publication date (YYYY-MM-DD)"
    default: "{{current_date}}"

  tags:
    type: list
    required: false
    description: "Post tags"
    default: []

  excerpt:
    type: str
    required: false
    description: "Brief summary of the post"

  status:
    type: str
    required: false
    description: "Post status"
    default: "draft"
    options: ["draft", "review", "published", "archived"]

frontmatter:
  title: "{{title}}"
  author: "{{author}}"
  date: "{{date}}"
  tags: "{{tags}}"
  excerpt: "{{excerpt}}"
  status: "{{status}}"

content:
  id: ""
  title: ""
  level: 0
  path: ""
  blocks: []
  children:
    - id: introduction
      title: Introduction
      level: 2
      path: introduction
      blocks:
        - section_id: introduction
          type: paragraph
          content: "Engaging opening paragraph for {{title}}."
          metadata: {}
      children: []

    - id: content
      title: Main Content
      level: 2
      path: content
      blocks:
        - section_id: content
          type: paragraph
          content: "Main article content goes here."
          metadata: {}
      children: []

    - id: conclusion
      title: Conclusion
      level: 2
      path: conclusion
      blocks:
        - section_id: conclusion
          type: paragraph
          content: "Summary and key takeaways."
          metadata: {}
      children: []
```

## Pattern 4: API Documentation

Template for API endpoint documentation.

```yaml
parameters:
  endpoint:
    type: str
    required: true
    description: "API endpoint path"
    default: "/api/endpoint"

  method:
    type: str
    required: true
    description: "HTTP method"
    default: "GET"
    options: ["GET", "POST", "PUT", "DELETE", "PATCH"]

  version:
    type: str
    required: false
    description: "API version"
    default: "v1"

  description:
    type: str
    required: true
    description: "Brief endpoint description"

frontmatter:
  endpoint: "{{endpoint}}"
  method: "{{method}}"
  version: "{{version}}"
  description: "{{description}}"

content:
  id: ""
  title: ""
  level: 0
  path: ""
  blocks: []
  children:
    - id: overview
      title: Overview
      level: 2
      path: overview
      blocks:
        - section_id: overview
          type: paragraph
          content: "{{description}}"
          metadata: {}
      children: []

    - id: request
      title: Request
      level: 2
      path: request
      blocks: []
      children:
        - id: parameters
          title: Parameters
          level: 3
          path: request.parameters
          blocks:
            - section_id: parameters
              type: code_block
              content: "{\n  \"param1\": \"value\",\n  \"param2\": \"value\"\n}"
              metadata:
                language: json
          children: []

    - id: response
      title: Response
      level: 2
      path: response
      blocks:
        - section_id: response
          type: code_block
          content: "{\n  \"status\": \"success\",\n  \"data\": {}\n}"
          metadata:
            language: json
      children: []
```

## Block Type Examples

Use these block examples in your templates:

### Paragraph Block
```yaml
- section_id: examples
  type: paragraph
  content: "This is a paragraph."
  metadata: {}
```

### Code Block
```yaml
- section_id: examples
  type: code_block
  content: "def example():\n    return True"
  metadata:
    language: python
```

### Unordered List
```yaml
- section_id: examples
  type: list
  content:
    - "Item 1"
    - "Item 2"
    - "Item 3"
  metadata: {}
```

### Ordered List
```yaml
- section_id: examples
  type: ordered_list
  content:
    - "Step 1"
    - "Step 2"
    - "Step 3"
  metadata: {}
```

### Task List
```yaml
- section_id: examples
  type: task_list
  content:
    - "Task 1"
    - "Task 2"
    - "Task 3"
  metadata:
    tasks:
      - content: "Task 1"
        symbol: "x"
      - content: "Task 2"
        symbol: " "
      - content: "Task 3"
        symbol: " "
```

### Blockquote
```yaml
- section_id: examples
  type: blockquote
  content: "This is a quoted passage."
  metadata: {}
```

## Using These Patterns

1. **Copy the pattern** that matches your needs
2. **Customize parameters** to fit your use case
3. **Add or remove sections** as needed
4. **Fill in content** with your specific information
5. **Test the template** with real data

## Combining Patterns

You can combine sections from different patterns:

```yaml
# Take parameters from Blog Post
parameters:
  title: "..."
  author: "..."

# Add sections from Documentation
content:
  children:
    - # Introduction from Blog Post
    - # Installation from Documentation
    - # Content from Blog Post
```
