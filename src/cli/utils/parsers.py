"""Input parsing utilities for CLI commands."""

import json
from pathlib import Path
from typing import Any, TypedDict


class ParseResult(TypedDict):
    """Result of value parsing."""

    success: bool
    value: Any
    error: str | None
    parsed_as: str  # 'json', 'string', 'number', 'boolean'


class InputParser:
    """Parser for CLI string input with type inference."""

    @staticmethod
    def parse_frontmatter_value(
        value: str, force_json: bool = False, allow_fallback: bool = True
    ) -> ParseResult:
        """Parse frontmatter value with optional JSON parsing.

        Args:
            value: String value to parse
            force_json: If True, value must be valid JSON
            allow_fallback: If True, fall back to string on JSON parse error

        Returns:
            ParseResult with parsed value and metadata
        """
        # Try JSON parsing first
        try:
            parsed = json.loads(value)
            return ParseResult(success=True, value=parsed, error=None, parsed_as="json")
        except json.JSONDecodeError as e:
            # JSON parsing failed
            if force_json:
                return ParseResult(
                    success=False,
                    value=None,
                    error=f"Invalid JSON value: {e}",
                    parsed_as="error",
                )
            elif allow_fallback:
                # Fall back to string
                return ParseResult(
                    success=True, value=value, error=None, parsed_as="string"
                )
            else:
                return ParseResult(
                    success=False,
                    value=None,
                    error=f"Failed to parse value: {e}",
                    parsed_as="error",
                )

    @staticmethod
    def parse_value_auto(value: str) -> Any:
        """Automatically parse value with smart type inference.

        Tries to parse as JSON first, falls back to string.

        Args:
            value: String value to parse

        Returns:
            Parsed value (may be string, number, bool, list, dict)
        """
        result = InputParser.parse_frontmatter_value(
            value, force_json=False, allow_fallback=True
        )
        return result["value"]

    @staticmethod
    def parse_value_strict(value: str) -> Any:
        """Parse value as JSON with no fallback.

        Args:
            value: String value to parse as JSON

        Returns:
            Parsed JSON value

        Raises:
            ValueError: If value is not valid JSON
        """
        result = InputParser.parse_frontmatter_value(
            value, force_json=True, allow_fallback=False
        )
        if not result["success"]:
            raise ValueError(result["error"])
        return result["value"]


def parse_cli_params(param_list: list[str]) -> dict[str, Any]:
    """Parse CLI parameters in KEY=VALUE or KEY=@file format.

    Args:
        param_list: List of parameter strings

    Returns:
        Dictionary of parsed parameters

    Raises:
        ValueError: If parameter format is invalid
    """
    params = {}
    for param in param_list:
        if "=" not in param:
            raise ValueError(f"Invalid parameter format: {param}. Expected KEY=VALUE")

        key, value = param.split("=", 1)

        # Handle file parameter values (@file)
        if value.startswith("@"):
            file_path = Path(value[1:])
            if not file_path.exists():
                raise ValueError(f"Parameter file not found: {file_path}")
            value = file_path.read_text().strip()

        params[key] = value

    return params
