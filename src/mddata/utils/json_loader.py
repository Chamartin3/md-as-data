"""JSON data loading and validation utilities for MarkdownDataDict."""

import json
import sys
from pathlib import Path

from ..models import MarkdownDataDict


class JSONDataError(Exception):
    """Exception for JSON data loading and validation errors.

    This single exception type covers all JSON loading scenarios:
    - File not found
    - Malformed JSON
    - Invalid structure for MarkdownDataDict

    The error message provides context about what went wrong.
    """

    pass


def load_json(source: str) -> dict:
    """Load JSON from file path or stdin.

    Args:
        source: File path or '-' for stdin

    Returns:
        Loaded JSON data as dictionary

    Raises:
        JSONDataError: If file doesn't exist or JSON is malformed
    """
    try:
        if source == "-":
            # Read from stdin
            return json.load(sys.stdin)
        else:
            # Read from file
            file_path = Path(source)
            if not file_path.exists():
                raise JSONDataError(f"JSON file not found: {source}")

            with open(file_path) as f:
                return json.load(f)

    except json.JSONDecodeError as e:
        source_name = "stdin" if source == "-" else f"file '{source}'"
        raise JSONDataError(f"Invalid JSON from {source_name}: {e}") from e


def validate_markdown_data_dict(data: dict) -> None:
    """Validate that data conforms to MarkdownDataDict structure.

    Args:
        data: Dictionary to validate

    Raises:
        JSONDataError: If structure is invalid
    """
    # Check if data is a dictionary
    if not isinstance(data, dict):
        raise JSONDataError(
            f"JSON data must be an object/dictionary, got {type(data).__name__}"
        )

    # Check for frontmatter field
    if "frontmatter" not in data:
        raise JSONDataError(
            "JSON data must contain 'frontmatter' field (MarkdownDataDict format)"
        )

    # Check for content field
    if "content" not in data:
        raise JSONDataError(
            "JSON data must contain 'content' field (MarkdownDataDict format)"
        )

    # Validate content structure (must be SectionData)
    content = data["content"]
    if not isinstance(content, dict):
        raise JSONDataError(
            "'content' field must be a dictionary (SectionData format), "
            f"got {type(content).__name__}"
        )

    # Root section requires id, title, level (path is optional for root)
    required_fields = ["id", "title", "level"]
    missing_fields = [f for f in required_fields if f not in content]
    if missing_fields:
        raise JSONDataError(
            f"'content' field missing required fields: {', '.join(missing_fields)}. "
            f"Expected SectionData format with at least: {', '.join(required_fields)}"
        )


def load_markdown_data_dict(source: str) -> MarkdownDataDict:
    """Load and validate MarkdownDataDict from JSON file or stdin.

    This is the main entrypoint for loading JSON data into MarkdownDataDict format.
    Combines loading and validation into a single operation.

    Args:
        source: File path or '-' for stdin

    Returns:
        Validated MarkdownDataDict

    Raises:
        JSONDataError: If file doesn't exist, JSON is malformed, or structure is invalid

    Example:
        >>> data = load_markdown_data_dict('document.json')
        >>> data = load_markdown_data_dict('-')  # from stdin
    """
    # Load JSON
    json_data = load_json(source)

    # Validate structure
    validate_markdown_data_dict(json_data)

    return json_data  # type: ignore
