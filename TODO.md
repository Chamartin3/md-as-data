# TODO: Parameter Validation Enhancement - Phase 1

**Epic**: Parameter Validation Enhancement
**Phase**: 1 - Essential Features
**Estimated Effort**: 5-7 hours
**Status**: Completed
**Created**: 2025-10-26

---

## Overview

Implement enum support, array constraints, and pattern-based validation for template parameters to achieve feature parity with the schema validation system.

**Reference**: See `PARAMETER_VALIDATION_IMPROVEMENTS.md` for detailed specifications.

---

## Task Breakdown

### 1. Update Data Models (30 min)

**File**: `src/mddata/models/contracts.py`

- [ ] Add new fields to `ParameterDefinition` TypedDict:
  ```python
  # Enum support
  enum: list[str | int | float | bool | None]
  enum_descriptions: dict[str, str]
  enum_strict: bool

  # Array constraints
  min_items: int
  max_items: int
  unique_items: bool

  # Array item enum support
  item_enum: list[str | int | float | bool | None]
  item_enum_descriptions: dict[str, str]
  item_enum_strict: bool

  # Pattern validation for array items
  item_pattern: str
  ```

- [ ] Update docstring for `ParameterDefinition` to document new fields

**Acceptance Criteria**:
- TypedDict compiles without errors
- All fields are marked as `total=False` (optional)
- Docstring describes each new field clearly

---

### 2. Implement Enum Validation (1.5 hours)

**File**: `src/mddata/templates/filler.py`

#### 2.1 Update Imports
- [ ] Add `import warnings` at the top of the file

#### 2.2 Implement Enum Validation
- [ ] Modify `_validate_param_constraints()` function:
  - [ ] Add enum validation logic before existing constraints
  - [ ] Extract `enum`, `enum_strict`, `enum_descriptions` from `param_def`
  - [ ] Default `enum_strict` to `True` if not specified
  - [ ] Check if value is in enum values
  - [ ] Build helpful error message with descriptions
  - [ ] If `enum_strict=True`: raise `ValueError`
  - [ ] If `enum_strict=False`: issue `warnings.warn()` with `UserWarning`
  - [ ] Return early after enum check (skip other constraints)

**Implementation Reference**:
```python
def _validate_param_constraints(
    value: ParameterValue, param_def: ParameterDefinition
) -> None:
    """Validate parameter against constraints (min, max, pattern, enum)."""

    # NEW: Enum constraint (check first for better error messages)
    enum_values = param_def.get("enum")
    if enum_values is not None:
        enum_strict = param_def.get("enum_strict", True)
        enum_descriptions = param_def.get("enum_descriptions", {})

        if value not in enum_values:
            # Build helpful message
            allowed_str = ", ".join(str(v) for v in enum_values)
            msg = f"Value '{value}' not in enum values: [{allowed_str}]"

            if enum_descriptions:
                msg += "\n\nAvailable options:"
                for val in enum_values:
                    desc = enum_descriptions.get(str(val), "")
                    if desc:
                        msg += f"\n  {val} - {desc}"
                    else:
                        msg += f"\n  {val}"

            if enum_strict:
                raise ValueError(msg)
            else:
                warnings.warn(
                    f"Parameter validation warning: {msg}",
                    UserWarning,
                    stacklevel=2
                )
        return  # Skip other constraints after enum check

    # Existing constraints continue...
```

**Acceptance Criteria**:
- Strict enum raises `ValueError` with helpful message
- Non-strict enum issues warning but continues
- Error messages include descriptions when provided
- Error messages show all allowed values
- Validation happens before other constraints (min/max/pattern)

---

### 3. Implement Array Constraints (1 hour)

**File**: `src/mddata/templates/filler.py`

#### 3.1 Create Array Constraints Validator
- [ ] Add new function `_validate_array_constraints()` after `_validate_param_constraints()`:
  ```python
  def _validate_array_constraints(
      value: list[Any], param_def: ParameterDefinition
  ) -> None:
      """Validate array-specific constraints (min_items, max_items, unique_items)."""
      # Implementation here
  ```

- [ ] Implement min_items validation:
  - [ ] Get `min_items` from `param_def`
  - [ ] If set and `len(value) < min_items`, raise `ValueError`

