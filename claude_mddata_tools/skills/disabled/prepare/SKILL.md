---
name: md-prepare
description: Prepare for mddata CLI usage by checking installation, understanding command parameters, and validating data formats. Use this skill before executing mddata commands to ensure the tool is available and data structures match expected formats (MarkdownDataDict for generation, schema format for validation).
allowed-tools: Bash(mddata:*), Bash(which:*), Read
---

# Markdown Data Preparation Skill

## Purpose

Prepare for mddata CLI usage by checking installation and validating data structures before executing commands. This skill ensures that:

1. The mddata tool is installed and accessible
2. Data passed to commands matches expected formats
3. Schemas are valid before validation operations
4. Command parameters are understood before execution

## Prerequisites

- `mddata` command must be available in PATH

## Core Operations

### 1. Check Installation

Verify mddata is installed and accessible:

```bash
# Check if mddata is available
which mddata

# Check mddata version and help
mddata --help
```

**Expected output:**
- Path to mddata executable (e.g., `/path/to/bin/mddata`)
- Help message showing available commands

**If mddata not found:**
- Report that mddata is not installed
- Inform user that mddata operations cannot be performed
- Do not proceed with mddata operations

### 2. Understand Command Parameters

Before executing any mddata command, verify what parameters it accepts:

```bash
# Get help for specific command
mddata write --help
mddata schema validate --help
mddata extract --help
mddata info --help
mddata modify --help

# View all available commands
mddata --help
```

**Key information to extract:**
- Required vs optional parameters
- Input format expectations (JSON, YAML, markdown file path)
- Output options (file, stdout)
- Flags and their meanings

### 3. Validate Data Format (JSON/YAML)

**Before using `mddata write --data`**, verify the data structure:

A valid MarkdownDataDict must have this structure:

```json
{
  "frontmatter": {
    "property_name": "value"
  },
  "content": {
    "id": "",
    "title": "",
    "level": 0,
    "path": "",
    "blocks": [],
    "children": [
      {
        "id": "section_id",
        "title": "Section Title",
        "level": 1,
        "path": "section_id",
        "blocks": [
          {
            "section_id": "section_id",
            "type": "paragraph",
            "content": "Block content",
            "metadata": {}
          }
        ],
        "children": []
      }
    ]
  }
}
```

**Validation checklist:**
- ✓ Has `frontmatter` key (object)
- ✓ Has `content` key (object)
- ✓ Content has required fields: `id`, `title`, `level`, `path`, `blocks`, `children`
- ✓ Root section has `level: 0`
- ✓ Each child section has required fields
- ✓ Each block has: `section_id`, `type`, `content`, `metadata`
- ✓ Block types are valid: `paragraph`, `code_block`, `list`, `ordered_list`, `task_list`, `blockquote`, `link`, `image`, `table`

**Verify using jq:**
```bash
# Check if file has required keys
cat data.json | jq 'has("frontmatter") and has("content")'

# Verify content structure
cat data.json | jq '.content | has("id") and has("title") and has("level") and has("path") and has("blocks") and has("children")'

# Count sections and blocks
cat data.json | jq '.content.children | length'
cat data.json | jq '[.content.children[].blocks] | add | length'
```

### 4. Validate Schema Format

**Before using `mddata schema validate`**, verify the schema structure:

A valid schema must have this structure:

```json
{
  "version": "1.0.0",
  "properties": {
    "property_name": {
      "type": "str|int|float|bool|list|dict",
      "required": true,
      "default": "value",
      "description": "Property description",
      "enum": ["option1", "option2"],
      "validations": [
        {
          "type": "min_length|max_length|min_value|max_value|pattern",
          "value": "constraint_value",
          "message": "Error message"
        }
      ]
    }
  },
  "sections": {
    "section_id": {
      "description": "Section description",
      "validation": {
        "required": true,
        "min_blocks": 1,
        "max_blocks": 10,
        "allowed_content": ["paragraph", "code_block"]
      },
      "children": {}
    }
  }
}
```

**Schema validation checklist:**
- ✓ Valid JSON or YAML syntax
- ✓ Has `properties` and/or `sections` keys
- ✓ Property types are valid: `str`, `int`, `float`, `bool`, `list`, `dict`, or union types
- ✓ Validation types are valid: `min_length`, `max_length`, `min_value`, `max_value`, `pattern`
- ✓ Section `allowed_content` uses valid block types
- ✓ Validation level (if present) is `strict`, `warnings`, or `disabled`

**Verify using jq/yq:**
```bash
# Validate JSON syntax
cat schema.json | jq . > /dev/null && echo "Valid JSON"

# Check for required schema keys
cat schema.json | jq 'has("properties") or has("sections")'

# List all property types
cat schema.json | jq '.properties | to_entries[] | "\(.key): \(.value.type)"'

# Verify YAML schema
cat schema.yaml | yq . > /dev/null && echo "Valid YAML"
```

## Usage Examples

### Example 1: Pre-Generation Verification

