"""Utility for loading schemas from JSON and YAML files."""

import json
from pathlib import Path
from typing import cast

import yaml

from ..models import DocumentSchema


def load_schema(filepath: str) -> DocumentSchema:
    """
    Load schema from JSON or YAML file.

    Args:
        filepath: Path to schema file (.json, .yaml, or .yml)

    Returns:
        DocumentSchema typed dictionary

    Raises:
        ValueError: If file format is unsupported
        FileNotFoundError: If file doesn't exist
    """
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"Schema file not found: {filepath}")

    suffix = path.suffix.lower()

    with open(path) as f:
        if suffix == ".json":
            data = json.load(f)
        elif suffix in (".yaml", ".yml"):
            data = yaml.safe_load(f)
        else:
            raise ValueError(
                f"Unsupported schema format: {suffix}. Use .json, .yaml, or .yml"
            )

    return cast(DocumentSchema, data)