- [ ] Implement max_items validation:
  - [ ] Get `max_items` from `param_def`
  - [ ] If set and `len(value) > max_items`, raise `ValueError`

- [ ] Implement unique_items validation:
  - [ ] Get `unique_items` from `param_def`
  - [ ] If `True` and `len(value) != len(set(value))`, raise `ValueError`

#### 3.2 Integrate with Array Parsing
- [ ] Update `_parse_array_param()` function:
  - [ ] Call `_validate_array_constraints(parsed, param_def)` after parsing
  - [ ] Ensure validation happens before type conversion to strings

**Acceptance Criteria**:
- min_items validation rejects arrays that are too short
- max_items validation rejects arrays that are too long
- unique_items validation rejects arrays with duplicates
- Error messages are clear and actionable
- Validation happens after JSON parsing but before use

---

### 4. Implement Array Item Enum Validation (1.5 hours)

**File**: `src/mddata/templates/filler.py`

#### 4.1 Create Array Item Enum Validator
- [ ] Add new function `_validate_array_item_enum()`:
  ```python
  def _validate_array_item_enum(
      value: list[Any], param_def: ParameterDefinition
  ) -> None:
      """Validate array items against enum constraints."""
      # Implementation here
  ```

- [ ] Extract `item_enum`, `item_enum_strict`, `item_enum_descriptions`
- [ ] Default `item_enum_strict` to `True`
- [ ] Loop through array items with index
- [ ] For each item not in enum:
  - [ ] Build error message with index and allowed values
  - [ ] Include descriptions if available
  - [ ] If strict: raise `ValueError`
  - [ ] If non-strict: issue `warnings.warn()`

#### 4.2 Integrate with Array Parsing
- [ ] Update `_parse_array_param()` function:
  - [ ] Call `_validate_array_item_enum(parsed, param_def)` after array constraints
  - [ ] Ensure validation happens before type conversion

**Acceptance Criteria**:
- Strict item_enum rejects invalid array items with index
- Non-strict item_enum warns but continues
- Error messages show item index: `Array item [1] = 'invalid' not in enum values: [...]`
- Descriptions are shown when available
- All array items are validated

---

### 5. Implement Pattern-Based Array Validation (1.5 hours)

**File**: `src/mddata/templates/filler.py`

#### 5.1 Create Array Item Pattern Validator
- [ ] Add new function `_validate_array_item_pattern()`:
  ```python
  def _validate_array_item_pattern(
      value: list[Any], param_def: ParameterDefinition
  ) -> None:
      """Validate array items against regex pattern."""
      # Implementation here
  ```

- [ ] Extract `item_pattern` from `param_def`
- [ ] Return early if no pattern defined
- [ ] Compile regex pattern: `pattern = re.compile(item_pattern)`
- [ ] Loop through array items with index
- [ ] Skip non-string items (pattern validation only for strings)
- [ ] For each item that doesn't match:
  - [ ] Raise `ValueError` with item index and pattern

#### 5.2 Integrate with Array Parsing
- [ ] Update `_parse_array_param()` function:
  - [ ] Call `_validate_array_item_pattern(parsed, param_def)` after enum validation
  - [ ] Ensure proper ordering: array constraints → item enum → item pattern

#### 5.3 Handle Combined Enum + Pattern
- [ ] Update `_validate_array_item_enum()`:
  - [ ] If `item_enum_strict=False` and item_pattern exists:
    - [ ] Check if item matches pattern before warning/erroring
    - [ ] Only warn/error if item matches neither enum nor pattern

**Acceptance Criteria**:
- Pattern validation rejects items that don't match regex
- Error messages include item index and pattern
- Pattern validation works with email, URL, version patterns
- Combined enum + pattern (non-strict) allows either to pass
- Pattern validation only applies to string items

---

### 6. Update Validation Flow Integration (30 min)

**File**: `src/mddata/templates/filler.py`

- [ ] Review `_parse_cli_params()` function:
  - [ ] Ensure it calls `_validate_param_constraints()` correctly
  - [ ] Verify array parameters flow through `_parse_array_param()`

- [ ] Review `TemplateFiller.fill()` method:
  - [ ] Ensure validation happens during parameter resolution
  - [ ] Verify error messages propagate correctly