```
User: "Generate markdown from this data.json file"

Before executing mddata generate:

1. Check mddata is installed:
   which mddata

2. If not found, report:
   "I cannot use mddata because it is not installed. Please install mddata first."
   → STOP, do not proceed

3. If found, check data structure:
   cat data.json | jq 'has("frontmatter") and has("content")'

4. If valid, proceed with generation:
   mddata write --data data.json --output document.md

5. If invalid, explain the required structure and reference MARKDOWN_DATA.md
```

### Example 2: Schema Validation Setup

```
User: "Validate this document against schema.json"

Before executing validation:

1. Check mddata is installed:
   which mddata

2. If not found, report:
   "I cannot use mddata because it is not installed. Please install mddata first."
   → STOP, do not proceed

3. If found, verify schema format:
   cat schema.json | jq 'has("properties") or has("sections")'

4. Check schema property types:
   cat schema.json | jq '.properties | to_entries[] | .value.type'

5. If valid schema, proceed:
   mddata schema validate document.md schema.json --verbose

6. If invalid, explain schema structure and reference MARKDOWN_SCHEMA.md
```

### Example 3: Installation Check

```
User: "I want to use mddata to work with markdown files"

1. Check if mddata is installed:
   which mddata

2. If not found, report:
   "I cannot use mddata because it is not installed on this system.
   Please install mddata first, then I can help you work with markdown files."
   → STOP, do not suggest mddata commands

3. If found, verify it works:
   mddata --help

4. Show available commands and suggest starting point
```

### Example 4: Data Format Assistance

```
User: "What format does mddata write expect?"

1. Explain MarkdownDataDict structure
2. Reference MARKDOWN_DATA.md for complete specification
3. Provide minimal working example:

{
  "frontmatter": {
    "title": "Document Title"
  },
  "content": {
    "id": "",
    "title": "",
    "level": 0,
    "path": "",
    "blocks": [],
    "children": [
      {
        "id": "intro",
        "title": "Introduction",
        "level": 2,
        "path": "intro",
        "blocks": [
          {
            "section_id": "intro",
            "type": "paragraph",
            "content": "Introduction text.",
            "metadata": {}
          }
        ],
        "children": []
      }
    ]
  }
}

4. Suggest using extract command to see examples:
   mddata extract json existing-doc.md --pretty
```

## Data Format References

### MarkdownDataDict Format

For complete specification, see: `MARKDOWN_DATA.md` (in this skill directory)

**Key requirements:**
1. Must have `frontmatter` (object) and `content` (object)
2. Frontmatter can contain any valid JSON/YAML types
3. Content must have root section with `level: 0`
4. Each section needs: `id`, `title`, `level`, `path`, `blocks`, `children`
5. Each block needs: `section_id`, `type`, `content`, `metadata`
6. Block types: `paragraph`, `code_block`, `list`, `ordered_list`, `task_list`, `blockquote`, `link`, `image`, `table`

### Schema Format

For complete specification, see: `MARKDOWN_SCHEMA.md` (in this skill directory)

**Key requirements:**
1. Must have `properties` and/or `sections`
2. Property types: `str`, `int`, `float`, `bool`, `list`, `dict`, or union types (e.g., `str|int`)
3. Validation types: `min_length`, `max_length`, `min_value`, `max_value`, `pattern`
4. Section validation: `required`, `min_blocks`, `max_blocks`, `allowed_content`
5. Validation levels: `strict`, `warnings`, `disabled`

## Best Practices

### Always Check Installation First

1. **Verify mddata is available** before any operation
2. **Stop immediately** if mddata is not found
3. **Do not suggest mddata commands** if tool is missing
4. **Inform user clearly** when mddata is not available

### Validate Before Executing

1. **Check data format** before generation operations
2. **Verify schema structure** before validation operations
3. **Reference documentation** when explaining formats
4. **Provide examples** alongside explanations

### Use Progressive Disclosure

1. Start with simple checks (`which mddata`)
2. Validate structure before detailed validation
3. Reference complete documentation for complex cases
4. Show minimal examples first, then point to full specs

### Error Prevention

1. **Don't guess** data formats - verify or reference docs
2. **Always check** if mddata is installed before suggesting commands
3. **Validate JSON/YAML** syntax before processing
4. **Explain requirements** when validation fails
5. **Reference specifications** instead of making assumptions

---

## Schema Design Best Practices

This section provides guidelines for creating well-designed, maintainable schemas for markdown documents.

### Schema Design Philosophy

#### Start Permissive, Tighten Gradually

Begin with flexible schemas and add constraints as patterns emerge:

```yaml
# Initial schema (permissive)
properties:
  title:
    type: str
    required: true

  tags:
    type: list
    required: false

# Evolved schema (constraints added)
properties:
  title:
    type: str
    required: true
    validations:
      - type: min_length
        value: 10
        message: "Title too short (min 10 chars)"
      - type: max_length
        value: 100
        message: "Title too long (max 100 chars)"

  tags:
    type: list
    required: false
    validations:
      - type: min_length
        value: 1
        message: "At least one tag required"
```

