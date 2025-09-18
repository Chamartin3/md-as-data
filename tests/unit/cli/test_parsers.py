"""Unit tests for CLI input parser utilities."""

import pytest

from cli.utils.parsers import InputParser, ParseResult


class TestParseValueAuto:
    """Test InputParser.parse_value_auto method."""

    def test_parse_value_auto_json_object(self) -> None:
        """Should parse valid JSON object."""
        result = InputParser.parse_value_auto('{"key": "value"}')
        assert result == {"key": "value"}

    def test_parse_value_auto_json_array(self) -> None:
        """Should parse valid JSON array."""
        result = InputParser.parse_value_auto('["a", "b", "c"]')
        assert result == ["a", "b", "c"]

    def test_parse_value_auto_json_number(self) -> None:
        """Should parse JSON number."""
        result = InputParser.parse_value_auto("42")
        assert result == 42
        assert isinstance(result, int)

    def test_parse_value_auto_json_float(self) -> None:
        """Should parse JSON float."""
        result = InputParser.parse_value_auto("3.14")
        assert result == 3.14
        assert isinstance(result, float)

    def test_parse_value_auto_json_boolean_true(self) -> None:
        """Should parse JSON boolean true."""
        result = InputParser.parse_value_auto("true")
        assert result is True

    def test_parse_value_auto_json_boolean_false(self) -> None:
        """Should parse JSON boolean false."""
        result = InputParser.parse_value_auto("false")
        assert result is False

    def test_parse_value_auto_json_null(self) -> None:
        """Should parse JSON null."""
        result = InputParser.parse_value_auto("null")
        assert result is None

    def test_parse_value_auto_fallback_to_string(self) -> None:
        """Should fall back to string when JSON parsing fails."""
        result = InputParser.parse_value_auto("not-json-value")
        assert result == "not-json-value"
        assert isinstance(result, str)

    def test_parse_value_auto_fallback_complex_string(self) -> None:
        """Should fall back to string for complex non-JSON strings."""
        value = "This is a sentence with spaces and punctuation!"
        result = InputParser.parse_value_auto(value)
        assert result == value
        assert isinstance(result, str)


class TestParseValueStrict:
    """Test InputParser.parse_value_strict method."""

    def test_parse_value_strict_valid_json_object(self) -> None:
        """Should parse valid JSON object in strict mode."""
        result = InputParser.parse_value_strict('{"name": "test"}')
        assert result == {"name": "test"}

    def test_parse_value_strict_valid_json_array(self) -> None:
        """Should parse valid JSON array in strict mode."""
        result = InputParser.parse_value_strict("[1, 2, 3]")
        assert result == [1, 2, 3]

    def test_parse_value_strict_valid_json_string(self) -> None:
        """Should parse valid JSON string in strict mode."""
        result = InputParser.parse_value_strict('"hello"')
        assert result == "hello"

    def test_parse_value_strict_invalid_json_raises(self) -> None:
        """Should raise ValueError for invalid JSON in strict mode."""
        with pytest.raises(ValueError, match="Invalid JSON value"):
            InputParser.parse_value_strict("not-valid-json")

    def test_parse_value_strict_partial_json_raises(self) -> None:
        """Should raise ValueError for partial JSON in strict mode."""
        with pytest.raises(ValueError, match="Invalid JSON value"):
            InputParser.parse_value_strict('{"incomplete": ')


class TestParseFrontmatterValue:
    """Test InputParser.parse_frontmatter_value method with different modes."""

    def test_parse_frontmatter_value_default_json_success(self) -> None:
        """Should parse valid JSON with default settings."""
        result = InputParser.parse_frontmatter_value('{"key": "value"}')

        assert result["success"] is True
        assert result["value"] == {"key": "value"}
        assert result["error"] is None
        assert result["parsed_as"] == "json"

    def test_parse_frontmatter_value_default_fallback(self) -> None:
        """Should fall back to string with default settings."""
        result = InputParser.parse_frontmatter_value("plain-string")

        assert result["success"] is True
        assert result["value"] == "plain-string"
        assert result["error"] is None
        assert result["parsed_as"] == "string"

    def test_parse_frontmatter_value_force_json_success(self) -> None:
        """Should parse valid JSON with force_json=True."""
        result = InputParser.parse_frontmatter_value('["a", "b"]', force_json=True)

        assert result["success"] is True
        assert result["value"] == ["a", "b"]
        assert result["error"] is None
        assert result["parsed_as"] == "json"

    def test_parse_frontmatter_value_force_json_failure(self) -> None:
        """Should return error with force_json=True and invalid JSON."""
        result = InputParser.parse_frontmatter_value("invalid", force_json=True)

        assert result["success"] is False
        assert result["value"] is None
        assert result["error"] is not None
        assert "Invalid JSON value" in result["error"]
        assert result["parsed_as"] == "error"

    def test_parse_frontmatter_value_no_fallback_failure(self) -> None:
        """Should return error with allow_fallback=False and invalid JSON."""
        result = InputParser.parse_frontmatter_value("invalid", allow_fallback=False)

        assert result["success"] is False
        assert result["value"] is None
        assert result["error"] is not None
        assert "Failed to parse value" in result["error"]
        assert result["parsed_as"] == "error"

    def test_parse_frontmatter_value_complex_json(self) -> None:
        """Should parse complex nested JSON structures."""
        json_str = '{"nested": {"array": [1, 2, 3], "bool": true}}'
        result = InputParser.parse_frontmatter_value(json_str)

        assert result["success"] is True
        assert result["value"] == {"nested": {"array": [1, 2, 3], "bool": True}}
        assert result["parsed_as"] == "json"


class TestEdgeCases:
    """Test edge cases and special values."""

    def test_parse_empty_string_fallback(self) -> None:
        """Should handle empty string."""
        result = InputParser.parse_value_auto("")
        assert result == ""
        assert isinstance(result, str)

    def test_parse_whitespace_string(self) -> None:
        """Should handle whitespace-only string."""
        result = InputParser.parse_value_auto("   ")
        assert result == "   "

    def test_parse_numeric_string_with_leading_zeros(self) -> None:
        """Should handle numeric strings with leading zeros."""
        result = InputParser.parse_value_auto("007")
        # JSON doesn't allow leading zeros, so this falls back to string
        assert result == "007"
        assert isinstance(result, str)

    def test_parse_quoted_string_as_json(self) -> None:
        """Should parse quoted strings as JSON strings."""
        result = InputParser.parse_value_auto('"quoted string"')
        assert result == "quoted string"

    def test_parse_special_json_values(self) -> None:
        """Should handle special JSON values."""
        assert InputParser.parse_value_auto("null") is None
        assert InputParser.parse_value_auto("true") is True
        assert InputParser.parse_value_auto("false") is False

    def test_parse_negative_numbers(self) -> None:
        """Should parse negative numbers."""
        result = InputParser.parse_value_auto("-42")
        assert result == -42

    def test_parse_scientific_notation(self) -> None:
        """Should parse scientific notation."""
        result = InputParser.parse_value_auto("1.5e10")
        assert result == 1.5e10
