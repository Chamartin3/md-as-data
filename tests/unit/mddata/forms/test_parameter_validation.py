"""Unit tests for parameter validation enhancements."""

import pytest
from mddata.forms.filler import (
    _validate_param_constraints,
    _validate_array_constraints,
    _validate_array_item_enum,
    _validate_array_item_pattern,
)
from mddata.models import ParameterDefinition, ParameterType


# =============================================================================
# Enum Validation Tests
# =============================================================================


def test_strict_enum_valid_value():
    """Test strict enum validation with valid value."""
    param_def: ParameterDefinition = {
        "type": ParameterType.STR,
        "enum": ["draft", "published"],
        "enum_strict": True,
    }
    # Should not raise
    _validate_param_constraints("test_param", "draft", param_def)


def test_strict_enum_invalid_value():
    """Test strict enum validation with invalid value."""
    param_def: ParameterDefinition = {
        "type": ParameterType.STR,
        "enum": ["draft", "published"],
        "enum_strict": True,
    }
    with pytest.raises(ValueError, match="not in enum values"):
        _validate_param_constraints("test_param", "invalid", param_def)


def test_strict_enum_error_message_with_descriptions():
    """Test strict enum validation error message includes descriptions."""
    param_def: ParameterDefinition = {
        "type": ParameterType.STR,
        "enum": ["draft", "published"],
        "enum_descriptions": {
            "draft": "Work in progress",
            "published": "Live content",
        },
        "enum_strict": True,
    }
    with pytest.raises(ValueError) as exc_info:
        _validate_param_constraints("test_param", "invalid", param_def)

    error_msg = str(exc_info.value)
    assert "not in enum values" in error_msg
    assert "Work in progress" in error_msg
    assert "Live content" in error_msg


def test_non_strict_enum_invalid_value():
    """Test non-strict enum validation with invalid value."""
    param_def: ParameterDefinition = {
        "type": ParameterType.STR,
        "enum": ["draft", "published"],
        "enum_strict": False,
    }
    with pytest.warns(UserWarning, match="Parameter validation warning"):
        _validate_param_constraints("test_param", "invalid", param_def)


def test_enum_with_numeric_values():
    """Test enum validation with numeric values."""
    param_def: ParameterDefinition = {
        "type": ParameterType.INT,
        "enum": [1, 2, 3],
        "enum_strict": True,
    }
    # Should not raise
    _validate_param_constraints("test_param", 2, param_def)

    with pytest.raises(ValueError, match="not in enum values"):
        _validate_param_constraints("test_param", 4, param_def)


def test_enum_with_none_value():
    """Test enum validation with None value."""
    param_def: ParameterDefinition = {
        "type": ParameterType.STR,
        "enum": ["value1", None],
        "enum_strict": True,
    }
    # Should not raise
    _validate_param_constraints("test_param", None, param_def)


def test_enum_without_descriptions():
    """Test enum validation without descriptions."""
    param_def: ParameterDefinition = {
        "type": ParameterType.STR,
        "enum": ["a", "b", "c"],
        "enum_strict": True,
    }
    with pytest.raises(ValueError) as exc_info:
        _validate_param_constraints("test_param", "d", param_def)

    error_msg = str(exc_info.value)
    assert "not in enum values" in error_msg
    assert "[a, b, c]" in error_msg


# =============================================================================
# Array Constraints Tests
# =============================================================================


def test_min_items_validation_too_few():
    """Test min_items validation rejects arrays that are too short."""
    param_def: ParameterDefinition = {
        "type": ParameterType.ARRAY,
        "min_items": 3,
    }
    with pytest.raises(ValueError, match="must have at least 3 items"):
        _validate_array_constraints([1, 2], param_def)


def test_max_items_validation_too_many():
    """Test max_items validation rejects arrays that are too long."""
    param_def: ParameterDefinition = {
        "type": ParameterType.ARRAY,
        "max_items": 2,
    }
    with pytest.raises(ValueError, match="must have at most 2 items"):
        _validate_array_constraints([1, 2, 3], param_def)