**Why this approach:**
- Allows document evolution
- Prevents over-constraining early
- Based on real usage patterns
- Easier team adoption

#### Document Everything

Always include descriptions for properties and sections:

```yaml
# Good: Well-documented schema
properties:
  status:
    type: str
    required: true
    default: draft
    enum: [draft, review, published, archived]
    description: "Document publication status. Use 'draft' for work in progress, 'review' for peer review, 'published' for finalized content, and 'archived' for obsolete documents."

sections:
  api_reference:
    description: "Complete API endpoint reference with request/response examples. Include authentication requirements and common error codes."
    validation:
      required: true
      allowed_content: [paragraph, code_block, table]
```

```yaml
# Bad: Undocumented schema
properties:
  status:
    type: str
    enum: [draft, review, published, archived]

sections:
  api_reference:
    validation:
      required: true
```

**Benefits:**
- Self-documenting schemas
- Clear requirements for document authors
- Easier onboarding for new team members
- Better tooling support

### Property Design Guidelines

#### Type Selection

Choose the most specific type that accurately represents the data:

```yaml
# Good type choices
properties:
  # Text content
  title:
    type: str

  # Numeric values
  priority:
    type: int           # Discrete values (1, 2, 3)

  score:
    type: float         # Continuous values (0.85, 2.5)

  # Boolean flags
  published:
    type: bool

  # Collections
  tags:
    type: list

  metadata:
    type: dict

  # Union types for flexibility
  version:
    type: str|int       # Supports "1.0" or 1

  optional_field:
    type: str|null      # Explicitly nullable
```

```yaml
# Bad type choices
properties:
  # Too generic
  priority:
    type: str           # Should be int for numeric priority

  # Ambiguous nullability
  optional_field:
    type: str           # Unclear if null is valid
```

**Guidelines:**
- Use `str` for text, identifiers, formatted data (dates, emails)
- Use `int` for whole numbers, counts, discrete levels
- Use `float` for measurements, scores, percentages
- Use `bool` for flags, binary states
- Use `list` for collections, arrays
- Use `dict` for nested structures
- Use union types (`str|int`) when multiple types are valid
- Always include `null` in union if property can be null

#### Required vs Optional Properties

Mark properties as `required: true` only when they are **essential** to document validity:

```yaml
# Good: Essential properties required
properties:
  title:
    type: str
    required: true      # Every document needs a title
    validations:
      - type: min_length
        value: 1
        message: "Title cannot be empty"

  author:
    type: str
    required: true      # Authorship tracking is critical

  created_date:
    type: str
    required: true      # Audit trail requirement

  # Optional enhancement properties
  tags:
    type: list
    required: false     # Nice to have, not essential
    default: []

  excerpt:
    type: str
    required: false     # Optional summary

  last_reviewed:
    type: str
    required: false     # Only set after review
```

```yaml
# Bad: Over-constraining with too many required fields
properties:
  title:
    required: true
  author:
    required: true
  tags:
    required: true      # Don't force tags if not essential
  excerpt:
    required: true      # Don't force summaries
  version:
    required: true      # Version might not apply to all docs
  category:
    required: true      # Categories might emerge organically
```

**Decision criteria:**
- **Required = true**: Property is fundamental to document purpose
- **Required = false**: Property is enhancement, metadata, or workflow-specific

**Multi-file schema consideration:**
When generating schemas from multiple documents, properties appearing in ≥75% of files are marked required. Review and adjust based on actual necessity.

#### Default Values

Provide sensible defaults for optional properties:

```yaml
# Good defaults
properties:
  status:
    type: str
    required: false
    default: draft              # Logical starting state
    enum: [draft, review, published]

  version:
    type: int
    required: false
    default: 1                  # Start at version 1

  draft:
    type: bool
    required: false
    default: true               # Safe default: unpublished

  tags:
    type: list
    required: false
    default: []                 # Empty list, not null

  priority:
    type: int
    required: false
    default: 3                  # Middle priority
    validations:
      - type: min_value
        value: 1
      - type: max_value
        value: 5
```

```yaml
# Bad defaults
properties:
  status:
    type: str
    required: false
    default: published          # Dangerous: auto-publishes

  priority:
    type: int
    required: false
    default: 10                 # Outside valid range (1-5)

  tags:
    type: list
    required: false
    default: null               # Use [] instead
```

**Guidelines:**
- Defaults should be **safe** (prefer conservative values)
- Defaults must match the specified type
- For enums, default to the most common or safest value
- For lists, use `[]` not `null`
- For numbers, choose middle-range or neutral values
- Document why a particular default was chosen

#### Enum vs Union Types

Use enums for categorical values, union types for type flexibility:

