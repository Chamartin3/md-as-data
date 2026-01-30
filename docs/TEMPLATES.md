# Markdown Templates and Parameters

This guide explains how to create and use parameterized markdown templates with mddata. Templates allow you to generate markdown documents from structured data with variable substitution, validation, and computed values.

## Overview

The template system provides two main capabilities:

1. **Parametrized Templates** - Create reusable markdown templates with placeholders
2. **Batch Updates** - Apply structured changes to existing documents

Both use the **MarkdownDataUpdate** format, which extends the basic document structure with parameters and update policies.

### Use Cases

Use templates and parametrization when you need to:

- **Generate consistent documents** from templates (bug reports, meeting notes, project specs)
- **Automate document creation** with dynamic content and computed values
- **Validate input** with type checking, constraints, and required fields
- **Apply batch modifications** to existing documents programmatically
- **Maintain document standards** across teams and projects

### CLI Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `mddata render --data` | Create markdown from data | `mddata render --data doc.json --output doc.md` |
| `mddata modify from-json` | Apply updates to existing file | `mddata modify from-json doc.md updates.json` |

---

## MarkdownDataUpdate Structure

The `MarkdownDataUpdate` format is the unified data structure for both templates and batch updates.

### Complete Structure

```yaml
# Template parameters (optional - makes this a template)
parameters:
  param_name:
    type: str|int|float|bool|date|array
    required: true|false
    default: value
    description: "Human-readable description"

    # Type-specific constraints
    min: number        # Minimum value/length
    max: number        # Maximum value/length
    pattern: "regex"   # String validation pattern
    item_type: str     # Array item type

    # Enhanced validation (Phase 1)
    enum: [value1, value2]                # Allowed values (any type)
    enum_descriptions: {value1: "desc"}   # Descriptions for enum values
    enum_strict: true|false               # Error (true) or warn (false)
    min_items: number                     # Minimum array length
    max_items: number                     # Maximum array length
    unique_items: true|false              # Require unique array values
    item_enum: [val1, val2]               # Allowed array item values
    item_enum_descriptions: {val1: "d"}   # Item enum descriptions
    item_enum_strict: true|false          # Strict array item validation
    item_pattern: "regex"                 # Regex for array items

# Document frontmatter
frontmatter:
  property_name: value
  placeholder: "{param_name}"

# Frontmatter update policy (for batch updates)
frontmatter_policy: merge|replace

# Document content (hierarchical format - preferred)
content:
  id: ""
  title: ""
  level: 0
  path: ""
  blocks: []
  children:
    - id: section_id
      title: "Section Title"
      level: 2
      path: "section_id"
      blocks: [...]
      children: [...]

# OR: Flat section updates (backward compatible)
sections:
  - id: section_id
    content: "Markdown content with {placeholders}"
    policy: update|replace|append
    # For nested sections, use 'children' key (NOT 'subsections')
    children:
      - id: child_section_id
        level: 3
        content: "Nested content"
```

> **Note**: For nested sections, always use the `children` key, not `subsections`. The `children` key is the correct field name in the `SectionUpdate` data model.

### Minimal Template Example

```yaml
parameters:
  title:
    type: str
    required: true

frontmatter:
  title: "{title}"
  date: "{date}"

sections:
  - id: introduction
    content: |
      # Introduction

      Welcome to {title}!
```

---

## Parameters

Parameters define the inputs required to fill a template. Each parameter has a type, validation rules, and optional default value.

### Parameter Definition

```yaml
parameters:
  parameter_name:
    type: str              # Required - data type
    required: true         # Optional - must be provided (default: false)
    default: "value"       # Optional - default if not provided
    description: "text"    # Optional - human-readable description

    # Enhanced validation constraints
    enum: [val1, val2]                      # Allowed values (any type)
    enum_descriptions: {val1: "desc"}       # Descriptions for enum values
    enum_strict: true                       # Error on invalid (true) or warn (false)

    # Array-specific constraints
    min_items: 1                            # Minimum array length
    max_items: 10                           # Maximum array length
    unique_items: true                      # Require unique values
    item_enum: [val1, val2]                 # Allowed values for array items
    item_enum_descriptions: {val1: "desc"}  # Descriptions for item enum
    item_enum_strict: true                  # Strict validation for items
    item_pattern: "regex"                   # Regex pattern for array items
```

### Parameter Types

#### String (`str`)

Text values with optional length and pattern constraints.

```yaml
parameters:
  title:
    type: str
    required: true
    min: 5              # Minimum length
    max: 100            # Maximum length
    pattern: "^[A-Z]"   # Regex validation
    description: "Document title (5-100 chars, starts with capital)"
```

**Usage:**
```bash
mddata render --data template.yaml title="My Document" --output doc.md
```

#### Integer (`int`)

