"""Parameter parsing and validation for templates."""

import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

from .models import ParameterDefinition, ParameterType, ResolvedParameters


def parse_param_value(value: str, param_def: ParameterDefinition) -> Any:
    """Parse single parameter value with type coercion."""
    param_type = param_def["type"]

    if param_type == ParameterType.STR:
        return str(value)
    elif param_type == ParameterType.INT:
        try:
            return int(value)
        except ValueError:
            raise ValueError(f"Cannot convert '{value}' to integer")
    elif param_type == ParameterType.FLOAT:
        try:
            return float(value)
        except ValueError:
            raise ValueError(f"Cannot convert '{value}' to float")
    elif param_type == ParameterType.BOOL:
        if value.lower() in ("true", "1", "yes", "on"):
            return True
        elif value.lower() in ("false", "0", "no", "off"):
            return False
        else:
            raise ValueError(f"Cannot convert '{value}' to boolean")
    elif param_type == ParameterType.DATE:
        # For now, treat dates as strings - could add date validation later
        return str(value)
    elif param_type == ParameterType.ARRAY:
        # Parse JSON array
        return parse_array_param(value, param_def.get("item_type"))
    else:
        raise ValueError(f"Unsupported parameter type: {param_type}")


def parse_array_param(value: str, item_type: ParameterType | None) -> list[Any]:
    """Parse JSON array parameter with item type validation."""
    try:
        parsed = json.loads(value)
        if not isinstance(parsed, list):
            raise ValueError(f"Expected JSON array, got {type(parsed)}")

        # Validate item types if specified
        if item_type:
            for i, item in enumerate(parsed):
                if item_type == ParameterType.STR and not isinstance(item, str):
                    raise ValueError(f"Array item {i} must be string, got {type(item)}")
                elif item_type == ParameterType.INT and not isinstance(item, int):
                    raise ValueError(
                        f"Array item {i} must be integer, got {type(item)}"
                    )
                elif item_type == ParameterType.FLOAT and not isinstance(
                    item, (int, float)
                ):
                    raise ValueError(f"Array item {i} must be number, got {type(item)}")
                elif item_type == ParameterType.BOOL and not isinstance(item, bool):
                    raise ValueError(
                        f"Array item {i} must be boolean, got {type(item)}"
                    )

        return parsed
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON array: {e}")


def validate_param_constraints(value: Any, param_def: ParameterDefinition) -> None:
    """Validate parameter against constraints (min, max, pattern)."""
    # Min constraint
    min_val = param_def.get("min")
    if min_val is not None:
        if isinstance(value, (int, float)) and value < min_val:
            raise ValueError(f"Value {value} is less than minimum {min_val}")
        elif isinstance(value, str) and len(value) < min_val:
            raise ValueError(
                f"String length {len(value)} is less than minimum {min_val}"
            )

    # Max constraint
    max_val = param_def.get("max")
    if max_val is not None:
        if isinstance(value, (int, float)) and value > max_val:
            raise ValueError(f"Value {value} is greater than maximum {max_val}")
        elif isinstance(value, str) and len(value) > max_val:
            raise ValueError(
                f"String length {len(value)} is greater than maximum {max_val}"
            )

    # Pattern constraint
    pattern = param_def.get("pattern")
    if pattern and isinstance(value, str):
        if not re.match(pattern, value):
            raise ValueError(f"Value '{value}' does not match pattern '{pattern}'")


def load_params_from_file(filepath: str) -> dict[str, Any]:
    """Load parameters from JSON/YAML file."""
    if not Path(filepath).exists():
        raise FileNotFoundError(f"Parameter file not found: {filepath}")

    # Detect format by extension
    suffix = Path(filepath).suffix.lower()
    if suffix == ".json":
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)
    elif suffix in (".yaml", ".yml"):
        with open(filepath, encoding="utf-8") as f:
            return yaml.safe_load(f)
    else:
        raise ValueError(f"Unsupported parameter file format: {suffix}")


def read_param_from_file(filepath: str) -> str:
    """Read parameter value from file (@filepath syntax)."""
    if not Path(filepath).exists():
        raise FileNotFoundError(f"Parameter file not found: {filepath}")

    with open(filepath, encoding="utf-8") as f:
        return f.read().strip()


def read_param_from_stdin(interactive: bool = False) -> str:
    """Read parameter from stdin (- for interactive, @- for piped)."""
    if interactive:
        print("Enter parameter value (Ctrl+D to finish):", file=sys.stderr)
        return input().strip()
    else:
        return sys.stdin.read().strip()


def parse_cli_params(
    params: list[str],
    definitions: dict[str, ParameterDefinition],
    computed: dict[str, Any],
    params_file: str | None = None,
) -> ResolvedParameters:
    """Parse and validate CLI parameters with precedence."""
    resolved_values = {}

    # Start with computed parameters (lowest precedence)
    resolved_values.update(computed)

    # Add template defaults (next precedence level)
    for key, param_def in definitions.items():
        default = param_def.get("default")
        if default is not None and key not in resolved_values:
            resolved_values[key] = default

    # Load from params file if specified
    if params_file:
        file_params = load_params_from_file(params_file)
        resolved_values.update(file_params)

    # Track stdin usage to prevent multiple consumption
    stdin_used = False

    # Parse CLI parameters (highest precedence)
    for param_str in params:
        if "=" not in param_str:
            raise ValueError(f"Invalid parameter format: {param_str}. Use key=value")

        key, value_spec = param_str.split("=", 1)

        if key not in definitions:
            raise ValueError(f"Unknown parameter: {key}")

        param_def = definitions[key]

        # Handle different value sources
        if value_spec.startswith("@"):
            # From file or stdin
            if value_spec == "@-":
                # From piped stdin
                if stdin_used:
                    raise ValueError(
                        "Cannot use stdin for multiple parameters. Use files instead."
                    )
                stdin_used = True
                value = read_param_from_stdin(interactive=False)
            else:
                # From file
                filepath = value_spec[1:]  # Remove @
                value = read_param_from_file(filepath)
        elif value_spec == "-":
            # Interactive stdin
            if stdin_used:
                raise ValueError(
                    "Cannot use stdin for multiple parameters. Use files instead."
                )
            stdin_used = True
            value = read_param_from_stdin(interactive=True)
        else:
            # Direct value
            value = value_spec

        # Parse and validate
        parsed_value = parse_param_value(value, param_def)
        validate_param_constraints(parsed_value, param_def)
        resolved_values[key] = parsed_value

    # Check required parameters
    for key, param_def in definitions.items():
        if param_def.get("required", False) and key not in resolved_values:
            raise ValueError(f"Required parameter '{key}' is not provided")

    return resolved_values