```yaml
# Use ENUM for: Fixed set of categorical values
properties:
  status:
    type: str
    enum: [draft, review, published, archived]
    description: "Document status"

  priority:
    type: str
    enum: [low, medium, high, urgent]
    description: "Priority level"

  doc_type:
    type: str
    enum: [guide, tutorial, reference, api]
    description: "Document category"

# Use UNION for: Multiple valid types
properties:
  version:
    type: str|int               # "1.0" or 1 both valid
    description: "Version identifier"

  id:
    type: str|int               # String UUID or numeric ID
    description: "Document identifier"

  optional_value:
    type: str|null              # Explicitly nullable
    description: "Optional configuration value"
```

**Decision criteria:**
- **Enum**: Value is one of a fixed, known set of options
- **Union**: Value can be different types but constrained set isn't applicable
- **Enum with null**: `enum: [value1, value2, null]` for optional categorical

**Auto-generated enums:**
When using `mddata schema infer`, enums are automatically created for single-word string properties with consistent values across documents. Review and refine these.

#### Property Naming Conventions

Use clear, consistent naming:

```yaml
# Good naming
properties:
  # Use snake_case
  created_date: ...
  last_modified: ...
  author_email: ...

  # Be specific
  publication_date: ...        # Not just "date"
  primary_author: ...          # Not just "author"
  target_audience: ...         # Not just "audience"

  # Use standard suffixes
  is_published: ...            # Boolean flag
  has_review: ...              # Boolean flag
  max_length: ...              # Numeric limit
  min_score: ...               # Numeric threshold

# Bad naming
properties:
  # Inconsistent case
  createdDate: ...             # camelCase mixed with snake_case
  last-modified: ...           # kebab-case in some fields

  # Too generic
  date: ...                    # Which date?
  author: ...                  # Primary? Contributing?
  value: ...                   # Value of what?

  # Unclear
  flag1: ...                   # What does it flag?
  temp: ...                    # Temporary what?
```

**Conventions:**
- **snake_case** for all property names
- **Descriptive names** that indicate purpose
- **Boolean prefixes**: `is_`, `has_`, `should_`, `can_`
- **Numeric suffixes**: `_count`, `_total`, `_min`, `_max`, `_score`
- **Temporal suffixes**: `_date`, `_time`, `_timestamp`, `_at`

### Validation Rule Design

#### When to Add Validations

Add validation rules when you need to enforce specific constraints:

```yaml
# Good: Validations for business rules
properties:
  email:
    type: str
    required: true
    validations:
      - type: pattern
        value: "^[^@]+@[^@]+\\.[^@]+$"
        message: "Invalid email format"

  title:
    type: str
    required: true
    validations:
      - type: min_length
        value: 10
        message: "Title too short (minimum 10 characters)"
      - type: max_length
        value: 100
        message: "Title too long (maximum 100 characters)"

  priority:
    type: int
    required: true
    validations:
      - type: min_value
        value: 1
        message: "Priority must be at least 1"
      - type: max_value
        value: 5
        message: "Priority cannot exceed 5"

  publish_date:
    type: str
    required: false
    validations:
      - type: pattern
        value: "^\\d{4}-\\d{2}-\\d{2}$"
        message: "Date must be YYYY-MM-DD format"
```

```yaml
# Bad: Over-constraining or missing key validations
properties:
  email:
    type: str
    required: true              # Missing email pattern validation

  title:
    type: str
    required: true
    validations:
      - type: min_length
        value: 50               # Too restrictive
        message: "Title too short"

  priority:
    type: int
    required: true              # No range validation (1-5)
```

**When to add validations:**
- **Format requirements**: Email, URL, date formats
- **Business constraints**: Priority ranges, character limits
- **Data quality**: Non-empty strings, positive numbers
- **Consistency**: Standard formats across documents

**When NOT to add validations:**
- Don't over-constrain content that might evolve
- Avoid arbitrary limits without business justification
- Skip validations that duplicate type checking

#### Validation Error Messages

Write clear, actionable error messages:

```yaml
# Good messages: Specific and helpful
properties:
  title:
    type: str
    validations:
      - type: min_length
        value: 10
        message: "Title too short. Provide at least 10 characters for clarity."

      - type: max_length
        value: 100
        message: "Title exceeds 100 character limit. Consider shortening."

  email:
    type: str
    validations:
      - type: pattern
        value: "^[^@]+@[^@]+\\.[^@]+$"
        message: "Invalid email format. Expected: user@domain.com"

  priority:
    type: int
    validations:
      - type: min_value
        value: 1
        message: "Priority must be between 1 (highest) and 5 (lowest)."
```

```yaml
# Bad messages: Vague and unhelpful
properties:
  title:
    type: str
    validations:
      - type: min_length
        value: 10
        message: "Invalid"               # What's invalid?

  email:
    type: str
    validations:
      - type: pattern
        value: "^[^@]+@[^@]+\\.[^@]+$"
        message: "Wrong format"          # What format is expected?

  priority:
    type: int
    validations:
      - type: min_value
        value: 1
        message: "Too low"               # How low is too low?
```