**Acceptance Criteria**:
- All validation functions are called in correct order
- Validation errors propagate to user with helpful messages
- Warnings are visible in CLI output

---

### 7. Write Unit Tests (2 hours)

**File**: `tests/unit/mddata/templates/test_parameter_validation.py` (new file)

#### 7.1 Test Enum Validation
- [ ] Test strict enum with valid value (should pass)
- [ ] Test strict enum with invalid value (should raise ValueError)
- [ ] Test strict enum error message includes descriptions
- [ ] Test non-strict enum with invalid value (should warn)
- [ ] Test enum with numeric values (int, float)
- [ ] Test enum with None value
- [ ] Test enum without descriptions

#### 7.2 Test Array Constraints
- [ ] Test min_items validation (too few items should raise)
- [ ] Test max_items validation (too many items should raise)
- [ ] Test unique_items validation (duplicates should raise)
- [ ] Test combined constraints (min + max + unique)
- [ ] Test array within valid range (should pass)

#### 7.3 Test Array Item Enum
- [ ] Test strict item_enum with all valid items (should pass)
- [ ] Test strict item_enum with one invalid item (should raise with index)
- [ ] Test item_enum error message includes descriptions
- [ ] Test non-strict item_enum with invalid item (should warn)
- [ ] Test item_enum with different data types

#### 7.4 Test Array Item Pattern
- [ ] Test item_pattern with valid email addresses (should pass)
- [ ] Test item_pattern with invalid email (should raise with index)
- [ ] Test item_pattern with URL pattern
- [ ] Test item_pattern with version string pattern
- [ ] Test pattern only validates strings (skips other types)

#### 7.5 Test Combined Validations
- [ ] Test enum + pattern (non-strict) - enum match passes
- [ ] Test enum + pattern (non-strict) - pattern match passes
- [ ] Test enum + pattern (non-strict) - neither match fails
- [ ] Test all array validations together

**Test Template**:
```python
import pytest
from mddata.templates.filler import (
    _validate_param_constraints,
    _validate_array_constraints,
    _validate_array_item_enum,
    _validate_array_item_pattern,
)
from mddata.models import ParameterDefinition, ParameterType

def test_strict_enum_valid_value():
    """Test strict enum validation with valid value."""
    param_def: ParameterDefinition = {
        "type": ParameterType.STR,
        "enum": ["draft", "published"],
        "enum_strict": True,
    }
    # Should not raise
    _validate_param_constraints("draft", param_def)

def test_strict_enum_invalid_value():
    """Test strict enum validation with invalid value."""
    param_def: ParameterDefinition = {
        "type": ParameterType.STR,
        "enum": ["draft", "published"],
        "enum_strict": True,
    }
    with pytest.raises(ValueError, match="not in enum values"):
        _validate_param_constraints("invalid", param_def)
```

**Acceptance Criteria**:
- All tests pass
- Test coverage > 90% for new validation functions
- Tests cover happy path and error cases
- Tests verify error message content
- Tests verify warning behavior

---

### 8. Integration Testing (1 hour)

**File**: `tests/integration/test_template_validation.py` (new file)

- [ ] Test complete template fill workflow with enum parameters
- [ ] Test template fill with array constraints
- [ ] Test template fill with item_enum validation
- [ ] Test template fill with item_pattern validation
- [ ] Test CLI integration (use subprocess to test mddata write command)
- [ ] Test error messages in real template usage

**Example Integration Test**:
```python
from mddata import MarkdownDataUpdate
from mddata.templates import TemplateFiller

def test_complete_template_with_enums():
    """Test complete template workflow with enum validation."""
    template = MarkdownDataUpdate(
        parameters={
            "status": {
                "type": ParameterType.STR,
                "enum": ["draft", "published"],
                "enum_descriptions": {
                    "draft": "Work in progress",
                    "published": "Live content",
                },
                "enum_strict": True,
                "required": True,
            }
        },
        frontmatter={"status": "{status}"},
    )

    filler = TemplateFiller(template)

    # Valid fill
    filled = filler.fill(cli_params=["status=draft"])
    assert filled.frontmatter["status"] == "draft"

    # Invalid fill
    with pytest.raises(ValueError, match="not in enum values"):
        filler.fill(cli_params=["status=invalid"])
```