Whole number values with optional range constraints.

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
mddata render --data template.yaml priority=3 --output doc.md
```

#### Float (`float`)

Decimal number values with optional range constraints.

```yaml
parameters:
  completion:
    type: float
    required: false
    default: 0.0
    min: 0.0
    max: 100.0
    description: "Completion percentage (0.0-100.0)"
```

**Usage:**
```bash
mddata render --data template.yaml completion=75.5 --output doc.md
```

#### Boolean (`bool`)

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
# Accepts: true, false, 1, 0, yes, no, on, off (case-insensitive)
mddata render --data template.yaml published=true --output doc.md
```

#### Date (`date`)

Date values (stored as strings in ISO format).

```yaml
parameters:
  due_date:
    type: date
    required: false
    default: "{date}"    # Use computed parameter
    description: "Due date (ISO format)"
```

**Usage:**
```bash
mddata render --data template.yaml due_date="2025-10-25" --output doc.md
```

#### Array (`array`)

List values with optional item type validation.

```yaml
parameters:
  tags:
    type: array
    item_type: str       # Optional - validate item types
    required: false
    default: []
    description: "Document tags"

  attendees:
    type: array
    item_type: str
    required: true
    description: "Meeting attendees"
```

**Usage:**
```bash
# JSON array syntax required
mddata render --data template.yaml \
  'tags=["tutorial", "beginner"]' \
  'attendees=["Alice", "Bob", "Carol"]' \
  --output doc.md
```

### Parameter Constraints

#### Length/Value Constraints (`min`, `max`)

**For strings:** Character length
```yaml
title:
  type: str
  min: 5      # At least 5 characters
  max: 100    # At most 100 characters
```

**For numbers:** Numeric value
```yaml
priority:
  type: int
  min: 1      # At least 1
  max: 5      # At most 5
```

#### Pattern Validation (`pattern`)

Regex pattern for string validation:

```yaml
email:
  type: str
  pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
  description: "Valid email address"

version:
  type: str
  pattern: "^\\d+\\.\\d+\\.\\d+$"
  description: "Semantic version (e.g., 1.2.3)"
```

#### Enum Validation

Restrict parameter values to a predefined set with optional descriptions:

**Basic enum (strict mode):**
```yaml
status:
  type: str
  enum: [draft, review, published]
  enum_strict: true  # Raises error on invalid value (default)
  description: "Document status"
```

**Enum with descriptions:**
```yaml
priority:
  type: str
  enum: [critical, high, medium, low]
  enum_descriptions:
    critical: "Requires immediate attention"
    high: "Important, address soon"
    medium: "Normal priority"
    low: "Can be deferred"
  enum_strict: true
```

**Non-strict enum (warning mode):**
```yaml
category:
  type: str
  enum: [bug, feature, docs]
  enum_strict: false  # Issues warning but allows invalid values
  description: "Issue category (extensible)"
```

**Enum with mixed types:**
```yaml
verbosity:
  type: int
  enum: [0, 1, 2, 3]
  enum_descriptions:
    "0": "Silent"
    "1": "Errors only"
    "2": "Warnings and errors"
    "3": "Verbose output"
```

#### Array Constraints

Validate array length and uniqueness:

**Length constraints:**
```yaml
tags:
  type: array
  min_items: 1    # At least 1 tag required
  max_items: 5    # At most 5 tags allowed
  description: "Document tags (1-5 required)"
```

**Uniqueness constraint:**
```yaml
collaborators:
  type: array
  unique_items: true  # No duplicate values allowed
  description: "Unique collaborator names"
```

**Combined array constraints:**
```yaml
keywords:
  type: array
  min_items: 2
  max_items: 10
  unique_items: true
  description: "2-10 unique keywords"
```

#### Array Item Enum Validation

Restrict array item values to predefined set:

**Strict item enum:**
```yaml
labels:
  type: array
  item_enum: [bug, feature, enhancement, documentation]
  item_enum_strict: true  # All items must match enum
  item_enum_descriptions:
    bug: "Bug fix or issue"
    feature: "New feature"
    enhancement: "Improvement to existing feature"
    documentation: "Documentation update"
```

**Non-strict item enum with pattern fallback:**
```yaml
tags:
  type: array
  item_enum: [python, javascript, typescript]
  item_enum_strict: false  # Allows non-enum values
  item_pattern: "^[a-z]+$"  # But they must match pattern
  description: "Predefined tags or custom lowercase tags"
```

This allows either enum values OR values matching the pattern.

#### Array Item Pattern Validation

Validate array item format with regex:

**Email validation:**
```yaml
recipients:
  type: array
  item_pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
  description: "Valid email addresses"
```

**URL validation:**
```yaml
links:
  type: array
  item_pattern: "^https?://.*"
  description: "HTTP/HTTPS URLs only"
```

**Version string validation:**
```yaml
supported_versions:
  type: array
  item_pattern: "^\\d+\\.\\d+\\.\\d+$"
  description: "Semantic version strings (e.g., 1.2.3)"
```