**Message guidelines:**
- **Explain the constraint**: What rule was violated?
- **Provide the requirement**: What is expected?
- **Give examples** when format is complex
- **Be specific**: Include actual limits/patterns
- **Be helpful**: Guide users to correct the issue

### Section Design Guidelines

#### Section Structure

Design section hierarchies that reflect document organization:

```yaml
# Good: Logical hierarchy
sections:
  overview:
    description: "Document overview and purpose"
    validation:
      required: true
      min_blocks: 1
      max_blocks: 3
      allowed_content: [paragraph]

  getting_started:
    description: "Quick start guide"
    validation:
      required: true
    children:
      prerequisites:
        description: "Required software and knowledge"
        validation:
          required: true
          allowed_content: [list, paragraph]

      installation:
        description: "Installation instructions"
        validation:
          required: true
          min_blocks: 1
          allowed_content: [code_block, paragraph, ordered_list]

      first_steps:
        description: "First steps tutorial"
        validation:
          required: false
          allowed_content: [paragraph, code_block]

  reference:
    description: "Detailed reference documentation"
    validation:
      required: false
    children:
      api:
        description: "API documentation"
      commands:
        description: "Command reference"
```

```yaml
# Bad: Flat, unclear hierarchy
sections:
  intro:                        # Unclear naming
    validation:
      required: true

  section1:                     # Non-descriptive ID
    validation:
      required: true

  section2:
    validation:
      required: false

  misc:                         # Too generic
    children:
      stuff:                    # Non-descriptive
        ...
```

**Guidelines:**
- **Descriptive IDs**: Use meaningful section identifiers
- **Logical nesting**: Group related subsections
- **Clear descriptions**: Explain section purpose
- **Consistent depth**: Don't nest unnecessarily deep

#### Section Validation Constraints

Set appropriate content constraints for sections:

```yaml
# Good: Appropriate constraints
sections:
  introduction:
    description: "Opening section providing document overview"
    validation:
      required: true
      min_blocks: 1             # At least some content
      max_blocks: 5             # Keep it concise
      allowed_content: [paragraph]

  examples:
    description: "Working code examples"
    validation:
      required: false           # Optional for some docs
      min_blocks: 1             # If present, need at least one
      allowed_content: [code_block, paragraph]

  changelog:
    description: "Version history"
    validation:
      required: false
      allowed_content: [ordered_list, paragraph, code_block]
```

```yaml
# Bad: Over-constraining or missing constraints
sections:
  introduction:
    validation:
      required: true
      min_blocks: 10            # Too restrictive
      max_blocks: 10            # Forces exact block count
      allowed_content: [paragraph]  # Maybe lists needed?

  examples:
    validation:
      required: true            # Forces examples in all docs
      allowed_content: [code_block]  # No explanatory text allowed?
```

**Constraint guidelines:**
- **min_blocks**: Use to ensure content presence, not exact counts
- **max_blocks**: Use sparingly, mainly for summaries/overviews
- **allowed_content**: Include all reasonable block types for the section
- **required**: Only for truly essential sections

### Schema Evolution Strategies

#### Versioning

Track schema changes with version identifiers:

```yaml
# Version 1.0.0: Initial schema
version: "1.0.0"
properties:
  title:
    type: str
    required: true
  author:
    type: str
    required: true

# Version 1.1.0: Added optional properties (backward compatible)
version: "1.1.0"
properties:
  title:
    type: str
    required: true
  author:
    type: str
    required: true
  tags:                         # New optional field
    type: list
    required: false
    default: []

# Version 2.0.0: Breaking changes (new required field)
version: "2.0.0"
properties:
  title:
    type: str
    required: true
  author:
    type: str
    required: true
  document_type:                # New REQUIRED field
    type: str
    required: true
    enum: [guide, tutorial, reference]
  tags:
    type: list
    required: false
    default: []
```

**Versioning rules:**
- **Patch (1.0.X)**: Documentation, descriptions, non-breaking clarifications
- **Minor (1.X.0)**: New optional properties, relaxed constraints
- **Major (X.0.0)**: New required properties, stricter constraints, removed properties

#### Backward Compatibility

Maintain compatibility when evolving schemas:

```yaml
# Good: Backward compatible evolution
# Version 1.0
properties:
  status:
    type: str
    enum: [draft, published]

# Version 1.1: Added new status value (compatible)
properties:
  status:
    type: str
    enum: [draft, review, published]  # Added 'review'
    description: "Added 'review' status for peer review workflow"

# Good: Using defaults for new fields
# Version 1.1: New optional field with default
properties:
  reviewed:
    type: bool
    required: false
    default: false              # Existing docs get default
```

```yaml
# Bad: Breaking compatibility
# Version 1.0
properties:
  status:
    type: str
    enum: [draft, published]

# Version 2.0: Removed valid value (BREAKS existing docs)
properties:
  status:
    type: str
    enum: [published]           # Removed 'draft'

# Bad: Making optional field required
# Version 1.0
properties:
  tags:
    type: list
    required: false

# Version 2.0: Now required (BREAKS existing docs)
properties:
  tags:
    type: list
    required: true              # Existing docs without tags now invalid
```

