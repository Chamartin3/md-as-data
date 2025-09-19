# Markdown Templates

The mddata template system allows you to create reusable markdown document templates with parameterized content. Templates support parameter substitution, computed values, and flexible input sources.

## Template Format

Templates are defined in JSON or YAML format with two main sections:

```yaml
# Template structure
parameters:     # Parameter definitions with types and constraints
  param_name:
    type: str|int|float|bool|date|array
    required: true|false
    default: "default_value"
    description: "Parameter description"
    # Type-specific constraints
    min: 0
    max: 100
    pattern: "^[A-Z]+$"
    item_type: str  # For array parameters

changes:        # Document modifications in BatchChanges format
  frontmatter:
    title: "Document Title"
    author: "{author_name}"
  sections:
    - id: "introduction"
      content: "Welcome {user_name}!"
    - id: "details"
      content: "Created on {date}"
```

## Parameter Types

### Basic Types

- **`str`**: String values
- **`int`**: Integer numbers
- **`float`**: Floating-point numbers
- **`bool`**: Boolean values (true/false)
- **`date`**: Date strings (currently treated as strings)
- **`array`**: JSON arrays with optional item type validation

### Type Coercion

Parameters are automatically coerced from string input:

```yaml
parameters:
  count:
    type: int
  enabled:
    type: bool
  tags:
    type: array
    item_type: str
```

```bash
# CLI usage with type coercion
mddata modify from-template doc.md template.yaml \
  -p count=42 \
  -p enabled=true \
  -p tags='["tag1", "tag2"]'
```

## Parameter Constraints

### Numeric Constraints

```yaml
parameters:
  age:
    type: int
    min: 0
    max: 120
  score:
    type: float
    min: 0.0
    max: 100.0
```

### String Constraints

```yaml
parameters:
  username:
    type: str
    min: 3        # Minimum length
    max: 20       # Maximum length
    pattern: "^[a-zA-Z0-9_]+$"  # Regex pattern
```

### Array Constraints

```yaml
parameters:
  tags:
    type: array
    item_type: str  # All items must be strings
```

## Computed Parameters

Built-in computed parameters are available without explicit definition:

- **`{date}`**: Current date in ISO format (YYYY-MM-DD)
- **`{time}`**: Current time in ISO format (HH:MM:SS)
- **`{now}`**: Current datetime in ISO 8601 format
- **`{env.VAR_NAME}`**: Environment variable value

```yaml
changes:
  frontmatter:
    created_date: "{date}"
    created_time: "{time}"
    created_at: "{now}"
    environment: "{env.NODE_ENV}"
```

## Placeholder Substitution

Use `{parameter_name}` syntax for substitution:

```yaml
parameters:
  user_name:
    type: str
    required: true

changes:
  sections:
    - id: "greeting"
      content: "Hello {user_name}!"
```

### Escaping Literal Braces

To output literal braces, escape them with backslash:

```yaml
changes:
  sections:
    - id: "code"
      content: "Use \\{param\\} syntax for placeholders"
```

This outputs: `Use {param} syntax for placeholders`

## Parameter Sources

Parameters can be provided from multiple sources with precedence:

1. **CLI parameters** (highest precedence)
2. **Parameter file** (`--params` option)
3. **Template defaults**
4. **Computed parameters** (lowest precedence)

### CLI Parameters

```bash
# Direct values
mddata modify from-template doc.md template.yaml \
  -p name="John Doe" \
  -p age=25

# From files
mddata modify from-template doc.md template.yaml \
  -p content=@content.txt \
  -p config=@config.json

# Interactive input
mddata modify from-template doc.md template.yaml \
  -p password=-

# From piped stdin
echo "secret" | mddata modify from-template doc.md template.yaml \
  -p password=@-
```

### Parameter Files

Load all parameters from JSON/YAML files:

```bash
mddata modify from-template doc.md template.yaml \
  --params params.json
```

Parameter file format:

```json
{
  "name": "John Doe",
  "age": 25,
  "tags": ["developer", "admin"]
}
```

## Template Loading

### From Files

Templates are loaded with automatic format detection:

```bash
# JSON template
mddata modify from-template doc.md template.json

# YAML template
mddata modify from-template doc.md template.yaml
```

### From Stdin

Load templates from stdin with explicit format:

```bash
# YAML from stdin (default)
cat template.yaml | mddata modify from-template doc.md -

# JSON from stdin
cat template.json | mddata modify from-template doc.md - --format json
```

## Changes Section

The `changes` section uses the same format as `mddata modify from-json`:

```yaml
changes:
  frontmatter:
    title: "New Title"
    author: "{author_name}"
    tags: ["{tag1}", "{tag2}"]

  sections:
    - id: "introduction"
      content: "Welcome {user_name}!"
      policy: "replace"

    - id: "details"
      content: "Created: {date}\nModified: {now}"
      policy: "append"
```

### Section Policies

- **`update`** (default): Merge content while preserving subsections
- **`replace`**: Replace entire section content
- **`append`**: Add content to existing section

## Validation

Templates are validated at load time:

- **Parameter definitions**: Type, constraints, and defaults
- **Changes structure**: Must contain valid BatchChanges format
- **Placeholders**: All `{param}` references must be defined or computed
- **Required parameters**: Must be provided or have defaults

## Examples

### Simple Blog Post Template

```yaml
parameters:
  title:
    type: str
    required: true
    description: "Post title"
  author:
    type: str
    default: "Anonymous"
    description: "Post author"
  tags:
    type: array
    item_type: str
    description: "Post tags"

changes:
  frontmatter:
    title: "{title}"
    author: "{author}"
    date: "{date}"
    tags: "{tags}"

  sections:
    - id: "content"
      content: "# {title}\n\n*By {author} on {date}*\n\nStart writing your content here..."
```

Usage:

```bash
mddata modify from-template post.md blog_template.yaml \
  -p title="My First Post" \
  -p author="Jane Doe" \
  -p tags='["blog", "first-post"]'
```

### Project Documentation Template

```yaml
parameters:
  project_name:
    type: str
    required: true
  version:
    type: str
    default: "1.0.0"
  maintainer:
    type: str
    required: true

changes:
  frontmatter:
    title: "{project_name} Documentation"
    version: "{version}"
    maintainer: "{maintainer}"
    generated_at: "{now}"

  sections:
    - id: "overview"
      content: "# {project_name}\n\nVersion: {version}\nMaintainer: {maintainer}\n\n## Overview\n\nDescribe your project here."

    - id: "installation"
      content: "## Installation\n\n```bash\n# Installation instructions\n```"

    - id: "usage"
      content: "## Usage\n\n```bash\n# Usage examples\n```"
```

## Error Handling

The template system provides detailed error messages:

- **Missing required parameters**: Lists all missing parameters
- **Type conversion errors**: Shows expected vs actual types
- **Constraint violations**: Details min/max/pattern failures
- **Unknown placeholders**: Lists undefined parameter references
- **File loading errors**: Clear messages for missing or invalid files

## Dry Run Mode

Preview template changes without applying them:

```bash
mddata modify from-template doc.md template.yaml \
  -p title="Test" \
  --dry-run
```

This outputs the resolved changes in JSON format for review.