#### Required Parameters

```yaml
# Required parameter - must be provided
title:
  type: str
  required: true

# Optional parameter - can be omitted
subtitle:
  type: str
  required: false
  default: ""
```

---

## Computed Parameters

Computed parameters are automatically resolved at template fill time. They don't need to be defined in the `parameters` section.

### Built-in Computed Parameters

#### `{date}` - Current Date

Returns current date in ISO format (YYYY-MM-DD).

```yaml
frontmatter:
  created: "{date}"

sections:
  - id: intro
    content: "Document created on {date}"
```

**Output:** `created: 2025-10-25`

#### `{time}` - Current Time

Returns current time in ISO format (HH:MM:SS).

```yaml
frontmatter:
  timestamp: "{time}"
```

**Output:** `timestamp: 14:30:45`

#### `{now}` - Current Date and Time

Returns current datetime in ISO format.

```yaml
frontmatter:
  generated_at: "{now}"
```

**Output:** `generated_at: 2025-10-25T14:30:45`

### Environment Variables

Access environment variables using `{env.VARIABLE_NAME}` syntax.

```yaml
parameters:
  author:
    type: str
    required: false
    default: "{env.USER}"    # Defaults to $USER environment variable

frontmatter:
  author: "{author}"
  home_dir: "{env.HOME}"
  shell: "{env.SHELL}"
```

**Common environment variables:**
- `{env.USER}` - Current username
- `{env.HOME}` - Home directory path
- `{env.PWD}` - Current working directory
- `{env.EDITOR}` - Default text editor

**Custom environment variables:**
```bash
# Set custom environment variable
export PROJECT_NAME="My Project"

# Use in template
mddata render --data template.yaml --output doc.md
# Template accesses via: {env.PROJECT_NAME}
```

---

## Creating Templates

Templates are YAML or JSON files defining document structure with parameters.

### Simple Template

**File:** `simple-template.yaml`

```yaml
parameters:
  title:
    type: str
    required: true
    description: "Document title"

  author:
    type: str
    required: false
    default: "{env.USER}"

frontmatter:
  title: "{title}"
  author: "{author}"
  date: "{date}"

sections:
  - id: introduction
    content: |
      # Introduction

      Welcome to {title}!

      This document was created by {author} on {date}.
```

**Usage:**
```bash
mddata render --data simple-template.yaml \
  title="Getting Started Guide" \
  --output guide.md
```

### Template with Constraints

**File:** `bug-report.yaml`

```yaml
parameters:
  title:
    type: str
    required: true
    min: 5
    max: 100
    description: "Bug title (5-100 characters)"

  severity:
    type: str
    required: true
    enum: [critical, high, medium, low]
    enum_descriptions:
      critical: "Requires immediate attention"
      high: "Important, address soon"
      medium: "Normal priority"
      low: "Can be deferred"
    description: "Bug severity level"

  priority:
    type: int
    required: true
    min: 1
    max: 5
    description: "Priority level (1-5)"

  description:
    type: str
    required: true
    min: 10
    description: "Detailed description (minimum 10 characters)"

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
  - id: bugs
    content: |
      ## [{severity}] {title}

      **Priority**: {priority}/5
      **Date**: {date}
      **Affected Versions**: {affected_versions}

      ### Description
      {description}

      ### Status
      - [ ] Investigate
      - [ ] Fix
      - [ ] Test
      - [ ] Deploy
    policy: append
```

**Usage:**
```bash
mddata render --data bug-report.yaml \
  title="Login endpoint returns 500 error" \
  severity="critical" \
  priority=1 \
  description="The /api/auth/login endpoint fails with 500 errors" \
  'affected_versions=["1.2.0", "1.2.1"]' \
  --output bug-001.md
```

### Template with Arrays

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
    description: "List of meeting attendees"

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
  - id: meeting_notes
    content: |
      # {title}

      **Date**: {date}

      ## Attendees
      {attendees}

      ## Action Items
      {action_items}

      ## Decisions
      {decisions}
```

**Usage:**
```bash
mddata render --data meeting-notes.yaml \
  title="Sprint Planning Meeting" \
  'attendees=["Alice", "Bob", "Carol"]' \
  'action_items=["Update docs", "Fix bug #123"]' \
  'decisions=["Approved feature X"]' \
  --output meeting-2025-10-25.md
```

---

## Using Templates

### CLI Parameter Syntax

**Basic format:**
```bash
mddata render --data template.yaml param=value --output file.md
```

**Multiple parameters:**
```bash
mddata render --data template.yaml \
  title="My Document" \
  author="Alice" \
  priority=1 \
  --output doc.md
```

**Array parameters (JSON syntax):**
```bash
mddata render --data template.yaml \
  'tags=["tutorial", "beginner"]' \
  --output doc.md
