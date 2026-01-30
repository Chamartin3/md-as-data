"""Schema file loader for JSON and YAML formats.

This module provides utilities for loading DocumentSchema from files
with automatic format detection based on file extensions.
"""

import json
from pathlib import Path

from mddata.models.schema import DocumentSchema


def load_schema(source: str | Path) -> DocumentSchema:
    """Load schema from JSON or YAML file with automatic format detection.

    Detection strategy:
    1. Check file extension (.yaml/.yml vs .json)
    2. Try format-specific parser based on extension
    3. Fall back to alternate format if parsing fails

    Args:
        source: Path to schema file (str or Path object)

    Returns:
        Loaded schema as DocumentSchema dictionary

    Raises:
        FileNotFoundError: If schema file doesn't exist
        ValueError: If file cannot be parsed as JSON or YAML

    Examples:
        # Load JSON schema
        schema = load_schema('schema.json')

        # Load YAML schema
        schema = load_schema('schema.yaml')

        # Works with Path objects
        schema = load_schema(Path('schema.yml'))
    """
    schema_path = Path(source)

    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    content = schema_path.read_text(encoding="utf-8")
    suffix = schema_path.suffix.lower()

    # Try extension-based detection first
    if suffix in [".yaml", ".yml"]:
        try:
            import yaml

            return yaml.safe_load(content)  # type: ignore
        except ImportError:
            # Fall back to JSON if YAML not available
            pass
        except Exception as e:
            raise ValueError(f"Invalid YAML schema format: {e}") from e

    # Try JSON parsing (default for .json or unknown extensions)
    try:
        return json.loads(content)  # type: ignore
    except json.JSONDecodeError as e:
        # Try YAML as fallback
        try:
            import yaml

            return yaml.safe_load(content)  # type: ignore
        except ImportError:
            raise ValueError(
                f"Invalid JSON format and PyYAML not installed. JSON error: {e}"
            ) from e
        except Exception as yaml_error:
            raise ValueError(
                f"Invalid schema format. JSON error: {e}. YAML error: {yaml_error}"
            ) from e


__all__ = ["load_schema"]
