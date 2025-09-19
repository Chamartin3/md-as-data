"""Template loading engine with JSON/YAML format detection and validation."""

import json
import sys
from pathlib import Path
from typing import Any, Literal, cast

import yaml

from .models import TemplateFile


def detect_template_format(path: str) -> Literal["json", "yaml"]:
    """Detect format based on file extension."""
    suffix = Path(path).suffix.lower()
    if suffix == ".json":
        return "json"
    elif suffix in (".yaml", ".yml"):
        return "yaml"
    else:
        raise ValueError(
            f"Unsupported file extension '{suffix}'. Use .json, .yaml, or .yml"
        )


def _validate_template_structure(data: dict[str, Any]) -> TemplateFile:
    """Validate template structure and return typed template."""
    if not isinstance(data, dict):
        raise ValueError("Template must be a dictionary")

    # Parameters is optional - defaults to empty dict
    if "parameters" not in data:
        data["parameters"] = {}

    if "changes" not in data:
        raise ValueError("Template must contain 'changes' section")

    if not isinstance(data["parameters"], dict):
        raise ValueError("'parameters' must be a dictionary")

    if not isinstance(data["changes"], dict):
        raise ValueError("'changes' must be a dictionary")

    changes = data["changes"]
    if "frontmatter" not in changes and "sections" not in changes:
        raise ValueError("'changes' must contain 'frontmatter' or 'sections'")

    if "sections" in changes:
        if not isinstance(changes["sections"], list):
            raise ValueError("'changes.sections' must be a list")
        for section in changes["sections"]:
            if not isinstance(section, dict):
                raise ValueError(
                    "Each section in 'changes.sections' must be a dictionary"
                )
            if "id" not in section or "content" not in section:
                raise ValueError("Each section must have 'id' and 'content' fields")

    return cast(TemplateFile, data)


def load_template(path: str) -> TemplateFile:
    """Load and validate template file with auto-format detection."""
    if not Path(path).exists():
        raise FileNotFoundError(f"Template file not found: {path}")

    format_type = detect_template_format(path)

    try:
        with open(path, encoding="utf-8") as f:
            content = f.read()

        if format_type == "json":
            data = json.loads(content)
        else:  # yaml
            data = yaml.safe_load(content)

        return _validate_template_structure(data)

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in template file '{path}': {e}")
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in template file '{path}': {e}")
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid template structure in '{path}': {e}")
    except Exception as e:
        raise ValueError(f"Failed to load template from '{path}': {e}")


def load_template_from_stdin(format: str = "yaml") -> TemplateFile:
    """Load template from stdin with specified format."""
    if format not in ("json", "yaml"):
        raise ValueError(f"Unsupported format '{format}'. Use 'json' or 'yaml'")

    try:
        content = sys.stdin.read()

        if format == "json":
            data = json.loads(content)
        else:  # yaml
            data = yaml.safe_load(content)

        return _validate_template_structure(data)

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON from stdin: {e}")
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML from stdin: {e}")
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid template structure from stdin: {e}")
    except Exception as e:
        raise ValueError(f"Failed to load template from stdin: {e}")