```

### Parameter Value Sources

#### Direct Values (CLI Arguments)

```bash
mddata render --data template.yaml title="My Document" --output doc.md
```

#### From File (`@filepath`)

Read parameter value from file:

**File:** `description.txt`
```
This is a long description
that spans multiple lines
and would be unwieldy as a CLI argument.
```

**Usage:**
```bash
mddata render --data template.yaml \
  title="Bug Report" \
  description=@description.txt \
  --output bug.md
```

#### From Stdin (`@-` or `-`)

**Piped stdin (`@-`):**
```bash
echo "Bug description text" | mddata render --data template.yaml \
  title="Bug Report" \
  description=@- \
  --output bug.md
```

**Interactive stdin (`-`):**
```bash
mddata render --data template.yaml \
  title="Bug Report" \
  description=- \
  --output bug.md
# Prompts: Enter parameter value (Ctrl+D to finish):
# User types description and presses Ctrl+D
```

#### From Parameters File

Group all parameters in a JSON/YAML file:

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
mddata render --data template.yaml \
  --params params.yaml \
  --output doc.md
```

**Override parameters file values:**
```bash
# params.yaml has author="Alice"
# CLI override changes it to "Bob"
mddata render --data template.yaml \
  --params params.yaml \
  author="Bob" \
  --output doc.md
```

### Parameter Precedence

Parameters are resolved in this order (lowest to highest):

1. **Computed parameters** (`{date}`, `{env.USER}`)
2. **Template defaults** (defined in `parameters.default`)
3. **Parameters file** (`--params file.yaml`)
4. **CLI arguments** (direct `param=value`)

Later sources override earlier ones.

**Example:**
```yaml
# template.yaml
parameters:
  author:
    type: str
    default: "{env.USER}"  # Precedence: 1 (computed) + 2 (default)

# params.yaml
author: "Alice"            # Precedence: 3

# CLI
author="Bob"               # Precedence: 4 (highest - wins!)
```

---

## Placeholder Substitution

Placeholders use `{parameter_name}` syntax and are replaced with parameter values.

### Basic Substitution

```yaml
parameters:
  title:
    type: str

frontmatter:
  title: "{title}"

sections:
  - id: intro
    content: "Welcome to {title}!"
```

**With:** `title="My Guide"`
**Output:** `Welcome to My Guide!`

### Nested Substitution

Placeholders can reference computed parameters:

```yaml
parameters:
  author:
    type: str
    default: "{env.USER}"  # Computed parameter in default

frontmatter:
  author: "{author}"       # References parameter (which references env var)
```

**Result:** `author: alice` (if `$USER=alice`)

### Escaping Literal Braces

Use backslash to escape literal braces:

```yaml
content: "Use \\{placeholders\\} in templates"
```

**Output:** `Use {placeholders} in templates`

### Array Formatting

Arrays are formatted as comma-separated lists:

```yaml
parameters:
  tags:
    type: array

frontmatter:
  tags: "{tags}"
```

**With:** `tags=["python", "tutorial", "beginner"]`
**Output:** `tags: python, tutorial, beginner`

### Placeholder Locations

Placeholders work in all text content:

**Frontmatter values:**
```yaml
frontmatter:
  title: "{title}"
  author: "{author}"
  version: "{version}"
```

**Section content:**
```yaml
sections:
  - id: intro
    content: |
      # {title}

      Created by {author} on {date}
```

**Block content (hierarchical format):**
```yaml
content:
  children:
    - id: intro
      blocks:
        - type: paragraph
          content: "Welcome to {title}!"
```

---

## Batch Updates (from-json)

Apply structured changes to existing documents without parameters.

### Update Format

```yaml
# No parameters section - this is a batch update, not a template

frontmatter:
  status: "published"
  version: "2.0"
  last_updated: "2025-10-25"

frontmatter_policy: merge  # merge (default) or replace

sections:
  - id: changelog
    content: |
      ### Version 2.0 - 2025-10-25

      - New features
      - Bug fixes
    policy: append
```

### Frontmatter Policies

#### `merge` (default)

Merge new properties with existing, update conflicts:

```yaml
frontmatter:
  status: "published"    # Updates existing or adds new
  version: "2.0"         # Updates existing or adds new

frontmatter_policy: merge
```

**Before:**
```yaml
title: "My Document"
status: "draft"
author: "Alice"
```

**After:**
```yaml
title: "My Document"      # Preserved
status: "published"       # Updated
author: "Alice"           # Preserved
version: "2.0"            # Added
```

#### `replace`

Replace entire frontmatter:

```yaml
frontmatter:
  status: "published"
  version: "2.0"

frontmatter_policy: replace
```

**Before:**
```yaml
title: "My Document"
status: "draft"
author: "Alice"
```

**After:**
```yaml
status: "published"       # Only specified properties remain
version: "2.0"
```

### Section Update Policies