def test_unique_items_validation_duplicates():
    """Test unique_items validation rejects arrays with duplicates."""
    param_def: ParameterDefinition = {
        "type": ParameterType.ARRAY,
        "unique_items": True,
    }
    with pytest.raises(ValueError, match="must be unique"):
        _validate_array_constraints([1, 2, 2, 3], param_def)


def test_combined_array_constraints():
    """Test combined min_items, max_items, and unique_items constraints."""
    param_def: ParameterDefinition = {
        "type": ParameterType.ARRAY,
        "min_items": 2,
        "max_items": 4,
        "unique_items": True,
    }
    # Should not raise - valid array
    _validate_array_constraints([1, 2, 3], param_def)

    # Should raise - too few items
    with pytest.raises(ValueError, match="at least 2 items"):
        _validate_array_constraints([1], param_def)

    # Should raise - too many items
    with pytest.raises(ValueError, match="at most 4 items"):
        _validate_array_constraints([1, 2, 3, 4, 5], param_def)

    # Should raise - duplicates
    with pytest.raises(ValueError, match="must be unique"):
        _validate_array_constraints([1, 2, 2], param_def)


def test_array_within_valid_range():
    """Test array within valid range passes all constraints."""
    param_def: ParameterDefinition = {
        "type": ParameterType.ARRAY,
        "min_items": 1,
        "max_items": 5,
        "unique_items": True,
    }
    # Should not raise
    _validate_array_constraints([1, 2, 3], param_def)


# =============================================================================
# Array Item Enum Tests
# =============================================================================


def test_strict_item_enum_all_valid():
    """Test strict item_enum with all valid items."""
    param_def: ParameterDefinition = {
        "type": ParameterType.ARRAY,
        "item_enum": ["a", "b", "c"],
        "item_enum_strict": True,
    }
    # Should not raise
    _validate_array_item_enum(["a", "b"], param_def)


def test_strict_item_enum_invalid_item():
    """Test strict item_enum with one invalid item."""
    param_def: ParameterDefinition = {
        "type": ParameterType.ARRAY,
        "item_enum": ["a", "b", "c"],
        "item_enum_strict": True,
    }
    with pytest.raises(ValueError, match=r"Array item \[1\] = 'd' not in enum values"):
        _validate_array_item_enum(["a", "d"], param_def)


def test_item_enum_error_message_with_descriptions():
    """Test item_enum error message includes descriptions."""
    param_def: ParameterDefinition = {
        "type": ParameterType.ARRAY,
        "item_enum": ["draft", "published"],
        "item_enum_descriptions": {
            "draft": "Work in progress",
            "published": "Live content",
        },
        "item_enum_strict": True,
    }
    with pytest.raises(ValueError) as exc_info:
        _validate_array_item_enum(["invalid"], param_def)

    error_msg = str(exc_info.value)
    assert "not in enum values" in error_msg
    assert "Work in progress" in error_msg
    assert "Live content" in error_msg


def test_non_strict_item_enum_invalid_item():
    """Test non-strict item_enum with invalid item."""
    param_def: ParameterDefinition = {
        "type": ParameterType.ARRAY,
        "item_enum": ["a", "b", "c"],
        "item_enum_strict": False,
    }
    with pytest.warns(UserWarning, match="Parameter validation warning"):
        _validate_array_item_enum(["a", "d"], param_def)


def test_item_enum_with_different_data_types():
    """Test item_enum with different data types."""
    param_def: ParameterDefinition = {
        "type": ParameterType.ARRAY,
        "item_enum": [1, "string", True, None],
        "item_enum_strict": True,
    }
    # Should not raise
    _validate_array_item_enum([1, "string", True, None], param_def)

    with pytest.raises(ValueError, match="not in enum values"):
        _validate_array_item_enum([1, "invalid"], param_def)


# =============================================================================
# Array Item Pattern Tests
# =============================================================================


def test_item_pattern_valid_email_addresses():
    """Test item_pattern with valid email addresses."""
    param_def: ParameterDefinition = {
        "type": ParameterType.ARRAY,
        "item_pattern": r"^[^@]+@[^@]+\.[^@]+$",
    }
    # Should not raise
    _validate_array_item_pattern(["test@example.com", "user@domain.org"], param_def)


