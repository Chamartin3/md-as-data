# Template Cookbook

This cookbook provides practical recipes and patterns for common markdown template use cases. Each recipe includes a complete template and usage examples.

## Basic Templates

### Blog Post Template

A template for creating consistent blog posts with metadata.

```yaml
# blog_post.yaml
parameters:
  title:
    type: str
    required: true
    description: "Post title"
  author:
    type: str
    default: "Anonymous"
    description: "Post author"
  excerpt:
    type: str
    description: "Post excerpt/summary"
  tags:
    type: array
    item_type: str
    description: "Post tags"
  category:
    type: str
    description: "Post category"

changes:
  frontmatter:
    title: "{title}"
    author: "{author}"
    date: "{date}"
    excerpt: "{excerpt}"
    tags: "{tags}"
    category: "{category}"

  sections:
    - id: "content"
      content: |
        # {title}

        *By {author} on {date}*

        {excerpt}

        ## Introduction

        Start writing your post content here...

        ## Conclusion

        Wrap up your thoughts here.
```

**Usage:**

```bash
# Create a new blog post
mddata modify from-template post.md blog_post.yaml \
  -p title="My First Blog Post" \
  -p author="Jane Doe" \
  -p excerpt="An introduction to my blogging journey" \
  -p tags='["blogging", "personal"]' \
  -p category="Personal"
```

### Project README Template

Generate consistent project documentation.

```yaml
# project_readme.yaml
parameters:
  project_name:
    type: str
    required: true
  description:
    type: str
    required: true
  version:
    type: str
    default: "1.0.0"
  license:
    type: str
    default: "MIT"
  maintainer:
    type: str
    required: true

changes:
  frontmatter:
    title: "{project_name}"
    description: "{description}"
    version: "{version}"

  sections:
    - id: "header"
      content: |
        # {project_name}

        {description}

        **Version:** {version} | **License:** {license} | **Maintainer:** {maintainer}

    - id: "installation"
      content: |
        ## Installation

        ```bash
        # Installation instructions
        pip install {project_name}
        ```

    - id: "usage"
      content: |
        ## Usage

        ```python
        import {project_name}

        # Example usage
        ```

    - id: "contributing"
      content: |
        ## Contributing

        1. Fork the repository
        2. Create a feature branch
        3. Make your changes
        4. Submit a pull request

    - id: "license"
      content: |
        ## License

        This project is licensed under the {license} License.
```

**Usage:**

```bash
mddata modify from-template README.md project_readme.yaml \
  -p project_name="my-awesome-tool" \
  -p description="A tool that does amazing things" \
  -p maintainer="dev@example.com"
```

## Advanced Templates

### Meeting Notes Template

Structured template for meeting documentation with agenda and action items.

```yaml
# meeting_notes.yaml
parameters:
  meeting_title:
    type: str
    required: true
  date:
    type: str
    default: "{date}"
  time:
    type: str
    default: "{time}"
  attendees:
    type: array
    item_type: str
    description: "List of attendees"
  facilitator:
    type: str
    description: "Meeting facilitator"

changes:
  frontmatter:
    title: "Meeting: {meeting_title}"
    date: "{date}"
    attendees: "{attendees}"
    facilitator: "{facilitator}"

  sections:
    - id: "meeting_info"
      content: |
        # {meeting_title}

        **Date:** {date}  
        **Time:** {time}  
        **Facilitator:** {facilitator}

        ## Attendees
        {attendees}

    - id: "agenda"
      content: |
        ## Agenda

        1. Item 1
        2. Item 2
        3. Item 3

    - id: "discussion"
      content: |
        ## Discussion Notes

        ### Item 1
        - Discussion points here

        ### Item 2
        - Discussion points here

    - id: "action_items"
      content: |
        ## Action Items

        - [ ] Action item 1 - @responsible_person
        - [ ] Action item 2 - @responsible_person

    - id: "decisions"
      content: |
        ## Decisions Made

        - Decision 1
        - Decision 2
```

**Usage:**

```bash
mddata modify from-template meeting.md meeting_notes.yaml \
  -p meeting_title="Sprint Planning" \
  -p attendees='["Alice", "Bob", "Charlie"]' \
  -p facilitator="Alice"
```

### API Documentation Template

Template for documenting REST API endpoints.

```yaml
# api_endpoint.yaml
parameters:
  endpoint:
    type: str
    required: true
    description: "API endpoint path"
  method:
    type: str
    required: true
    pattern: "^(GET|POST|PUT|DELETE|PATCH)$"
    description: "HTTP method"
  description:
    type: str
    required: true
  version:
    type: str
    default: "v1"

changes:
  frontmatter:
    title: "API: {method} {endpoint}"
    endpoint: "{endpoint}"
    method: "{method}"
    version: "{version}"

  sections:
    - id: "overview"
      content: |
        # {method} {endpoint}

        {description}

        **Endpoint:** `{endpoint}`  
        **Method:** {method}  
        **Version:** {version}

    - id: "request"
      content: |
        ## Request

        ### Headers
        ```
        Content-Type: application/json
        Authorization: Bearer <token>
        ```

        ### Body
        ```json
        {
          "example": "request body"
        }
        ```

    - id: "response"
      content: |
        ## Response

        ### Success (200)
        ```json
        {
          "status": "success",
          "data": {}
        }
        ```

        ### Error (400)
        ```json
        {
          "status": "error",
          "message": "Error description"
        }
        ```

    - id: "examples"
      content: |
        ## Examples

        ### cURL
        ```bash
        curl -X {method} "{endpoint}" \\
          -H "Content-Type: application/json" \\
          -d '{"key": "value"}'
        ```

        ### Python
        ```python
        import requests

        response = requests.{method.lower()}('{endpoint}')
        print(response.json())
        ```
```

