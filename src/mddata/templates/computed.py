"""Computed parameter resolution for templates."""

import os
import re
from datetime import datetime
from typing import Any

from .models import TemplateFile


def get_date_param() -> str:
    """Get current date in ISO format (YYYY-MM-DD)."""
    return datetime.now().date().isoformat()


def get_time_param() -> str:
    """Get current time in ISO format (HH:MM:SS)."""
    return datetime.now().time().isoformat()


def get_now_param() -> str:
    """Get current datetime in ISO 8601 format."""
    return datetime.now().isoformat()


def get_env_param(var_name: str) -> str | None:
    """Get environment variable value."""
    return os.environ.get(var_name)


def extract_computed_params(content: str) -> set[str]:
    """Extract all computed parameter references from content."""
    # Find all {param} patterns
    pattern = r"\{([^}]+)\}"
    matches = re.findall(pattern, content)
    return set(matches)


def resolve_computed_params(template: TemplateFile) -> dict[str, Any]:
    """Resolve all computed parameters in template."""
    computed_values = {}

    # Extract all computed params from template
    all_computed = set()

    # Check parameters section
    for param_def in template["parameters"].values():
        default = param_def.get("default")
        if default and isinstance(default, str):
            all_computed.update(extract_computed_params(default))

    # Check changes section (recursively)
    def extract_from_changes(changes: dict) -> None:
        for value in changes.values():
            if isinstance(value, str):
                all_computed.update(extract_computed_params(value))
            elif isinstance(value, dict):
                extract_from_changes(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        extract_from_changes(item)

    extract_from_changes(template["changes"])

    # Resolve each computed param
    for param in all_computed:
        if param.startswith("env."):
            var_name = param[4:]  # Remove 'env.' prefix
            computed_values[param] = get_env_param(var_name)
        elif param == "date":
            computed_values[param] = get_date_param()
        elif param == "time":
            computed_values[param] = get_time_param()
        elif param == "now":
            computed_values[param] = get_now_param()
        # Future: Add more computed param types here

    return computed_values