#### `update` (default)

Merge content, preserve subsections:

```yaml
sections:
  - id: introduction
    content: |
      # Introduction

      Updated introduction text.
    policy: update
```

#### `replace`

Replace entire section including subsections:

```yaml
sections:
  - id: introduction
    content: |
      # Introduction

      Completely new introduction.
    policy: replace
```

#### `append`

Add content to end of section:

```yaml
sections:
  - id: changelog
    content: |

      ### Version 2.0

      - New feature X
      - Bug fix Y
    policy: append
```

### CLI Usage

```bash
# Apply batch updates
mddata modify from-json document.md updates.yaml

# From stdin
cat updates.yaml | mddata modify from-json document.md -

# Preview changes (dry run)
mddata modify from-json document.md updates.yaml --dry-run
```

---

## Complete Examples

### Example 1: Project Specification Template

**Template:** `project-spec.yaml`

```yaml
parameters:
  project_name:
    type: str
    required: true
    min: 3
    max: 50
    description: "Project name"

  project_description:
    type: str
    required: true
    min: 10
    description: "Brief project description"

  team_members:
    type: array
    item_type: str
    required: true
    description: "Project team members"

  timeline:
    type: str
    required: false
    default: "TBD"
    description: "Project timeline"

  budget:
    type: str
    required: false
    default: "TBD"

frontmatter:
  title: "{project_name}"
  type: "project_specification"
  date: "{date}"
  status: "draft"

frontmatter_policy: merge

sections:
  - id: overview
    content: |
      # {project_name}

      **Created**: {date}
      **Status**: Draft

      ## Overview

      {project_description}

  - id: team
    content: |
      ## Team

      {team_members}

  - id: timeline
    content: |
      ## Timeline

      {timeline}

  - id: budget
    content: |
      ## Budget

      {budget}

  - id: requirements
    content: |
      ## Requirements

      ### Functional Requirements

      - TBD

      ### Non-Functional Requirements

      - TBD

  - id: milestones
    content: |
      ## Milestones

      - [ ] Project kickoff
      - [ ] Requirements finalized
      - [ ] Design complete
      - [ ] Implementation complete
      - [ ] Testing complete
      - [ ] Deployment
```

**Usage:**

```bash
mddata render --data project-spec.yaml \
  project_name="Authentication System Redesign" \
  project_description="Redesign authentication system with OAuth2 and MFA support" \
  'team_members=["Alice (Lead)", "Bob (Backend)", "Carol (Frontend)"]' \
  timeline="Q1 2026" \
  budget="$50,000" \
  --output auth-redesign-spec.md
```

### Example 2: Weekly Status Report Template

**Template:** `status-report.yaml`

```yaml
parameters:
  week_ending:
    type: date
    required: true
    description: "Week ending date"

  reporter:
    type: str
    required: false
    default: "{env.USER}"

  accomplishments:
    type: array
    item_type: str
    required: false
    default: []

  next_week_plans:
    type: array
    item_type: str
    required: false
    default: []

  blockers:
    type: array
    item_type: str
    required: false
    default: []

frontmatter:
  title: "Status Report - Week Ending {week_ending}"
  date: "{date}"
  reporter: "{reporter}"
  week_ending: "{week_ending}"

sections:
  - id: status_report
    content: |
      # Status Report

      **Reporter**: {reporter}
      **Week Ending**: {week_ending}
      **Report Date**: {date}

      ## Accomplishments This Week

      {accomplishments}

      ## Plans for Next Week

      {next_week_plans}

      ## Blockers

      {blockers}
```

**Usage:**

```bash
mddata render --data status-report.yaml \
  week_ending="2025-10-25" \
  'accomplishments=["Completed feature X", "Fixed bug Y", "Reviewed 5 PRs"]' \
  'next_week_plans=["Start feature Z", "Performance optimization"]' \
  'blockers=["Waiting on API documentation"]' \
  --output status-2025-10-25.md
```

### Example 3: Batch Update Existing Document

**Update file:** `publish-updates.yaml`

```yaml
# No parameters - this is a batch update

frontmatter:
  status: "published"
  published_date: "2025-10-25"
  version: "1.0.0"
  reviewed_by: "Alice"

frontmatter_policy: merge

sections:
  - id: changelog
    content: |

      ## Version 1.0.0 - 2025-10-25

      - Initial publication
      - Reviewed and approved
      - All requirements met
    policy: append

  - id: review_notes
    content: |
      ## Review Notes

      **Reviewer**: Alice
      **Date**: 2025-10-25
      **Status**: Approved

      Document meets all quality standards and is approved for publication.
    policy: update
```

**Usage:**

```bash
# Apply updates to document
mddata modify from-json my-document.md publish-updates.yaml

# Preview changes first
mddata modify from-json my-document.md publish-updates.yaml --dry-run
```

---

## Advanced Validation Examples