**Usage:**

```bash
mddata modify from-template api_docs.md api_endpoint.yaml \
  -p endpoint="/api/v1/users" \
  -p method="POST" \
  -p description="Create a new user account"
```

## Dynamic Templates

### Environment-Based Configuration

Templates that adapt based on environment variables.

```yaml
# env_config.yaml
parameters:
  component:
    type: str
    required: true

changes:
  frontmatter:
    component: "{component}"
    environment: "{env.NODE_ENV}"
    version: "{env.APP_VERSION}"
    build_date: "{date}"

  sections:
    - id: "configuration"
      content: |
        # {component} Configuration

        **Environment:** {env.NODE_ENV}  
        **Version:** {env.APP_VERSION}  
        **Built:** {build_date}

        ## Database
        - Host: {env.DB_HOST}
        - Port: {env.DB_PORT}
        - Name: {env.DB_NAME}

        ## Features
        - Debug: {env.DEBUG}
        - Logging: {env.LOG_LEVEL}
```

**Usage:**

```bash
# Set environment variables
export NODE_ENV=production
export APP_VERSION=2.1.0
export DB_HOST=prod-db.example.com
export DEBUG=false

mddata modify from-template config.md env_config.yaml \
  -p component="web-service"
```

### Conditional Content Templates

Use computed parameters and defaults for conditional content.

```yaml
# conditional_doc.yaml
parameters:
  doc_type:
    type: str
    required: true
    pattern: "^(guide|reference|tutorial)$"
  include_examples:
    type: bool
    default: true
  difficulty:
    type: str
    default: "beginner"
    pattern: "^(beginner|intermediate|advanced)$"

changes:
  frontmatter:
    title: "{doc_type} Document"
    type: "{doc_type}"
    difficulty: "{difficulty}"
    has_examples: "{include_examples}"

  sections:
    - id: "introduction"
      content: |
        # {doc_type} Introduction

        This is a {difficulty} level {doc_type}.

    - id: "content"
      content: |
        ## Main Content

        Content for {doc_type}...

        {include_examples}
```

**Usage:**

```bash
mddata modify from-template doc.md conditional_doc.yaml \
  -p doc_type="tutorial" \
  -p difficulty="intermediate"
```

## Batch Processing Templates

### Multiple File Generation

Create multiple related documents from a single template.

```yaml
# multi_file_template.yaml
parameters:
  base_name:
    type: str
    required: true
  versions:
    type: array
    item_type: str
    default: '["v1", "v2", "v3"]'

changes:
  frontmatter:
    name: "{base_name}"
    generated_at: "{now}"

  sections:
    - id: "versions"
      content: |
        # {base_name} Versions

        Available versions: {versions}

        Generated on: {now}
```

**Batch Usage Script:**

```bash
#!/bin/bash
# generate_docs.sh

components=("api" "web" "db")

for component in "${components[@]}"; do
  mddata modify from-template "${component}.md" multi_file_template.yaml \
    -p base_name="$component"
done
```

## Template Composition

### Base Template with Extensions

Create base templates that can be extended.

```yaml
# base_document.yaml
parameters:
  title:
    type: str
    required: true
  author:
    type: str
    default: "Documentation Team"

changes:
  frontmatter:
    title: "{title}"
    author: "{author}"
    created: "{date}"

  sections:
    - id: "header"
      content: "# {title}\n\n*Author: {author} | Created: {date}*"
```

```yaml
# technical_doc.yaml (extends base_document.yaml)
parameters:
  title:
    type: str
    required: true
  author:
    type: str
    default: "Engineering Team"
  component:
    type: str
    required: true

changes:
  frontmatter:
    title: "{title}"
    author: "{author}"
    component: "{component}"
    created: "{date}"

  sections:
    - id: "header"
      content: "# {title}\n\n*Component: {component} | Author: {author} | Created: {date}*"

    - id: "architecture"
      content: |
        ## Architecture

        Describe the {component} architecture here.

    - id: "api"
      content: |
        ## API Reference

        Document the {component} API here.
```

## Best Practices

### Template Organization

1. **Parameter Naming**: Use consistent naming conventions
2. **Default Values**: Provide sensible defaults where possible
3. **Validation**: Use constraints to prevent invalid inputs
4. **Documentation**: Include descriptions for all parameters
5. **Modularity**: Break complex templates into smaller, reusable parts

### Parameter Design

```yaml
# Good parameter design
parameters:
  user_name:
    type: str
    required: true
    min: 2
    max: 50
    pattern: "^[a-zA-Z0-9_]+$"
    description: "Username (2-50 chars, alphanumeric + underscore)"

  email:
    type: str
    required: true
    pattern: "^[^@]+@[^@]+\\.[^@]+$"
    description: "Valid email address"

  priority:
    type: str
    default: "medium"
    pattern: "^(low|medium|high)$"
    description: "Task priority level"
```

### Error Handling

Templates should handle edge cases gracefully:

```yaml
# Robust template with error handling
parameters:
  title:
    type: str
    required: true
    min: 1
    description: "Document title (required)"

  optional_section:
    type: str
    description: "Optional content section"

changes:
  sections:
    - id: "title"
      content: "# {title}"

    - id: "optional"
      content: "{optional_section}"
      policy: "replace"
```

### Template Testing

Always test templates with various parameter combinations:

```bash
# Test with minimal parameters
mddata modify from-template test.md template.yaml \
  -p title="Test" \
  --dry-run

# Test with all parameters
mddata modify from-template test.md template.yaml \
  -p title="Full Test" \
  -p author="Tester" \
  -p tags='["test", "example"]' \
  --dry-run

# Test parameter validation
mddata modify from-template test.md template.yaml \
  -p title=""  # Should fail validation
```