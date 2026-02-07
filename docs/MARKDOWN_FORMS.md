# Markdown Forms

Markdown Forms are parameterized document templates that allow you to create structured markdown documents with validated inputs. Forms define parameters with types, validation rules, and defaults, enabling consistent document generation with user-provided values.

## Overview

Forms provide:
- **Parameterized Templates** - Define reusable document structures with placeholders
- **Type Safety** - Strong typing with validation for str, int, float, bool, array types
- **Validation Rules** - Constraints including min/max, patterns, enums, and array validation
- **Computed Values** - Automatic resolution of date, time, and environment variables
- **CLI Integration** - Fill forms from command line with parameter validation

## Use Cases

- **Bug Reports** - Standardized bug reporting with validated severity, priority, and descriptions
- **Meeting Notes** - Consistent meeting documentation with attendees, action items, and decisions
- **Project Specifications** - Structured project docs with required fields and validation
- **Status Reports** - Weekly/monthly reports with standard sections and computed dates
- **Documentation Templates** - API docs, guides, and READMEs with validated structure

## Quick Start

### Create a Simple Form

**File:** `blog-post.yaml`

```yaml
parameters:
  title:
    type: str
    required: true
    min: 5
    max: 100
    description: "Blog post title (5-100 characters)"

  author:
    type: str
    required: false
    default: "{env.USER}"
    description: "Post author"

  tags:
    type: array
    item_type: str
    required: false
    default: []
    description: "Post tags"

frontmatter:
  title: "{title}"
  author: "{author}"
  date: "{date}"
  tags: "{tags}"

sections:
  - id: introduction
    content: |
      # {title}

      **Author:** {author}
      **Published:** {date}

      ## Introduction

      [Write your introduction here]
```

### Fill the Form

```bash
mddata write from -f blog-post.yaml \
  -p title="Getting Started with mddata" \
  -p 'tags=["tutorial", "markdown"]' \
  -o my-post.md
```

## Form Structure

### Complete Form Specification

```yaml
# Parameter definitions (what users fill in)
parameters:
  param_name:
    type: str|int|float|bool|array|date
    required: true|false
    default: value
    description: "Human-readable description"

    # Validation constraints
    min: number              # Min value/length
    max: number              # Max value/length
    pattern: "regex"         # Regex validation (strings)

    # Enum validation
    enum: [val1, val2]       # Allowed values
    enum_strict: true|false  # Error vs warning on invalid
    enum_descriptions:       # Help text for each value
      val1: "Description 1"
      val2: "Description 2"

    # Array-specific
    item_type: str           # Type of array items
    min_items: number        # Minimum array length
    max_items: number        # Maximum array length
    unique_items: true       # Require unique values
    item_enum: [v1, v2]      # Allowed item values
    item_enum_strict: true   # Strict item validation
    item_pattern: "regex"    # Pattern for array items

# Document frontmatter (uses parameters)
frontmatter:
  property: "{param_name}"
  computed: "{date}"

# Document content - Two approaches:

# Approach 1: Raw Markdown Content
sections:
  - id: section_id
    content: |
      ## Section Title
      Markdown content with {param_name} placeholders

# Approach 2: Structured YAML (Recommended)
sections:
  - id: section_id
    title: "Section Title"  # Clear separation
    level: 2                # Heading level (1-6)
    policy: append          # Update policy
    content: |              # Content without heading
      Content with {param_name} placeholders
```

## Section Formats: Raw Markdown vs Structured YAML

Forms support two ways to define section content:

### Raw Markdown Content (Simple)

Embed complete markdown including headings in the `content` field:

```yaml
sections:
  - id: "meetings"
    content: |
      ## {title} - {date}

      ### Attendees
      {attendees_list}

      ### Notes
      Meeting notes here
    policy: append
```

**Pros:**
- Quick and simple for basic forms
- Familiar markdown syntax
- Good for simple, flat structures

**Cons:**
- Heading levels are hardcoded in content
- Less structured and harder to parse
- Mixing structure and content

