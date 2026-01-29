"""Unified data loader for markdown modifications from multiple formats.

This module provides a single interface for loading MarkdownDataUpdate structures
from JSON, YAML, and template files with optional parameter substitution.
"""

import json
import sys
from enum import Enum
from pathlib import Path

import yaml

from mddata.models import MarkdownDataDict, MarkdownDataUpdate
from mddata.templates.filler import TemplateFiller


class DataLoadError(Exception):
    """Exception for data loading errors.

    Covers:
    - File not found
    - Malformed JSON/YAML
    - Invalid structure
    - Template parameter errors
    - Data validation errors
    """

    pass


class DataFormat(str, Enum):
    """Supported data formats for loading markdown updates."""

    JSON = "json"
    YAML = "yaml"


def detect_format(path: str) -> DataFormat:
    """Detect format based on file extension.

    Args:
        path: File path to detect format from

    Returns:
        Detected DataFormat enum value

    Raises:
        DataLoadError: If extension is unsupported
    """
    suffix = Path(path).suffix.lower()
    if suffix == ".json":
        return DataFormat.JSON
    elif suffix in (".yaml", ".yml"):
        return DataFormat.YAML
    else:
        raise DataLoadError(
            f"Unsupported file extension '{suffix}'. Use .json, .yaml, or .yml"
        )


def _load_raw_data(source: str, format: DataFormat | None = None) -> dict:
    """Load raw data from file or stdin with automatic format detection.

    Args:
        source: File path or '-' for stdin
        format: Data format (optional, auto-detected from file extension)

    Returns:
        Loaded data as dictionary

    Raises:
        DataLoadError: If loading or parsing fails
    """
    try:
        # Determine format
        if source == "-":
            # Stdin - must specify format explicitly
            if format is None:
                raise DataLoadError(
                    "Format must be specified when reading from stdin "
                    "(use DataFormat.JSON or DataFormat.YAML)"
                )
            detected_format = format
            content = sys.stdin.read()
        else:
            # File - auto-detect from extension or use provided format
            file_path = Path(source)
            if not file_path.exists():
                raise DataLoadError(f"File not found: {source}")

            detected_format = detect_format(source) if format is None else format
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

        # Parse based on format
        if detected_format == DataFormat.JSON:
            data = json.loads(content)
        else:  # DataFormat.YAML
            data = yaml.safe_load(content)

        if not isinstance(data, dict):
            raise DataLoadError(f"Data must be a dictionary, got {type(data).__name__}")

        return data

    except json.JSONDecodeError as e:
        source_name = "stdin" if source == "-" else f"file '{source}'"
        raise DataLoadError(f"Invalid JSON from {source_name}: {e}") from e
    except yaml.YAMLError as e:
        source_name = "stdin" if source == "-" else f"file '{source}'"
        raise DataLoadError(f"Invalid YAML from {source_name}: {e}") from e


def load_data_update(
    source: str,
    format: DataFormat | None = None,
    cli_params: list[str] | None = None,
    params_file: str | None = None,
) -> MarkdownDataUpdate:
    """Load MarkdownDataUpdate from any supported format.

    This unified loader handles:
    - JSON files with batch changes (from-json style)
    - YAML template files with parameters (from-template style)
    - Stdin input in either format
    - Template parameter substitution when applicable
    - Automatic format detection from file extensions

    Args:
        source: File path or '-' for stdin
        format: Data format (optional, auto-detected from file extension)
        cli_params: Template parameters in KEY=VALUE format (optional)
        params_file: JSON/YAML file with parameter definitions (optional)

    Returns:
        MarkdownDataUpdate instance ready for application

    Raises:
        DataLoadError: If loading, parsing, or validation fails

    Examples:
        # Load JSON batch changes (auto-detected)
        update = load_data_update('changes.json')

        # Load YAML template with parameters (auto-detected)
        update = load_data_update(
            'template.yaml',
            cli_params=['title=My Doc', 'author=John']
        )

        # Load from stdin with explicit format
        update = load_data_update('-', format=DataFormat.JSON)

        # Override auto-detection with explicit format
        update = load_data_update('data.txt', format=DataFormat.YAML)
    """
    try:
        # Load raw data
        data = _load_raw_data(source, format)

        # Create MarkdownDataUpdate - validates structure
        try:
            update = MarkdownDataUpdate.from_dict(data)
        except ValueError as e:
            raise DataLoadError(f"Data validation failed: {e}") from e

        # If template (has parameters), fill with provided values
        # Check for parameters dict presence (even if empty) to handle computed params
        if update.parameters is not None:
            filler = TemplateFiller(update)
            update = filler.fill(cli_params=cli_params or [], params_file=params_file)

        return update

    except DataLoadError:
        raise
    except Exception as e:
        source_name = "stdin" if source == "-" else source
        raise DataLoadError(f"Failed to load data from {source_name}: {e}") from e


def validate_markdown_data_dict(data: dict) -> None:
    """Validate that data conforms to MarkdownDataDict structure.

    Args:
        data: Dictionary to validate

    Raises:
        DataLoadError: If structure is invalid
    """
    # Check if data is a dictionary
    if not isinstance(data, dict):
        raise DataLoadError(
            f"Data must be an object/dictionary, got {type(data).__name__}"
        )

    # Check for frontmatter field
    if "frontmatter" not in data:
        raise DataLoadError(
            "Data must contain 'frontmatter' field (MarkdownDataDict format)"
        )

    # Check for content field
    if "content" not in data:
        raise DataLoadError(
            "Data must contain 'content' field (MarkdownDataDict format)"
        )

    # Validate content structure (must be SectionData)
    content = data["content"]
    if not isinstance(content, dict):
        raise DataLoadError(
            f"'content' field must be a dictionary (SectionData format), "
            f"got {type(content).__name__}"
        )

    # Root section requires id, title, level (path is optional for root)
    required_fields = ["id", "title", "level"]
    missing_fields = [f for f in required_fields if f not in content]
    if missing_fields:
        raise DataLoadError(
            f"'content' field missing required fields: {', '.join(missing_fields)}. "
            f"Expected SectionData format with at least: {', '.join(required_fields)}"
        )


def load_markdown_data_dict(
    source: str, format: DataFormat | None = None
) -> MarkdownDataDict:
    """Load and validate MarkdownDataDict from JSON or YAML file/stdin.

    This function loads complete markdown document data in MarkdownDataDict format,
    which includes frontmatter and complete content structure.

    Args:
        source: File path or '-' for stdin
        format: Data format (optional, auto-detected from file extension)

    Returns:
        Validated MarkdownDataDict

    Raises:
        DataLoadError: If file doesn't exist, data is malformed, or structure is invalid

    Examples:
        # Load from JSON file (auto-detected)
        data = load_markdown_data_dict('document.json')

        # Load from YAML file (auto-detected)
        data = load_markdown_data_dict('document.yaml')

        # Load from stdin with explicit format
        data = load_markdown_data_dict('-', format=DataFormat.JSON)

        # Override auto-detection
        data = load_markdown_data_dict('data.txt', format=DataFormat.JSON)
    """
    try:
        # Load raw data using shared loader
        data = _load_raw_data(source, format)

        # Validate structure
        validate_markdown_data_dict(data)

        return data  # type: ignore

    except DataLoadError:
        raise
    except Exception as e:
        source_name = "stdin" if source == "-" else source
        raise DataLoadError(
            f"Failed to load MarkdownDataDict from {source_name}: {e}"
        ) from e