**Compatibility guidelines:**
- **Safe changes**: Add optional fields, add enum values, relax constraints
- **Breaking changes**: Add required fields, remove enum values, tighten constraints
- **Migration path**: Provide defaults or migration tools for breaking changes

### Common Schema Patterns

#### Document Status Workflow

```yaml
properties:
  status:
    type: str
    required: true
    default: draft
    enum: [draft, review, published, archived]
    description: "Document publication workflow status"

  draft:
    type: bool
    required: false
    default: true
    description: "Quick draft flag (deprecated, use status field)"

  published_date:
    type: str
    required: false
    description: "Date document was published (YYYY-MM-DD)"
    validations:
      - type: pattern
        value: "^\\d{4}-\\d{2}-\\d{2}$"
        message: "Date must be YYYY-MM-DD format"

  last_reviewed:
    type: str
    required: false
    description: "Date of last review (YYYY-MM-DD)"
```

#### Authorship and Attribution

```yaml
properties:
  author:
    type: str
    required: true
    description: "Primary document author"

  contributors:
    type: list
    required: false
    default: []
    description: "Additional contributors"

  author_email:
    type: str
    required: false
    description: "Primary author contact email"
    validations:
      - type: pattern
        value: "^[^@]+@[^@]+\\.[^@]+$"
        message: "Invalid email format"

  organization:
    type: str
    required: false
    description: "Authoring organization"
```

#### Categorization and Taxonomy

```yaml
properties:
  category:
    type: str
    required: false
    enum: [guide, tutorial, reference, api, concept]
    description: "Primary document category"

  tags:
    type: list
    required: false
    default: []
    description: "Topic tags for discovery"

  audience:
    type: str
    required: false
    enum: [beginner, intermediate, advanced, expert]
    description: "Target audience skill level"

  topics:
    type: list
    required: false
    default: []
    description: "Specific topics covered"
```

#### Versioning and Changelog

```yaml
properties:
  version:
    type: str
    required: true
    default: "1.0.0"
    description: "Document semantic version"
    validations:
      - type: pattern
        value: "^\\d+\\.\\d+\\.\\d+$"
        message: "Version must be semantic (X.Y.Z)"

  last_updated:
    type: str
    required: false
    description: "Last modification date (YYYY-MM-DD)"

  changelog_url:
    type: str
    required: false
    description: "Link to detailed changelog"

sections:
  changelog:
    description: "Version history and changes"
    validation:
      required: false
      allowed_content: [ordered_list, paragraph]
```

### Schema Testing and Validation

#### Test Your Schemas

Always test schemas with representative documents:

```bash
# 1. Generate schema from example
mddata schema infer good_example.md --output test_schema.json --pretty

# 2. Validate against multiple documents
mddata schema validate doc1.md test_schema.json --verbose
mddata schema validate doc2.md test_schema.json --verbose
mddata schema validate doc3.md test_schema.json --verbose

# 3. Test template generation
mddata write --schema test_schema.json --output template.md

# 4. Validate template against itself
mddata schema validate template.md test_schema.json --verbose

# 5. Test edge cases
# - Document with all optional fields omitted
# - Document with all optional fields present
# - Document with maximum constraints
# - Document with minimal content
```

#### Schema Quality Checklist

Before finalizing a schema, verify:

**Properties:**
- [ ] All properties have descriptions
- [ ] Required properties are truly essential
- [ ] Optional properties have sensible defaults
- [ ] Enum values cover all expected cases
- [ ] Union types are necessary (not just lazy typing)
- [ ] Validation rules have clear error messages
- [ ] Property names follow snake_case convention
- [ ] Types match the actual data (str vs int vs bool)

**Sections:**
- [ ] All sections have descriptions
- [ ] Section IDs are descriptive
- [ ] Required sections are truly mandatory
- [ ] Block count constraints are reasonable
- [ ] allowed_content includes all needed block types
- [ ] Hierarchy reflects logical document structure
- [ ] Child sections are properly nested

**Overall:**
- [ ] Schema has a version identifier
- [ ] Schema is tested with real documents
- [ ] Template generates successfully
- [ ] Schema is documented (comments, README)
- [ ] Breaking changes are noted in version
- [ ] Migration path exists for breaking changes

### Common Schema Anti-Patterns

Avoid these common mistakes:

#### Over-Constraining

```yaml
# Bad: Too restrictive
properties:
  title:
    type: str
    required: true
    validations:
      - type: min_length
        value: 50               # Arbitrary high minimum
      - type: max_length
        value: 50               # Forces exact length!
      - type: pattern
        value: "^[A-Z].*\\.$"   # Must start with capital, end with period

sections:
  introduction:
    validation:
      required: true
      min_blocks: 5             # Arbitrary minimum
      max_blocks: 5             # Forces exact count
      allowed_content: [paragraph]  # Only paragraphs, no flexibility
```