### Structured YAML (Recommended)

Separate structure (title, level) from content:

```yaml
sections:
  - id: "meetings"
    title: "{title} - {date}"  # Section title
    level: 2                    # H2 heading
    policy: append
    content: |                  # Content only (no heading)
      **Attendees:** {attendees}

      ### Decisions
      {decisions_list}

      ### Action Items
      {action_items_list}
```

**Pros:**
- Clear separation of structure and content
- Title and level are explicit and parameterizable
- Easier to validate and process
- More maintainable for complex forms

**Cons:**
- Slightly more verbose
- Requires understanding of level values (1-6)

### When to Use Each

**Use Raw Markdown when:**
- Creating simple, one-off forms
- Headings don't need parameterization
- Quick prototyping

**Use Structured YAML when:**
- Section titles contain parameters (e.g., `title: "{name} - {date}"`)
- Building reusable form libraries
- Need clear structure for tooling
- Creating complex multi-level forms
- Want explicit control over heading levels

## Parameter Types

### String (`str`)

Text values with optional length and pattern constraints.

```yaml
parameters:
  title:
    type: str
    required: true
    min: 5              # Minimum 5 characters
    max: 100            # Maximum 100 characters
    pattern: "^[A-Z]"   # Must start with capital
    description: "Document title"
```

**Usage:**
```bash
mddata write from -f form.yaml -p title="My Document" -o doc.md
```

### Integer (`int`)

Whole numbers with optional range constraints.

```yaml
parameters:
  priority:
    type: int
    required: true
    min: 1
    max: 5
    description: "Priority level (1-5)"
```

**Usage:**
```bash
mddata write from -f form.yaml -p priority=3 -o doc.md
```

### Float (`float`)

Decimal numbers with optional range constraints.

```yaml
parameters:
  completion:
    type: float
    required: false
    default: 0.0
    min: 0.0
    max: 100.0
    description: "Completion percentage"
```

**Usage:**
```bash
mddata write from -f form.yaml -p completion=75.5 -o doc.md
```

### Boolean (`bool`)

True/false values.

```yaml
parameters:
  published:
    type: bool
    required: false
    default: false
    description: "Publication status"
```

**Usage:**
```bash
# Accepts: true, false, 1, 0, yes, no (case-insensitive)
mddata write from -f form.yaml -p published=true -o doc.md
```

### Array (`array`)

Lists with optional item type and validation.

```yaml
parameters:
  tags:
    type: array
    item_type: str
    required: false
    default: []
    min_items: 1        # At least 1 tag
    max_items: 5        # At most 5 tags
    unique_items: true  # No duplicates
    description: "Document tags"
```

**Usage:**

Arrays can be passed in multiple formats:

```bash
# JSON array syntax (explicit)
mddata write from -f form.yaml \
  -p 'tags=["python", "tutorial"]' \
  -o doc.md

# Comma-separated values (shell-friendly)
mddata write from -f form.yaml \
  -p tags="python, tutorial, beginner" \
  -o doc.md

# From JSON file
echo '["python", "tutorial"]' > tags.json
mddata write from -f form.yaml \
  -p tags=@tags.json \
  -o doc.md

# From parameter file
mddata write from -f form.yaml --params params.yaml -o doc.md
```

**Array Placeholders:**

Arrays support two automatic placeholder formats in templates:

- **`{param_name}`** - Renders as comma-separated string: `"python, tutorial, beginner"`
- **`{param_name_list}`** - Auto-generated markdown bullet list:
  ```markdown
  - python
  - tutorial
  - beginner
  ```

**Example:**
```yaml
parameters:
  attendees:
    type: array
    item_type: str

sections:
  - id: meeting
    content: |
      ## Attendees

      {attendees_list}

      Present: {attendees}
```

**Result:**
```markdown
## Attendees

- Alice
- Bob
- Charlie

Present: Alice, Bob, Charlie
```

### Date (`date`)

Date values in ISO format (YYYY-MM-DD).