### Example 4: Pull Request Template with Enhanced Validation

This example demonstrates all enhanced validation features:

**Template:** `pull-request.yaml`

```yaml
parameters:
  title:
    type: str
    required: true
    min: 10
    max: 100
    description: "PR title (10-100 characters)"

  pr_type:
    type: str
    required: true
    enum: [feature, bugfix, refactor, docs, test, chore]
    enum_strict: true
    enum_descriptions:
      feature: "New feature or functionality"
      bugfix: "Bug fix"
      refactor: "Code refactoring (no behavior change)"
      docs: "Documentation changes"
      test: "Test additions or modifications"
      chore: "Maintenance tasks"
    description: "Type of change"

  priority:
    type: int
    required: true
    enum: [1, 2, 3]
    enum_descriptions:
      "1": "High priority - merge ASAP"
      "2": "Medium priority - normal review"
      "3": "Low priority - can wait"
    description: "Priority level"

  labels:
    type: array
    required: true
    min_items: 1
    max_items: 5
    unique_items: true
    item_enum: [backend, frontend, database, api, security, performance]
    item_enum_strict: false
    item_pattern: "^[a-z-]+$"
    item_enum_descriptions:
      backend: "Backend code changes"
      frontend: "Frontend/UI changes"
      database: "Database schema or query changes"
      api: "API endpoint changes"
      security: "Security-related changes"
      performance: "Performance improvements"
    description: "PR labels (predefined or custom lowercase-hyphenated)"

  reviewers:
    type: array
    required: true
    min_items: 1
    max_items: 3
    unique_items: true
    item_pattern: "^[a-zA-Z0-9_-]+$"
    description: "GitHub usernames (1-3 reviewers)"

  linked_issues:
    type: array
    required: false
    default: []
    item_pattern: "^#\\d+$"
    description: "Related issue numbers (e.g., #123)"

  breaking_changes:
    type: bool
    required: false
    default: false
    description: "Does this PR introduce breaking changes?"

frontmatter:
  title: "{title}"
  pr_type: "{pr_type}"
  priority: "{priority}"
  labels: "{labels}"
  reviewers: "{reviewers}"
  linked_issues: "{linked_issues}"
  breaking_changes: "{breaking_changes}"
  created: "{date}"

sections:
  - id: pull_request
    content: |
      # {title}

      **Type**: {pr_type}
      **Priority**: {priority}/3
      **Labels**: {labels}
      **Reviewers**: {reviewers}
      **Created**: {date}

      ## Description

      [Describe the changes in this PR]

      ## Related Issues

      {linked_issues}

      ## Testing

      - [ ] Unit tests added/updated
      - [ ] Integration tests added/updated
      - [ ] Manual testing completed

      ## Breaking Changes

      **Has Breaking Changes**: {breaking_changes}

      [If yes, describe breaking changes and migration path]

      ## Checklist

      - [ ] Code follows project style guidelines
      - [ ] Self-review completed
      - [ ] Comments added for complex code
      - [ ] Documentation updated
      - [ ] No new warnings generated
```

**Usage with validation:**

```bash
# Valid PR with all constraints met
mddata write --data pull-request.yaml \
  title="Add user authentication with OAuth2" \
  pr_type="feature" \
  priority=1 \
  'labels=["backend", "api", "security"]' \
  'reviewers=["alice", "bob"]' \
  'linked_issues=["#42", "#56"]' \
  breaking_changes=true \
  --output pr-auth.md

# Invalid: title too short (min 10 chars)
mddata write --data pull-request.yaml \
  title="Fix bug" \
  # Error: String length is less than minimum 10

# Invalid: wrong enum value
mddata write --data pull-request.yaml \
  pr_type="hotfix" \
  # Error: Value 'hotfix' not in enum values: [feature, bugfix, ...]
  # Available options:
  #   feature - New feature or functionality
  #   bugfix - Bug fix
  #   ...

# Invalid: too many labels
mddata write --data pull-request.yaml \
  'labels=["a", "b", "c", "d", "e", "f"]' \
  # Error: Array must have at most 5 items, got 6

# Invalid: duplicate reviewers
mddata write --data pull-request.yaml \
  'reviewers=["alice", "alice"]' \
  # Error: Array items must be unique

# Valid: custom label allowed (non-strict enum + pattern match)
mddata write --data pull-request.yaml \
  'labels=["backend", "custom-feature"]' \
  # Success: "backend" in enum, "custom-feature" matches pattern

# Invalid: custom label doesn't match pattern
mddata write --data pull-request.yaml \
  'labels=["backend", "Custom_Feature"]' \
  # Error: Array item [1] = 'Custom_Feature' does not match pattern '^[a-z-]+$'

# Invalid: malformed issue reference
mddata write --data pull-request.yaml \
  'linked_issues=["42", "issue-56"]' \
  # Error: Array item [0] = '42' does not match pattern '^#\\d+$'
```