```yaml
# Good: Reasonable constraints
properties:
  title:
    type: str
    required: true
    validations:
      - type: min_length
        value: 10               # Reasonable minimum
      - type: max_length
        value: 100              # Reasonable maximum

sections:
  introduction:
    validation:
      required: true
      min_blocks: 1             # At least some content
      allowed_content: [paragraph, list]  # Flexibility
```

#### Under-Documenting

```yaml
# Bad: No documentation
properties:
  s: ...
  f: ...
  x: ...

sections:
  sec1: ...
  sec2: ...
```

```yaml
# Good: Clear documentation
properties:
  status:
    type: str
    description: "Document publication status"
    ...

  feature_flag:
    type: bool
    description: "Enable experimental features"
    ...

sections:
  introduction:
    description: "Opening section providing document overview"
    ...
```

#### Inconsistent Naming

```yaml
# Bad: Mixed conventions
properties:
  createdDate: ...          # camelCase
  last-modified: ...        # kebab-case
  UpdatedBy: ...            # PascalCase
  is_published: ...         # snake_case

sections:
  getStarted: ...
  API-Reference: ...
  final_notes: ...
```

```yaml
# Good: Consistent snake_case
properties:
  created_date: ...
  last_modified: ...
  updated_by: ...
  is_published: ...

sections:
  getting_started: ...
  api_reference: ...
  final_notes: ...
```

#### Missing Defaults for Optional Fields

```yaml
# Bad: Optional without defaults
properties:
  tags:
    type: list
    required: false           # What happens when omitted?

  priority:
    type: int
    required: false           # Unclear default behavior
```

```yaml
# Good: Clear defaults
properties:
  tags:
    type: list
    required: false
    default: []               # Empty list when omitted

  priority:
    type: int
    required: false
    default: 3                # Middle priority
    validations:
      - type: min_value
        value: 1
      - type: max_value
        value: 5
```

### Schema Generation Modes

#### Permissive Mode (Recommended for Initial Schemas)

```bash
mddata schema infer document.md --output schema.json
```

**Characteristics:**
- Properties optional unless present in ≥75% of documents
- Flexible block counts
- Wide allowed_content ranges
- Good for evolving documentation

**Use when:**
- Starting a new documentation project
- Documents are still evolving
- You want to allow flexibility
- Team is still learning patterns

#### Strict Mode (For Templates and Standards)

```bash
mddata schema infer document.md --mode strict --output schema.json
```

**Characteristics:**
- All present properties marked required
- Exact block counts (min = max = actual)
- Strict content type restrictions
- Good for enforcing templates

**Use when:**
- Creating templates for repeated document types
- Enforcing strict standards
- Generating forms/structured input
- All documents must match exactly

### Multi-File Schema Generation Best Practices

When generating schemas from multiple documents:

```bash
# Generate from directory
mddata schema infer ./docs/ --output docs_schema.json --pretty
```

**Review and refine the generated schema:**

1. **Check required properties**: Properties in ≥75% of files are marked required. Verify this threshold makes sense for your use case.

2. **Review enum types**: Auto-generated enums for single-word strings. Verify these are truly categorical.

3. **Check union types**: Conflicting types create unions (e.g., `str|int`). Decide if this is intentional or needs fixing.

4. **Validate merged sections**: All section hierarchies are merged. Check for unintended structure.

5. **Test with all documents**: Validate schema against all source documents to ensure compatibility.

Example refinement:

```bash
# 1. Generate initial schema
mddata schema infer ./docs/ --output initial_schema.json --pretty

# 2. Review and edit schema manually
# - Adjust required properties
# - Refine enum values
# - Add descriptions
# - Fix union types

# 3. Validate against all documents
for doc in ./docs/*.md; do
  mddata schema validate "$doc" initial_schema.json --verbose
done

# 4. Iterate until all pass
```

---

## Schema Design Workflow

Recommended workflow for creating and maintaining schemas:

### 1. Initial Schema Creation

```bash
# Option A: Generate from example document
mddata schema infer example.md --output schema.json --pretty

# Option B: Generate from document set
mddata schema infer ./docs/ --output schema.json --pretty

# Option C: Write schema manually (for greenfield projects)
```

### 2. Review and Refine

Edit the schema file:
- Add descriptions to all properties and sections
- Adjust required/optional settings
- Add validation rules
- Set appropriate defaults
- Refine enum values
- Document any constraints

### 3. Test with Real Documents

```bash
# Validate representative documents
mddata schema validate doc1.md schema.json --verbose
mddata schema validate doc2.md schema.json --verbose

# Generate template
mddata write --schema schema.json --output template.md

# Validate template against itself
mddata schema validate template.md schema.json --verbose
```

### 4. Document the Schema

Create a README or documentation for the schema:
- Purpose and use cases
- Version history
- Property descriptions
- Required vs optional rationale
- Examples of valid documents
- Migration guides for breaking changes