```yaml
parameters:
  due_date:
    type: date
    required: false
    default: "{date}"    # Uses current date
    description: "Due date"
```

**Usage:**
```bash
mddata write from -f form.yaml -p due_date="2025-12-31" -o doc.md
```

## Validation Rules

### Enum Validation

Restrict values to a predefined set.

```yaml
parameters:
  status:
    type: str
    enum: [draft, review, published]
    enum_strict: true  # Error on invalid (default)
    enum_descriptions:
      draft: "Work in progress"
      review: "Under review"
      published: "Published and live"
    description: "Document status"
```

**Non-strict mode** (allows custom values with warning):
```yaml
parameters:
  category:
    type: str
    enum: [bug, feature, docs]
    enum_strict: false  # Warning instead of error
    description: "Category (predefined or custom)"
```

### Array Constraints

**Length constraints:**
```yaml
parameters:
  tags:
    type: array
    min_items: 2    # At least 2 required
    max_items: 10   # At most 10 allowed
```

**Uniqueness:**
```yaml
parameters:
  collaborators:
    type: array
    unique_items: true  # No duplicates
```

**Item enum validation:**
```yaml
parameters:
  labels:
    type: array
    item_enum: [bug, feature, enhancement, docs]
    item_enum_strict: true
    item_enum_descriptions:
      bug: "Bug fix"
      feature: "New feature"
      enhancement: "Improvement"
      docs: "Documentation"
```

**Item pattern validation:**
```yaml
parameters:
  emails:
    type: array
    item_pattern: "^[^@]+@[^@]+\\.[^@]+$"
    description: "Valid email addresses"
```

### Pattern Validation

Regex validation for strings and array items.

```yaml
parameters:
  email:
    type: str
    pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
    description: "Valid email address"

  version:
    type: str
    pattern: "^\\d+\\.\\d+\\.\\d+$"
    description: "Semantic version (e.g., 1.2.3)"
```

## Computed Parameters

Computed parameters are automatically resolved without user input.

### Built-in Computed Parameters

**`{date}` - Current Date**
```yaml
frontmatter:
  created: "{date}"  # Output: 2025-11-19
```

**`{time}` - Current Time**
```yaml
frontmatter:
  timestamp: "{time}"  # Output: 14:30:45
```

**`{now}` - Current DateTime**
```yaml
frontmatter:
  generated_at: "{now}"  # Output: 2025-11-19T14:30:45
```

### Environment Variables

Access environment variables using `{env.VAR_NAME}` syntax.

```yaml
parameters:
  author:
    type: str
    default: "{env.USER}"  # Defaults to $USER

frontmatter:
  author: "{author}"
  home: "{env.HOME}"
  shell: "{env.SHELL}"
```

**Common variables:**
- `{env.USER}` - Current username
- `{env.HOME}` - Home directory
- `{env.PWD}` - Current directory
- `{env.EDITOR}` - Default editor

## Parameter Sources & Precedence

Parameters are resolved in order (highest priority last):

1. **Computed parameters** (`{date}`, `{env.USER}`)
2. **Form defaults** (defined in `parameters.default`)
3. **Parameter files** (`--params file.yaml`)
4. **CLI arguments** (`-p key=value`) ← **Highest priority**

### CLI Parameters

```bash
mddata write from -f form.yaml \
  -p title="My Document" \
  -p author="Alice" \
  -p priority=1 \
  -o doc.md
```

### Parameter Files

**File:** `params.yaml`
```yaml
title: "My Document"
author: "Alice"
priority: 1
tags:
  - tutorial
  - beginner
```

**Usage:**
```bash
mddata write from -f form.yaml --params params.yaml -o doc.md
```

**Override with CLI:**
```bash
# params.yaml has author="Alice", CLI changes to "Bob"
mddata write from -f form.yaml \
  --params params.yaml \
  -p author="Bob" \
  -o doc.md
```

### From Files (`@filepath`)

Read parameter value from file:

```bash
# Read description from file
mddata write from -f form.yaml \
  -p title="Bug Report" \
  -p description=@long-description.txt \
  -o bug.md
```

### From Stdin (`@-` or `-`)

```bash
# From piped stdin
echo "Bug description" | mddata write from -f form.yaml \
  -p title="Bug" \
  -p description=@- \
  -o bug.md

# Interactive stdin (prompts for input)
mddata write from -f form.yaml \
  -p title="Bug" \
  -p description=- \
  -o bug.md
```

### Data from Stdin (Alternative to `-p` Options)

Instead of using multiple `-p` parameters, you can provide all form data via stdin using the `--data -` option. The format (JSON or YAML) is automatically detected. This is particularly useful when:
- Generating data programmatically
- Reading from other tools in pipelines
- Working with complex nested data structures
- Building shell pipelines for document generation

```bash
# Pipe JSON data to fill form (most common)
echo '{"title": "My Blog Post", "author": "Alice", "tags": ["tutorial", "python"]}' | \
  mddata write from -f blog-post.yaml -d - -o post.md

# From a data-generating script
./generate-report-data.sh | \
  mddata write from -f monthly-report.yaml -d - -o report.md

# Combine with jq for data transformation
jq '.user_input' user-data.json | \
  mddata write from -f form.yaml -d - -o output.md

# Override specific values with CLI parameters (CLI has highest priority)
echo '{"title": "Draft Title", "status": "draft"}' | \
  mddata write from -f form.yaml -d - \
  -p status="published" \
  -o final.md

# Pipe YAML data (auto-detected)
echo "title: My Document
author: Alice
tags:
  - tutorial
  - python" | mddata write from -f form.yaml -d - -o output.md
```

**Format Auto-Detection**: The system automatically detects JSON or YAML format by trying to parse the content as JSON first, then falling back to YAML. This allows seamless integration with various data sources without manual format specification.

## Complete Examples

### Bug Report Form

**File:** `bug-report.yaml`

```yaml
parameters:
  title:
    type: str
    required: true
    min: 10
    max: 100
    description: "Bug title (10-100 characters)"

  severity:
    type: str
    required: true
    enum: [critical, high, medium, low]
    enum_strict: true
    enum_descriptions:
      critical: "Requires immediate attention"
      high: "Important, address soon"
      medium: "Normal priority"
      low: "Can be deferred"

  priority:
    type: int
    required: true
    min: 1
    max: 5
    description: "Priority (1-5)"

  description:
    type: str
    required: true
    min: 20
    description: "Detailed description"

  affected_versions:
    type: array
    item_type: str
    required: false
    default: []

frontmatter:
  title: "{title}"
  severity: "{severity}"
  priority: "{priority}"
  date_reported: "{date}"
  status: "open"

sections:
  - id: bug_report
    content: |
      # [{severity}] {title}

      **Priority:** {priority}/5
      **Reported:** {date}
      **Affected Versions:** {affected_versions}

      ## Description

      {description}

      ## Status

      - [ ] Investigate
      - [ ] Fix
      - [ ] Test
      - [ ] Deploy
```

**Usage:**
```bash
mddata write from -f bug-report.yaml \
  -p title="Login endpoint returns 500 error" \
  -p severity="critical" \
  -p priority=1 \
  -p description="The /api/auth/login endpoint fails with 500 errors" \
  -p 'affected_versions=["1.2.0", "1.2.1"]' \
  -o bug-001.md
```

### Meeting Notes Form

**File:** `meeting-notes.yaml`

```yaml
parameters:
  title:
    type: str
    required: true

  attendees:
    type: array
    item_type: str
    required: true
    min_items: 1

  action_items:
    type: array
    item_type: str
    required: false
    default: []

  decisions:
    type: array
    item_type: str
    required: false
    default: []

frontmatter:
  title: "{title}"
  date: "{date}"
  type: "meeting_notes"

sections:
  - id: meeting
    content: |
      # {title}

      **Date:** {date}

      ## Attendees

      {attendees_list}

      ## Decisions

      {decisions_list}

      ## Action Items

      {action_items_list}
```