**Acceptance Criteria**:
- End-to-end workflows work correctly
- CLI commands produce expected output
- Error messages are user-friendly
- Warnings are visible in output

---

### 9. Documentation Updates (30 min)

#### 9.1 Update Code Documentation
**File**: `src/mddata/templates/filler.py`
- [ ] Update module docstring to mention new validation features
- [ ] Add docstrings to all new validation functions
- [ ] Add inline comments for complex validation logic

#### 9.2 Update User Documentation
**File**: `docs/CLI_REFERENCE.md` (if it exists)
- [ ] Add section on enum parameters
- [ ] Add section on array constraints
- [ ] Add examples of enum_strict usage
- [ ] Add examples of pattern validation

**File**: `CLAUDE.md`
- [ ] Add note about parameter validation capabilities
- [ ] Reference PARAMETER_VALIDATION_IMPROVEMENTS.md

**Acceptance Criteria**:
- All new functions have clear docstrings
- User documentation includes practical examples
- Code comments explain non-obvious logic

---

### 10. Manual Testing & Validation (30 min)

- [ ] Create test template with all new features:
  - [ ] Enum with descriptions
  - [ ] Non-strict enum
  - [ ] Array constraints
  - [ ] Item enum (strict and non-strict)
  - [ ] Item pattern

- [ ] Test with mddata CLI:
  ```bash
  # Create test template
  mddata write --data test_template.yaml -p status=draft -o test.md

  # Test strict enum error
  mddata write --data test_template.yaml -p status=invalid -o test.md

  # Test non-strict enum warning
  mddata write --data test_template.yaml -p category=custom -o test.md

  # Test array constraints
  mddata write --data test_template.yaml -p tags='["a", "b"]' -o test.md

  # Test item pattern
  mddata write --data test_template.yaml -p emails='["test@example.com"]' -o test.md
  ```

- [ ] Verify error messages are helpful and clear
- [ ] Verify warnings appear in output
- [ ] Test edge cases (empty arrays, null values, etc.)

**Acceptance Criteria**:
- Manual tests pass for all features
- Error messages guide user to fix issues
- Warnings are visible but don't block execution
- Edge cases are handled gracefully

---

## Definition of Done

- [x] All code changes implemented and working
- [x] All unit tests written and passing
- [x] Integration tests written and passing
- [x] Code documentation updated
- [x] User documentation updated
- [x] Manual testing completed successfully
- [x] Code passes linting (`python src/dev/lint_command.py`)
- [x] Type checking passes (`uv run pyright`)
- [x] All tests pass (`uv run pytest`)
- [ ] Changes committed with clear commit message
- [ ] PARAMETER_VALIDATION_IMPROVEMENTS.md status updated to "Phase 1 Complete"

---

## Files to Modify

- [ ] `src/mddata/models/contracts.py` - Add new fields to ParameterDefinition
- [ ] `src/mddata/templates/filler.py` - Implement all validation functions
- [ ] `tests/unit/mddata/templates/test_parameter_validation.py` - New unit tests
- [ ] `tests/integration/test_template_validation.py` - New integration tests
- [ ] `docs/CLI_REFERENCE.md` - Update documentation (if exists)
- [ ] `CLAUDE.md` - Add reference to new capabilities

---

## Progress Tracking

**Status**: ✅ Completed

- [x] Task 1: Update Data Models
- [x] Task 2: Implement Enum Validation
- [x] Task 3: Implement Array Constraints
- [x] Task 4: Implement Array Item Enum Validation
- [x] Task 5: Implement Pattern-Based Array Validation
- [x] Task 6: Update Validation Flow Integration
- [x] Task 7: Write Unit Tests
- [x] Task 8: Integration Testing
- [x] Task 9: Documentation Updates
- [x] Task 10: Manual Testing & Validation

---

## Notes

- Start with data models, then validation functions, then tests
- Test each feature individually before combining
- Pay attention to error message quality - they're user-facing
- Consider backward compatibility (all new fields are optional)
- Reference `src/mddata/schema/schema_property_validator.py` for similar patterns

---

## Related Issues

- See: `PARAMETER_VALIDATION_IMPROVEMENTS.md` for full design specification
- Phase 2 tasks (custom validation messages) will be in a separate TODO

---

**Started**: 2025-10-26
**Completed**: 2025-10-26
**Duration**: ~4 hours
