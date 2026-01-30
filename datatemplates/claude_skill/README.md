---
title: Datatemplates
description: Reusable markdown datatemplates with parameter substitution
version: 1.0.0
---

# Datatemplates

This directory contains reusable datatemplates for generating structured markdown documents using the mddata library. Datatemplates define the structure, parameters, and validation rules for markdown documents.

## What are Datatemplates?

Datatemplates are YAML or JSON files that define:
- **Parameters**: Customizable values with validation rules
- **Frontmatter**: Document metadata structure
- **Sections**: Content structure with heading levels
- **Schema**: Validation rules for the generated document

## Available Datatemplates

### claude-skill.yaml

Generates properly formatted Claude Code skill documents with:
- **Required fields**: skill_name, description, purpose, instructions
- **Optional fields**: allowed_tools, examples, additional_notes, version
- **Automatic date computation**: created field uses `{date}` placeholder
- **Validation**: skill_name pattern (lowercase, hyphens, max 64 chars), description max 1024 chars
- **Structure**: Nested sections format (Purpose, Instructions, Examples, Additional Notes)

## Usage

### Using the Python API (Recommended)

The Python API provides full control over datatemplate instantiation with proper parameter validation.

#### Basic usage with inline parameters:

```python
from mddata.utils import load_data_update
import yaml

# Load datatemplate with parameters
data_update = load_data_update(
    'datatemplates/claude-skill.yaml',
    format='yaml',
    cli_params=[
        'skill_name=my-skill',
        'description=My custom skill for specific tasks',
        'purpose=Detailed explanation of skill purpose',
        'instructions=Step-by-step instructions for using the skill',
        'allowed_tools=Read, Write, Edit',  # Optional
        'version=1.0.0'  # Optional
    ]
)

# Helper function to render nested sections
def render_section(section_data, level=2):
    """Render a section dict to markdown."""
    lines = []
    title = section_data.get('title', '')
    if title:
        lines.append(f"{'#' * level} {title}")
        lines.append('')
    content = section_data.get('content', '')
    if content:
        lines.append(content)
        lines.append('')
    return '\n'.join(lines)

# Generate markdown content
frontmatter_yaml = yaml.dump(data_update.frontmatter, default_flow_style=False, sort_keys=False)
markdown_parts = [f"---\n{frontmatter_yaml}---\n"]

# Render nested sections
if data_update.content:
    for section_id, section_data in data_update.content.items():
        section_md = render_section(section_data, section_data.get('level', 2))
        markdown_parts.append(section_md)

markdown_content = '\n'.join(markdown_parts)

# Write to file
with open('my-skill-SKILL.md', 'w') as f:
    f.write(markdown_content)
```

#### Using parameters from JSON file:

```python
from mddata.utils import load_data_update
import json
import yaml

# Load parameters from JSON file
with open('datatemplates/claude-skill-example.json') as f:
    params = json.load(f)

# Convert to CLI parameter format
cli_params = [f'{k}={v}' for k, v in params.items() if v]

# Load and fill datatemplate
data_update = load_data_update(
    'datatemplates/claude-skill.yaml',
    format='yaml',
    cli_params=cli_params
)

# Helper function to render nested sections
def render_section(section_data, level=2):
    """Render a section dict to markdown."""
    lines = []
    title = section_data.get('title', '')
    if title:
        lines.append(f"{'#' * level} {title}")
        lines.append('')
    content = section_data.get('content', '')
    if content:
        lines.append(content)
        lines.append('')
    return '\n'.join(lines)

# Generate markdown
frontmatter_yaml = yaml.dump(data_update.frontmatter, default_flow_style=False, sort_keys=False)
markdown_parts = [f"---\n{frontmatter_yaml}---\n"]

# Render nested sections
if data_update.content:
    for section_id, section_data in data_update.content.items():
        section_md = render_section(section_data, section_data.get('level', 2))
        markdown_parts.append(section_md)

markdown_content = '\n'.join(markdown_parts)

# Write to file
with open('api-client-helper-SKILL.md', 'w') as f:
    f.write(markdown_content)
```

### Parameter Validation

Datatemplates enforce validation on required parameters:

```python
# Missing required parameters
try:
    data_update = load_data_update(
        'datatemplates/claude-skill.yaml',
        format='yaml',
        cli_params=['skill_name=test']  # Missing description, purpose, instructions
    )
except Exception as e:
    print(f"Validation error: {e}")
    # Output: Missing required parameters: description, purpose, instructions

# Invalid pattern (skill_name must be lowercase with hyphens)
try:
    data_update = load_data_update(
        'datatemplates/claude-skill.yaml',
        format='yaml',
        cli_params=[
            'skill_name=InvalidName',  # Violates pattern
            'description=Test',
            'purpose=Test',
            'instructions=Test'
        ]
    )
except Exception as e:
    print(f"Pattern error: {e}")
    # Output: Value does not match pattern '^[a-z0-9-]{1,64}$'
```

### Inspecting Datatemplate Structure

```bash
# View datatemplate parameters
mddata info properties datatemplates/claude-skill.yaml

# View datatemplate structure
mddata info summary datatemplates/claude-skill.yaml

# View sections
mddata info sections datatemplates/claude-skill.yaml
```

## Parameter Types

Datatemplates support several parameter types:

### Basic Types
- `str` - String values
- `int` - Integer values
- `bool` - Boolean values

### Special Types
- `computed: date` - Auto-generates current date (YYYY-MM-DD)
- `computed: time` - Auto-generates current time (HH:MM:SS)
- `computed: env.VAR` - Reads from environment variable

### Validation Rules

Parameters can include validation rules:

```yaml
parameters:
  skill_name:
    type: str
    required: true
    validations:
      - type: pattern
        value: "^[a-z0-9-]{1,64}$"
        message: "Invalid format"

      - type: min_length
        value: 1
        message: "Must not be empty"

      - type: max_length
        value: 64
        message: "Must not exceed 64 characters"
```

## Creating New Datatemplates

To create a new datatemplate:

1. **Define Parameters**
   ```yaml
   parameters:
     param_name:
       type: str
       required: true
       description: "What this parameter is for"
       default: "optional default value"
   ```

2. **Define Frontmatter Structure**
   ```yaml
   frontmatter:
     title: "{{param_name}}"
     date: "{{computed_date}}"
   ```

3. **Define Sections**
   ```yaml
   sections:
     - id: section_id
       heading: "Section Title"
       level: 2
       content: "{{param_content}}"
   ```

4. **Add Schema Validation**
   ```yaml
   schema:
     frontmatter:
       title:
         type: str
         required: true
     sections:
       section_id:
         validation:
           required: true
           min_blocks: 1
   ```

## Examples

See `claude-skill-example.json` for a complete example of parameters that can be used with the claude-skill datatemplate.

## Best Practices

1. **Parameter Naming**: Use lowercase with underscores (e.g., `skill_name`)
2. **Required vs Optional**: Mark truly required fields as required
3. **Defaults**: Provide sensible defaults for optional parameters
4. **Validation**: Add validation rules for critical fields
5. **Documentation**: Include clear descriptions for all parameters
6. **Examples**: Provide example parameter files for complex datatemplates

## Related Documentation

- [mddata CLI Reference](../docs/CLI_REFERENCE.md)
- [mddata Python API](../README.md#python-api-reference)
- [Template System](../README.md#template-parameter-substitution-python-api)
- [Claude Code Skills Documentation](https://docs.claude.com/en/docs/claude-code/skills)