def test_item_pattern_invalid_email():
    """Test item_pattern with invalid email."""
    param_def: ParameterDefinition = {
        "type": ParameterType.ARRAY,
        "item_pattern": r"^[^@]+@[^@]+\.[^@]+$",
    }
    with pytest.raises(ValueError, match=r"Array item \[1\] = 'invalid-email' does not match pattern"):
        _validate_array_item_pattern(["test@example.com", "invalid-email"], param_def)


def test_item_pattern_url():
    """Test item_pattern with URL pattern."""
    param_def: ParameterDefinition = {
        "type": ParameterType.ARRAY,
        "item_pattern": r"^https?://",
    }
    # Should not raise
    _validate_array_item_pattern(["https://example.com", "http://test.org"], param_def)

    with pytest.raises(ValueError, match="does not match pattern"):
        _validate_array_item_pattern(["https://example.com", "ftp://invalid.com"], param_def)


def test_item_pattern_version_string():
    """Test item_pattern with version string pattern."""
    param_def: ParameterDefinition = {
        "type": ParameterType.ARRAY,
        "item_pattern": r"^\d+\.\d+\.\d+$",
    }
    # Should not raise
    _validate_array_item_pattern(["1.0.0", "2.1.3"], param_def)

    with pytest.raises(ValueError, match="does not match pattern"):
        _validate_array_item_pattern(["1.0.0", "invalid-version"], param_def)


def test_item_pattern_only_validates_strings():
    """Test pattern validation only applies to string items."""
    param_def: ParameterDefinition = {
        "type": ParameterType.ARRAY,
        "item_pattern": r"^\d+$",
    }
    # Should not raise - non-string items are skipped
    _validate_array_item_pattern(["123", 456, True], param_def)

    # Should raise - string item doesn't match
    with pytest.raises(ValueError, match="does not match pattern"):
        _validate_array_item_pattern(["123", "abc"], param_def)


# =============================================================================
# Combined Validations Tests
# =============================================================================


def test_enum_and_pattern_non_strict_enum_match():
    """Test enum + pattern (non-strict) - enum match passes."""
    param_def: ParameterDefinition = {
        "type": ParameterType.ARRAY,
        "item_enum": ["allowed"],
        "item_enum_strict": False,
        "item_pattern": r"^\d+$",
    }
    # Should not raise - item in enum
    _validate_array_item_enum(["allowed"], param_def)


def test_enum_and_pattern_non_strict_pattern_match():
    """Test enum + pattern (non-strict) - pattern match passes."""
    param_def: ParameterDefinition = {
        "type": ParameterType.ARRAY,
        "item_enum": ["allowed"],
        "item_enum_strict": False,
        "item_pattern": r"^\d+$",
    }
    # Should not warn - item matches pattern
    _validate_array_item_enum(["123"], param_def)


def test_enum_and_pattern_non_strict_neither_match():
    """Test enum + pattern (non-strict) - neither match fails."""
    param_def: ParameterDefinition = {
        "type": ParameterType.ARRAY,
        "item_enum": ["allowed"],
        "item_enum_strict": False,
        "item_pattern": r"^\d+$",
    }
    # Should warn - item matches neither enum nor pattern
    with pytest.warns(UserWarning):
        _validate_array_item_enum(["invalid"], param_def)


def test_all_array_validations_together():
    """Test all array validations together."""
    param_def: ParameterDefinition = {
        "type": ParameterType.ARRAY,
        "min_items": 2,
        "max_items": 4,
        "unique_items": True,
        "item_enum": ["a", "b", "c"],
        "item_enum_strict": True,
        "item_pattern": r"^[a-c]$",
    }

    # Should not raise - valid array
    _validate_array_constraints(["a", "b"], param_def)
    _validate_array_item_enum(["a", "b"], param_def)
    _validate_array_item_pattern(["a", "b"], param_def)

    # Should raise - invalid item
    with pytest.raises(ValueError, match="not in enum values"):
        _validate_array_item_enum(["a", "d"], param_def)