**Usage:**
```bash
# Using JSON array syntax
mddata write from -f meeting-notes.yaml \
  -p title="Sprint Planning" \
  -p 'attendees=["Alice", "Bob", "Carol"]' \
  -p 'decisions=["Approved feature X"]' \
  -p 'action_items=["Update docs", "Fix bug #123"]' \
  -o meeting-2025-11-19.md

# Using comma-separated syntax (shell-friendly)
mddata write from -f meeting-notes.yaml \
  -p title="Sprint Planning" \
  -p attendees="Alice, Bob, Carol" \
  -p decisions="Approved feature X" \
  -p action_items="Update docs, Fix bug #123" \
  -o meeting-2025-11-19.md
```

## Python API

### Loading and Filling Forms

```python
from mddata.templates import MarkdownFormFiller
from mddata.utils.data_loader import load_data_update

# Load form
form = load_data_update('bug-report.yaml')

# Create filler
filler = MarkdownFormFiller(form)

# Fill with parameters
filled = filler.fill(
    cli_params=[
        'title=Login bug',
        'severity=critical',
        'priority=1',
        'description=Login endpoint failing'
    ]
)

# filled is a MarkdownDataUpdate ready to use
print(filled.frontmatter)
print(filled.sections)
```

### Creating Documents from Forms

```python
from mddata import MarkdownFile
from mddata.templates import MarkdownFormFiller
from mddata.utils.data_loader import load_data_update

# Load and fill form
form = load_data_update('bug-report.yaml')
filler = MarkdownFormFiller(form)
filled = filler.fill(cli_params=['title=Bug', 'severity=high', 'priority=2'])

# Create document
doc = MarkdownFile.from_dict(
    filled.to_dict(),
    filepath='bug-001.md'
)
doc.save()
```

## Best Practices

### 1. Use Descriptive Parameter Names

```yaml
# Good
parameters:
  project_description:
    type: str

# Bad
parameters:
  desc:
    type: str
```

### 2. Provide Clear Descriptions

```yaml
parameters:
  priority:
    type: int
    min: 1
    max: 5
    description: "Priority level (1=lowest, 5=highest)"  # Helpful!
```

### 3. Set Sensible Defaults

```yaml
parameters:
  author:
    type: str
    default: "{env.USER}"  # Auto-fills current user

  date:
    type: date
    default: "{date}"      # Auto-fills today
```

### 4. Use Validation Constraints

```yaml
parameters:
  email:
    type: str
    pattern: "^[^@]+@[^@]+\\.[^@]+$"  # Validates email format

  title:
    type: str
    min: 5                             # Prevents too-short titles
    max: 100                           # Prevents too-long titles
```

### 5. Use Enums with Descriptions

```yaml
parameters:
  status:
    type: str
    enum: [draft, review, published]
    enum_descriptions:
      draft: "Work in progress"      # Helps users understand
      review: "Under review"          # each option
      published: "Published and live"
```

### 6. Validate Array Content

```yaml
parameters:
  tags:
    type: array
    min_items: 1                # At least one tag
    max_items: 10               # Not too many
    unique_items: true          # No duplicates
    item_pattern: "^[a-z-]+$"  # Lowercase with hyphens only
```

## Troubleshooting

### Common Errors

**"Missing required parameter 'name'"**
- Provide all required parameters
- Check `required: true` fields in form

**"Value 'X' not in enum values"**
- Use one of the allowed enum values
- Check error message for valid options

**"String length less than minimum"**
- Provide longer string
- Check `min` constraint

**"Array must have at least N items"**
- Provide more array items
- Check `min_items` constraint

**"Array items must be unique"**
- Remove duplicate values from array

## Related Documentation

- **[CLI Reference](CLI_REFERENCE.md)** - Complete CLI documentation
- **[Schema Validation](MARKDOWN_SCHEMA.md)** - Schema generation and validation
