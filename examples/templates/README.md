# Template Examples

This directory contains example templates demonstrating the mddata template system functionality. Templates enable parameterized, reusable document modifications with type-safe validation.

## Available Templates

### 1. `log-entry.yaml` - Simple Template
**Purpose**: Add timestamped log entries to a changelog document

**Features**:
- Basic string parameters
- Computed parameters (`{date}`, `{now}`)
- Default values
- Append policy for accumulating entries

**Usage**:
```python
from mddata import MarkdownFile
from mddata.templates import load_template, parse_cli_params, resolve_computed_params

# Load template and document
template = load_template('examples/templates/log-entry.yaml')
doc = MarkdownFile('changelog.md')

# Resolve computed parameters
computed = resolve_computed_params(template)

# Parse user parameters
params = parse_cli_params(
    ['title=Fixed authentication bug', 'category=bugfix', 'content=Updated JWT validation logic'],
    template.parameters,
    computed
)

# Apply template (implementation depends on Task 022)
# This demonstrates the data flow - CLI integration pending
print(f"Title: {params.values['title']}")
print(f"Category: {params.values['category']}")
print(f"Date: {params.values['date']}")  # Auto-computed
```

### 2. `meeting-notes.yaml` - Array Parameters
**Purpose**: Document meeting notes with attendees and action items

**Features**:
- Array parameters for lists
- Comma-separated array formatting
- Multiple array fields
- Structured meeting documentation

**Usage**:
```python
from mddata.templates import load_template, parse_cli_params, resolve_computed_params

template = load_template('examples/templates/meeting-notes.yaml')
computed = resolve_computed_params(template)

# Array parameters are parsed from JSON
params = parse_cli_params([
    'title=Sprint Planning',
    'attendees=["Alice", "Bob", "Carol"]',
    'action_items=["Update docs", "Fix bug #123", "Review PRs"]',
    'decisions=["Approved new feature", "Postponed refactoring"]'
], template.parameters, computed)

print(f"Attendees: {params.values['attendees']}")
# Output: Alice, Bob, Carol
```

### 3. `bug-report.yaml` - Complex Constraints
**Purpose**: Create structured bug reports with validation

**Features**:
- Parameter constraints (min, max lengths)
- Enum validation for severity levels
- Integer range validation for priority
- Environment variable defaults
- Multiple parameter types

**Usage**:
```python
from mddata.templates import load_template, parse_cli_params, resolve_computed_params

template = load_template('examples/templates/bug-report.yaml')
computed = resolve_computed_params(template)

# Constraint validation happens automatically
params = parse_cli_params([
    'title=Login endpoint returns 500 error',
    'severity=critical',
    'priority=1',
    'description=The /api/auth/login endpoint is returning 500 errors for all requests',
    'affected_versions=["1.2.0", "1.2.1"]',
    'reproduce_steps=1. Navigate to login page\\n2. Enter credentials\\n3. Observe 500 error'
], template.parameters, computed)

# reporter will default to {env.USER} if not specified
print(f"Reporter: {params.values['reporter']}")
```

## Template File Structure

All templates follow this YAML structure:

```yaml
parameters:
  param_name:
    type: str|int|float|bool|date|array
    required: true|false
    default: "value"                    # Optional
    description: "Parameter description"
    # Constraints (optional)
    min: 1                              # Minimum value/length
    max: 100                            # Maximum value/length
    pattern: "regex"                    # Regex pattern (strings)
    enum: ["value1", "value2"]          # Allowed values
    item_type: str                      # For arrays

frontmatter:
  property: "{param}"                 # Placeholder substitution

sections:
  - id: "section_id"
    content: |
      Content with {placeholders}
    policy: append|replace|update     # Section merge policy
```

## Computed Parameters

Templates automatically provide these computed parameters:

- `{date}` - Current date (YYYY-MM-DD)
- `{now}` - Current datetime (ISO 8601)
- `{time}` - Current time (HH:MM:SS)
- `{env.VAR_NAME}` - Environment variables

## Parameter Types

### String (`str`)
```yaml
title:
  type: str
  min: 5          # Minimum length
  max: 100        # Maximum length
  pattern: "^[A-Z].*"  # Regex pattern
```

### Integer (`int`)
```yaml
priority:
  type: int
  min: 1
  max: 5
```

### Float (`float`)
```yaml
score:
  type: float
  min: 0.0
  max: 100.0
```

### Boolean (`bool`)
```yaml
published:
  type: bool
  default: false
```

### Date (`date`)
```yaml
deadline:
  type: date
  # Format: YYYY-MM-DD
```

### Array (`array`)
```yaml
tags:
  type: array
  item_type: str  # Validates each item
  default: []
```

## Placeholder Syntax

- **Simple substitution**: `{param_name}`
- **Escape braces**: `\{literal}` → `{literal}` in output
- **Case-sensitive**: `{Date}` ≠ `{date}`
- **Array formatting**: Arrays become comma-separated strings

## Section Policies

- **`append`**: Add content to end of section
- **`replace`**: Replace entire section content
- **`update`**: Merge content while preserving subsections (default)

## Testing Your Templates

Validate template structure:
```python
from mddata.templates import load_template

# Will raise ValidationError if template is invalid
template = load_template('your-template.yaml')
print(f"Loaded template with {len(template.parameters)} parameters")
```

Load parameters from file:
```python
from mddata.templates import load_params_from_file

params_dict = load_params_from_file('params.yaml')
# or params.json - format auto-detected
```

## Creating Your Own Templates

1. Start with a simple template (like `log-entry.yaml`)
2. Add required parameters with descriptions
3. Use computed parameters for timestamps and environment info
4. Add constraints for validation
5. Test with various parameter values
6. Document expected usage

## Notes

- **CLI Integration**: The `mddata modify from-template` command (Task 022) is not yet implemented
- **Current Usage**: Templates can be loaded and used programmatically via the Python API
- **All Features**: Parameter parsing, validation, computed params, and substitution are fully functional
- **Testing**: All 88 unit tests pass for the template system core

## See Also

- [Template System Plan](../../plans/template_modifications.md) - Complete feature specification
- [Template Models](../../src/mddata/templates/models.py) - Pydantic model definitions
- [Template Tests](../../tests/unit/mddata/templates/) - Comprehensive test suite