### 5. Iterate Based on Feedback

- Collect validation errors from team
- Identify over-constraints or missing flexibility
- Update schema version
- Document changes
- Communicate updates to team

### 6. Maintain Over Time

- Review schema quarterly
- Update based on document evolution
- Add new optional properties
- Deprecate unused properties
- Version appropriately (semantic versioning)

## Error Handling

### mddata Not Found

```
Error: mddata: command not found

Response:
"I cannot use mddata because it is not installed on this system.
Please install mddata first, then I can help you work with markdown files."

→ STOP: Do not proceed with mddata operations if the tool is not available.
```

### Invalid Data Format

```
Error: Invalid MarkdownDataDict format

Solution:
1. Check required keys: jq 'has("frontmatter") and has("content")' data.json
2. Validate content structure
3. Reference MARKDOWN_DATA.md for complete spec
4. Use extract command to see valid example:
   mddata extract json valid-doc.md --pretty > example.json
```

### Invalid Schema Format

```
Error: Invalid schema structure

Solution:
1. Validate JSON/YAML syntax
2. Check for required keys: properties or sections
3. Verify property types are valid
4. Reference MARKDOWN_SCHEMA.md for spec
5. Generate example schema:
   mddata schema infer example.md --output example-schema.json --pretty
```

### Permission Errors

```
Error: Permission denied

Solution:
1. Check file permissions: ls -la file.json
2. Ensure readable: chmod +r file.json
3. Check output directory is writable
4. Verify PATH includes mddata location
```

## When to Use This Skill

Use md-prepare skill when:

1. **Starting to use mddata** in a new context
2. **Before executing any mddata command** to ensure installation
3. **User asks about data formats** for generation or schemas
4. **Validation fails** and need to understand why
5. **Creating data structures** and need to verify format
6. **User mentions mddata** but unclear if it's installed
7. **Any mddata operation** to verify prerequisites are met

## Integration with Other Skills

This skill should be used **before** other mddata skills:

```
User Request → md-prepare (check installation & format)
            ↓
            → md-query (if reading/inspecting)
            → md-schema (if validating/generating schemas)
            → md-generator (if creating markdown)
```

**Workflow:**
1. md-prepare: Ensure mddata is available and data is valid
2. Other skills: Execute operations with confidence

## Proactive Behavior

**Always prepare before executing mddata commands:**

1. When user mentions "generate from JSON" → Check installation and data format first
2. When user wants "validate with schema" → Check installation and schema format first
3. When suggesting mddata commands → Check installation first
4. When errors occur → Verify data/schema format

**Critical rule:** If `which mddata` fails, STOP and inform user. Do not proceed with mddata operations.

## Output

When using this skill:

1. **Report check results** clearly (✓ mddata available / ✗ mddata not found)
2. **Explain what's missing** if checks fail
3. **Reference documentation** for complete specifications
4. **Provide examples** of correct formats
5. **Suggest next steps** after preparation
6. **Be specific** about what's wrong and how to fix it

## Supporting Resources

### Reference Documents

Available in this skill directory:

- `MARKDOWN_DATA.md` - Complete MarkdownDataDict specification
  - Use cases and CLI commands
  - Structure overview (frontmatter, content, sections, blocks)
  - Block types reference with examples
  - Update data format for modifications
  - CLI usage and workflows

- `MARKDOWN_SCHEMA.md` - Complete schema format specification
  - Schema structure and validation rules
  - Property types and validations
  - Section validation constraints
  - Multi-file schema generation
  - Schema inference modes

### Quick Reference Cards

**MarkdownDataDict Minimal Structure:**
```json
{
  "frontmatter": {},
  "content": {
    "id": "",
    "title": "",
    "level": 0,
    "path": "",
    "blocks": [],
    "children": []
  }
}
```

**Schema Minimal Structure:**
```json
{
  "version": "1.0.0",
  "properties": {},
  "sections": {}
}
```

**Valid Block Types:**
- `paragraph`
- `code_block`
- `list`
- `ordered_list`
- `task_list`
- `blockquote`
- `link`
- `image`
- `table`

**Valid Property Types:**
- `str`
- `int`
- `float`
- `bool`
- `list`
- `dict`
- Union types: `str|int`, `str|null`, etc.

**Valid Validation Types:**
- `min_length`
- `max_length`
- `min_value`
- `max_value`
- `pattern`

## Summary

The md-prepare skill ensures reliable mddata operations by:

1. **Checking installation** before any operation
2. **Stopping immediately** if mddata is not available
3. **Validating data formats** against specifications
4. **Checking schema structures** before validation
5. **Referencing documentation** instead of guessing
6. **Preventing errors** through proactive preparation
7. **Providing clear guidance** when issues are found

**Remember:** Always check mddata installation first. If not found, stop and inform user. When in doubt about formats, reference `MARKDOWN_DATA.md` and `MARKDOWN_SCHEMA.md`.
