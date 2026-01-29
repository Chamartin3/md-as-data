
**Complete Parameter Examples:**

```yaml
parameters:
  # Required string parameter
  title:
    type: str
    required: true
    description: "Document title"

  # String with pattern validation (email format)
  email:
    type: str
    required: true
    description: "Author email address"
    pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"

  # Integer with range constraints
  priority:
    type: int
    required: false
    description: "Task priority (1-10)"
    default: 5
    min: 1
    max: 10

  # Float with range constraints
  score:
    type: float
    required: false
    description: "Quality score (0.0-1.0)"
    default: 0.5
    min: 0.0
    max: 1.0

  # Boolean with default
  published:
    type: bool
    required: false
    description: "Publication status"
    default: false

  # Date parameter (YYYY-MM-DD format)
  created_date:
    type: date
    required: true
    description: "Creation date"
    default: "{{date}}"  # Computed value

  # Array parameter with item type
  tags:
    type: array
    required: false
    description: "Document tags"
    item_type: str
    default: []

  # String with enum-like pattern (status values)
  status:
    type: str
    required: false
    description: "Document status"
    default: "draft"
    pattern: "^(draft|review|published|archived)$"
```

**Available Parameter Types:**

| Type | Description | Example Value |
|------|-------------|---------------|
| `str` | String values | `"Hello World"` |
| `int` | Integer numbers | `42` |
| `float` | Floating-point numbers | `3.14` |
| `bool` | True/false values | `true` or `false` |
| `date` | Date values (YYYY-MM-DD) | `"2025-01-15"` |
| `array` | Array of items | `["tag1", "tag2"]` |

**Validation Constraints Reference:**

| Constraint | Applies To | Purpose | Example |
|------------|-----------|---------|---------|
| `min` | int, float | Minimum value | `min: 1` |
| `max` | int, float | Maximum value | `max: 100` |
| `pattern` | str | Regex validation | `pattern: "^\\w+$"` |
| `item_type` | array | Array element type | `item_type: str` |

**Computed Default Values:**

Use these special placeholders in `default` fields:

- `{{date}}` - Current date (YYYY-MM-DD format)
- `{{time}}` - Current time (HH:MM:SS format)
- `{{now}}` - Current datetime (ISO 8601 format)
- `{{env.VAR_NAME}}` - Environment variable value

**Parameter Design Guidelines:**

1. **Always specify `type`** - Required field, determines how the value is parsed
2. **Mark essential parameters as `required: true`**
3. **Provide sensible defaults** for optional parameters to improve user experience
4. **Add clear descriptions** to explain what each parameter does
5. **Use validation constraints** to ensure data quality:
   - `min/max` for numeric ranges (priority: 1-10, percentage: 0-100)
   - `pattern` for string formats (email, phone, slug, etc.)
   - `item_type` for typed arrays (tags, categories, etc.)
6. **Use computed defaults** for timestamps and dynamic values
