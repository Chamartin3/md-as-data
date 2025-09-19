"""Placeholder substitution engine for templates."""

import re
from typing import Any

from .models import ResolvedParameters

# Compiled regex patterns for performance
PLACEHOLDER_PATTERN = re.compile(r"(?<!\\)\{([a-zA-Z_][a-zA-Z0-9_\.]*)\}")
ESCAPE_PATTERN = re.compile(r"\\(\{)")


def substitute_placeholders(content: str, params: ResolvedParameters) -> str:
    """Replace all placeholders with parameter values."""
    if not isinstance(content, str):
        return content

    def replace_placeholder(match):
        param_name = match.group(1)
        if param_name not in params:
            raise ValueError(f"Unknown placeholder: {{{param_name}}}")
        value = params[param_name]
        return format_value(value)

    # First substitute placeholders
    result = PLACEHOLDER_PATTERN.sub(replace_placeholder, content)

    # Then unescape literal braces
    result = unescape_literal_braces(result)

    return result


def substitute_in_dict(
    data: dict[str, Any], params: ResolvedParameters
) -> dict[str, Any]:
    """Recursively substitute placeholders in dictionary."""
    result = {}
    for key, value in data.items():
        if isinstance(value, str):
            result[key] = substitute_placeholders(value, params)
        elif isinstance(value, dict):
            result[key] = substitute_in_dict(value, params)
        elif isinstance(value, list):
            result[key] = substitute_in_list(value, params)
        else:
            result[key] = value
    return result


def substitute_in_list(items: list[Any], params: ResolvedParameters) -> list[Any]:
    """Recursively substitute placeholders in list."""
    result = []
    for item in items:
        if isinstance(item, str):
            result.append(substitute_placeholders(item, params))
        elif isinstance(item, dict):
            result.append(substitute_in_dict(item, params))
        elif isinstance(item, list):
            result.append(substitute_in_list(item, params))
        else:
            result.append(item)
    return result


def find_placeholders(content: str) -> set[str]:
    """Extract all placeholder names from content."""
    if not isinstance(content, str):
        return set()

    matches = PLACEHOLDER_PATTERN.findall(content)
    return set(matches)


def validate_placeholders(content: str, available_params: set[str]) -> None:
    """Validate all placeholders are available, raise on unknown."""
    placeholders = find_placeholders(content)
    unknown = placeholders - available_params
    if unknown:
        unknown_list = sorted(unknown)
        raise ValueError(
            f"Unknown placeholders: {', '.join(f'{{{p}}}' for p in unknown_list)}"
        )


def format_value(value: Any) -> str:
    """Format a parameter value for string substitution."""
    if isinstance(value, list):
        return format_array_value(value)
    elif isinstance(value, bool):
        return str(value).lower()
    elif value is None:
        return ""
    else:
        return str(value)


def format_array_value(value: list[Any]) -> str:
    """Format array value for markdown substitution."""
    return ", ".join(str(item) for item in value)


def unescape_literal_braces(content: str) -> str:
    """Convert \\{ to { for literal brace output."""
    return ESCAPE_PATTERN.sub(r"\1", content)