**Error Messages:**

The validation system provides detailed error messages:

```
# Enum validation with descriptions
Error: Value 'hotfix' not in enum values: [feature, bugfix, refactor, docs, test, chore]

Available options:
  feature - New feature or functionality
  bugfix - Bug fix
  refactor - Code refactoring (no behavior change)
  docs - Documentation changes
  test - Test additions or modifications
  chore - Maintenance tasks

# Array item validation with index
Error: Array item [2] = 'URGENT' not in enum values: [backend, frontend, database, api, security, performance]

# Pattern validation with regex
Error: Array item [1] = 'user@domain' does not match pattern '^[a-zA-Z0-9_-]+$'
```

---

## Python API

Use templates programmatically in Python code.

### Loading Templates

```python
from mddata.templates import TemplateFiller
from mddata.utils import load_markdown_data_update

# Load template from YAML/JSON file
template = load_markdown_data_update('template.yaml')

# Create filler instance
filler = TemplateFiller(template)
```

### Filling Templates

```python
# Fill template with parameters
filled = filler.fill(
    cli_params=['title=My Document', 'author=Alice'],
    params_file='params.yaml'  # Optional
)

# Access filled data
print(filled.frontmatter)
print(filled.sections)
```

### Applying to Documents

```python
from mddata import MarkdownFile

# Method 1: Apply to new document
doc = MarkdownFile.from_dict(filled.as_markdown_dict(), filepath='output.md')
doc.save()

# Method 2: Apply updates to existing document
doc = MarkdownFile('existing.md')
doc.mddata.apply_batch_changes(filled.to_dict())
doc.save()
```

### Complete Example

```python
from pathlib import Path
from mddata import MarkdownFile
from mddata.templates import TemplateFiller
from mddata.utils import load_markdown_data_update

# Load template
template_path = Path('templates/bug-report.yaml')
template = load_markdown_data_update(str(template_path))

# Create filler
filler = TemplateFiller(template)

# Fill with parameters
filled = filler.fill(
    cli_params=[
        'title=Login endpoint returns 500 error',
        'severity=critical',
        'priority=1',
        'description=The /api/auth/login endpoint is failing',
        'affected_versions=["1.2.0", "1.2.1"]'
    ]
)

# Create document
doc = MarkdownFile.from_dict(
    filled.as_markdown_dict(),
    filepath='bugs/bug-001.md'
)
doc.save()

print(f"Created bug report: {doc.filepath}")
```

---

## Best Practices

### Template Design

1. **Use descriptive parameter names**
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

2. **Provide helpful descriptions**
   ```yaml
   parameters:
     priority:
       type: int
       min: 1
       max: 5
       description: "Priority level (1=lowest, 5=highest)"
   ```

3. **Set sensible defaults**
   ```yaml
   parameters:
     author:
       type: str
       default: "{env.USER}"  # Defaults to current user

     date:
       type: date
       default: "{date}"      # Defaults to today
   ```

4. **Use constraints for validation**
   ```yaml
   parameters:
     email:
       type: str
       pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"

     title:
       type: str
       min: 5
       max: 100
   ```

5. **Use enums for controlled vocabularies**
   ```yaml
   parameters:
     status:
       type: str
       enum: [draft, review, published]
       enum_descriptions:
         draft: "Work in progress"
         review: "Under review"
         published: "Published and live"
       description: "Document lifecycle status"
   ```

6. **Use non-strict enums for extensibility**
   ```yaml
   parameters:
     category:
       type: str
       enum: [common, predefined, values]
       enum_strict: false  # Allow custom values with warning
       description: "Category (predefined or custom)"
   ```

7. **Validate array content with constraints**
   ```yaml
   parameters:
     tags:
       type: array
       min_items: 1
       max_items: 10
       unique_items: true
       item_enum: [python, javascript, typescript]
       item_enum_strict: false
       item_pattern: "^[a-z-]+$"
       description: "1-10 unique tags (predefined or custom lowercase)"
   ```

8. **Provide helpful enum descriptions**
   ```yaml
   # Good - clear descriptions help users
   parameters:
     priority:
       type: int
       enum: [1, 2, 3]
       enum_descriptions:
         "1": "Critical - requires immediate attention"
         "2": "Normal - handle in regular workflow"
         "3": "Low - can be deferred"

   # Bad - no descriptions
   parameters:
     priority:
       type: int
       enum: [1, 2, 3]  # Users have to guess meanings
   ```

### Parameter Organization

1. **Group related parameters**
   ```yaml
   parameters:
     # Document metadata
     title:
       type: str
     author:
       type: str
     date:
       type: date

     # Content parameters
     description:
       type: str
     tags:
       type: array
   ```

2. **Mark required vs optional clearly**
   ```yaml
   parameters:
     # Required
     title:
       type: str
       required: true

     # Optional with defaults
     author:
       type: str
       required: false
       default: "{env.USER}"
   ```

### Template Reusability

1. **Create template libraries**
   ```
   templates/
   ├── bug-report.yaml
   ├── meeting-notes.yaml
   ├── project-spec.yaml
   └── status-report.yaml
   ```

2. **Version your templates**
   ```yaml
   frontmatter:
     template_version: "1.0.0"
     template_name: "bug-report"
   ```

3. **Document template usage**
   ```yaml
   # Bug Report Template v1.0
   #
   # Usage:
   #   mddata render --data bug-report.yaml \
   #     title="Bug title" \
   #     severity="critical" \
   #     priority=1 \
   #     description="Bug description" \
   #     --output bug.md
   #
   parameters:
     # ...
   ```

---

## Troubleshooting

### Common Issues

#### "Unknown placeholder: {name}"

**Cause:** Parameter not defined or not provided.

**Solution:** Check parameter is defined and value is provided:

```yaml
# Define parameter
parameters:
  name:
    type: str
    required: true

# Or provide value
mddata render --data template.yaml name="Alice" --output doc.md
```

#### "Cannot convert 'value' to integer"

**Cause:** Parameter type mismatch.

**Solution:** Provide correct type:

```bash
# Wrong
priority="high"

# Right
priority=1
```

#### "Value is less than minimum N"

**Cause:** Constraint violation.

**Solution:** Check parameter constraints:

```yaml
parameters:
  priority:
    type: int
    min: 1  # Must be at least 1
    max: 5  # Must be at most 5
```

#### "Expected JSON array, got ..."

**Cause:** Array parameter syntax error.

**Solution:** Use JSON array syntax with quotes:

```bash
# Wrong
tags=tutorial,beginner

# Right
'tags=["tutorial", "beginner"]'
```

#### "Required parameter 'name' is not provided"

**Cause:** Required parameter missing.

**Solution:** Provide all required parameters:

```yaml
parameters:
  title:
    type: str
    required: true  # Must provide this
```

#### "Value 'X' not in enum values: [...]"

**Cause:** Invalid enum value provided.

**Solution:** Use one of the allowed enum values:

```yaml
parameters:
  status:
    type: str
    enum: [draft, review, published]
    enum_strict: true

# Must use: draft, review, or published
mddata write --data template.yaml status=draft -o doc.md
```

**Tip:** Error message shows all valid values with descriptions if defined.

#### "Array must have at least N items"

**Cause:** Array has fewer items than required minimum.

**Solution:** Provide sufficient array items:

```yaml
parameters:
  tags:
    type: array
    min_items: 2  # At least 2 required

# Must provide at least 2 items
'tags=["tag1", "tag2"]'
```

#### "Array items must be unique"

**Cause:** Array contains duplicate values.

**Solution:** Remove duplicate values:

```bash
# Wrong
'tags=["python", "python"]'

# Right
'tags=["python", "javascript"]'
```

#### "Array item [N] = 'value' not in enum values"

**Cause:** Array item doesn't match allowed values.

**Solution:** Use valid enum values or check pattern:

```yaml
parameters:
  labels:
    type: array
    item_enum: [bug, feature, docs]
    item_enum_strict: false
    item_pattern: "^[a-z-]+$"

# Valid: enum value
'labels=["bug"]'

# Valid: matches pattern (non-strict)
'labels=["custom-label"]'

# Invalid: neither enum nor pattern match
'labels=["Invalid_Label"]'
```

#### "Array item [N] = 'value' does not match pattern"

**Cause:** Array item doesn't match regex pattern.

**Solution:** Format value according to pattern:

```yaml
parameters:
  emails:
    type: array
    item_pattern: "^[^@]+@[^@]+\\.[^@]+$"

# Valid email format
'emails=["user@example.com"]'

# Invalid: missing @ or domain
'emails=["invalid-email"]'
```

### Validation Tips

```bash
# Test template with minimal parameters
mddata render --data template.yaml \
  title="Test" \
  --output /tmp/test.md

# Use --dry-run for batch updates
mddata modify from-json doc.md updates.yaml --dry-run

# Validate parameter file syntax
cat params.yaml | yq empty  # YAML
cat params.json | jq empty  # JSON

# Check computed parameters
echo '{env.USER}'  # Show current user
echo '{date}'      # Show current date
```

---

## Related Documentation

**Core Documentation:**
- **[Markdown Data Format](./MARKDOWN_DATA.md)** - Complete MarkdownDataDict structure reference
- **[Schema Format](./MARKDOWN_SCHEMA.md)** - Schema validation and generation
- **[CLI Reference](./CLI_REFERENCE.md)** - Full command-line interface documentation

**Examples and Guides:**
- **[Template Examples](../examples/templates/)** - Working template examples and demos
- **[Generation Examples](../examples/generation/)** - Document generation workflows
