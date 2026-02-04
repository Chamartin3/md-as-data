"""Template filling engine - unified entry point for template substitution.

This module consolidates all template filling logic into a single, cohesive interface.
It handles parameter resolution, computed values, placeholder substitution, and
comprehensive parameter validation with enums, array constraints, and pattern matching.

Public API:
- TemplateFiller: Main class for filling templates with parameters
- ComputedParam: Enum of available computed parameters

Parameter Validation Features:
- Enum validation with strict/non-strict modes and descriptions
- Array constraints (min_items, max_items, unique_items)
- Array item enum validation with pattern fallback
- Regex pattern validation for strings and array items
- Combined validation modes for flexible parameter acceptance
"""

import json
import os
import re
import sys
import warnings
from collections.abc import Callable
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, TypedDict

import yaml

from mddata.errors import ParameterValidationError
from mddata.models import (
    MarkdownDataUpdate,
    MarkdownForm,
    MarkdownFormField,
    ParameterType,
    ParameterValue,
    ResolvedParameters,
)

# ==================================================================
# Type Definitions
# ==================================================================


class TemplateDict(TypedDict, total=False):
    """Type-safe template dictionary structure.

    This represents the serialized template structure used during
    placeholder substitution operations.
    """

    frontmatter: dict[str, ParameterValue]
    frontmatter_policy: str
    content: dict[str, object] | None
    sections: list[dict[str, object]]
    parameters: dict[str, MarkdownFormField]


class ArrayItemConstraints(TypedDict, total=False):
    """Constraints for array item type validation."""

    item_type: ParameterType


class ParameterConstraints(TypedDict, total=False):
    """Type-safe parameter constraints for validation."""

    min: int | float
    max: int | float
    pattern: str


# ==================================================================
# Computed Parameter Enum
# ==================================================================


class ComputedParam(Enum):
    """Available computed parameters with resolver functions.

    Each parameter stores its resolver function that returns the computed value.
    Parameters can be used in templates without explicit definition.
    They are resolved at template fill time with current runtime values.

    Usage:
        value = ComputedParam.DATE.resolve()
        value = ComputedParam.resolve_param("date")
        is_computed = ComputedParam.is_computed("date")
    """

    DATE = ("date", lambda: datetime.now().date().isoformat())
    TIME = ("time", lambda: datetime.now().time().isoformat())
    NOW = ("now", lambda: datetime.now().isoformat())

    def __init__(self, param_name: str, resolver: Callable[[], str]) -> None:
        """Initialize computed parameter with name and resolver function."""
        self.param_name = param_name
        self.resolver = resolver

    def resolve(self) -> str:
        """Resolve this computed parameter to its current value."""
        return self.resolver()

    @classmethod
    def from_name(cls, param_name: str) -> "ComputedParam | None":
        """Get ComputedParam enum from parameter name."""
        for param in cls:
            if param.param_name == param_name:
                return param
        return None

    @classmethod
    def is_env_param(cls, param_name: str) -> bool:
        """Check if parameter is an environment variable reference."""
        return param_name.startswith("env.")

    @classmethod
    def resolve_env_param(cls, param_name: str) -> str | None:
        """Resolve environment variable parameter."""
        if not cls.is_env_param(param_name):
            raise ValueError(f"Not an env parameter: {param_name}")

        var_name = param_name[4:]  # Remove 'env.' prefix
        return os.environ.get(var_name)

    @classmethod
    def is_computed(cls, param_name: str) -> bool:
        """Check if parameter name is a computed parameter."""
        return cls.is_env_param(param_name) or cls.from_name(param_name) is not None

    @classmethod
    def resolve_param(cls, param_name: str) -> str | None:
        """Resolve any computed parameter by name."""
        # Try environment variable
        if cls.is_env_param(param_name):
            return cls.resolve_env_param(param_name)

        # Try enum member
        param = cls.from_name(param_name)
        if param:
            return param.resolve()

        raise ValueError(f"Unknown computed parameter: {param_name}")


# ==================================================================
# Placeholder Substitution
# ==================================================================

# Compiled regex patterns for performance
PLACEHOLDER_PATTERN = re.compile(r"(?<!\\)\{([a-zA-Z_][a-zA-Z0-9_\.]*)\}")
ESCAPE_PATTERN = re.compile(r"\\(\{)")


def _format_value(value: ParameterValue) -> str:
    """Format a parameter value for string substitution."""
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    elif isinstance(value, bool):
        return str(value).lower()
    elif value is None:
        return ""
    else:
        return str(value)


def _substitute_placeholders(content: str, params: ResolvedParameters) -> str:
    """Replace all placeholders with parameter values."""
    if not isinstance(content, str):
        return content

    def replace_placeholder(match: re.Match[str]) -> str:
        param_name = match.group(1)
        if param_name not in params:
            raise ValueError(f"Unknown placeholder: {{{param_name}}}")
        value = params[param_name]
        return _format_value(value)

    # First substitute placeholders
    result = PLACEHOLDER_PATTERN.sub(replace_placeholder, content)

    # Then unescape literal braces
    result = ESCAPE_PATTERN.sub(r"\1", result)

    return result


def _substitute_in_value(value: object, params: ResolvedParameters) -> object:
    """Recursively substitute placeholders in any value type."""
    if isinstance(value, str):
        return _substitute_placeholders(value, params)
    elif isinstance(value, dict):
        return _substitute_in_dict(value, params)
    elif isinstance(value, list):
        return _substitute_in_list(value, params)
    else:
        return value


def _substitute_in_dict(
    data: dict[str, object], params: ResolvedParameters
) -> dict[str, object]:
    """Recursively substitute placeholders in dictionary."""
    result: dict[str, object] = {}
    for key, value in data.items():
        result[key] = _substitute_in_value(value, params)
    return result


def _substitute_in_list(
    items: list[object], params: ResolvedParameters
) -> list[object]:
    """Recursively substitute placeholders in list."""
    result: list[object] = []
    for item in items:
        result.append(_substitute_in_value(item, params))
    return result


# ==================================================================
# Computed Parameters
# ==================================================================


def _extract_computed_params(content: str) -> set[str]:
    """Extract all computed parameter references from content."""
    pattern = r"\{([^}]+)\}"
    matches = re.findall(pattern, content)
    return set(matches)


def _extract_from_value(value: object, accumulator: set[str]) -> None:
    """Recursively extract computed params from any value type."""
    if isinstance(value, str):
        accumulator.update(_extract_computed_params(value))
    elif isinstance(value, dict):
        _extract_from_dict(value, accumulator)
    elif isinstance(value, list):
        _extract_from_list(value, accumulator)


def _extract_from_dict(data: dict[str, object], accumulator: set[str]) -> None:
    """Recursively extract computed params from dictionary."""
    for value in data.values():
        _extract_from_value(value, accumulator)


def _extract_from_list(items: list[object], accumulator: set[str]) -> None:
    """Recursively extract computed params from list."""
    for item in items:
        _extract_from_value(item, accumulator)


def _resolve_computed_params(
    template: MarkdownDataUpdate,
) -> ResolvedParameters:
    """Resolve all computed parameters in template using enum-based resolution."""
    computed_values: dict[str, ParameterValue] = {}
    all_computed: set[str] = set()

    # Check parameters section
    for param_def in template.parameters.values():
        default = param_def.get("default")
        if default and isinstance(default, str):
            all_computed.update(_extract_computed_params(default))

    # Check template data by converting to dict
    template_dict = template.to_dict()

    # Extract from frontmatter
    if frontmatter := template_dict.get("frontmatter"):
        if isinstance(frontmatter, dict):
            _extract_from_dict(frontmatter, all_computed)

    # Extract from sections
    if sections := template_dict.get("sections"):
        if isinstance(sections, list):
            _extract_from_list(sections, all_computed)

    # Extract from hierarchical content
    if content := template_dict.get("content"):
        if isinstance(content, dict):
            _extract_from_dict(content, all_computed)

    # Resolve each computed param using enum
    for param in all_computed:
        if ComputedParam.is_computed(param):
            try:
                value = ComputedParam.resolve_param(param)
                computed_values[param] = value
            except ValueError:
                # Skip unknown computed params (they might be user-defined params)
                pass

    return computed_values


# ==================================================================
# Parameter Parsing
# ==================================================================


def _parse_param_value(value: str, param_def: MarkdownFormField) -> ParameterValue:
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
        return str(value)
    elif param_type == ParameterType.ARRAY:
        return _parse_array_param(value, param_def.get("item_type"), param_def)
    else:
        raise ValueError(f"Unsupported parameter type: {param_type}")


def _parse_array_param(
    value: str,
    item_type: ParameterType | None,
    param_def: MarkdownFormField | None = None,
) -> list[str]:
    """Parse JSON array parameter with item type validation and constraints.

    Returns list[str] to match ParameterValue type definition.
    Mixed-type arrays are converted to strings.
    """
    # Try parsing as JSON first
    try:
        parsed = json.loads(value)
        if not isinstance(parsed, list):
            raise ValueError(f"Expected JSON array, got {type(parsed)}")
    except json.JSONDecodeError:
        # If JSON parsing fails, try comma-separated values (shell-friendly)
        # Split on commas and strip whitespace
        items = [item.strip() for item in value.split(",") if item.strip()]
        if not items:
            # Empty value - return empty list
            parsed = []
        else:
            parsed = items

    # Validate array constraints if param_def provided
    if param_def:
        _validate_array_constraints(parsed, param_def)
        _validate_array_item_enum(parsed, param_def)
        _validate_array_item_pattern(parsed, param_def)

    # Validate item types if specified
    if item_type:
        for i, item in enumerate(parsed):
            if item_type == ParameterType.STR and not isinstance(item, str):
                raise ValueError(f"Array item {i} must be string")
            elif item_type == ParameterType.INT and not isinstance(item, int):
                raise ValueError(f"Array item {i} must be integer")
            elif item_type == ParameterType.FLOAT and not isinstance(
                item, (int, float)
            ):
                raise ValueError(f"Array item {i} must be number")
            elif item_type == ParameterType.BOOL and not isinstance(item, bool):
                raise ValueError(f"Array item {i} must be boolean")

    # Convert all items to strings for type safety
    # ParameterValue only supports list[str]
    return [str(item) for item in parsed]


def _validate_param_constraints(
    param_name: str, value: ParameterValue, param_def: MarkdownFormField
) -> None:
    """Validate parameter against constraints (min, max, pattern, enum).

    Args:
        param_name: Name of the parameter being validated
        value: Parameter value to validate
        param_def: Parameter definition with constraints

    Raises:
        ValueError: If validation fails, with parameter name in message
    """

    # Array constraints (check first for arrays)
    if isinstance(value, list):
        try:
            _validate_array_constraints(value, param_def)
            _validate_array_item_enum(value, param_def)
        except ValueError as e:
            # Re-raise with parameter name if not already included
            error_msg = str(e)
            if "Parameter '" not in error_msg:
                raise ValueError(f"Parameter '{param_name}': {error_msg}") from e
            raise
        return  # Skip other constraints for arrays

    # NEW: Enum constraint (check first for better error messages)
    enum_values = param_def.get("enum")
    if enum_values is not None:
        enum_strict = param_def.get("enum_strict", True)
        enum_descriptions = param_def.get("enum_descriptions", {})

        if value not in enum_values:
            # Build helpful message
            allowed_str = ", ".join(str(v) for v in enum_values)
            msg = (
                f"Parameter '{param_name}': value '{value}' "
                f"not in enum values: [{allowed_str}]"
            )

            if enum_descriptions:
                msg += "\n\nAvailable options:"
                for val in enum_values:
                    desc = enum_descriptions.get(str(val), "")
                    if desc:
                        msg += f"\n  {val} - {desc}"
                    else:
                        msg += f"\n  {val}"

            if enum_strict:
                raise ValueError(msg)
            else:
                warnings.warn(
                    f"Parameter validation warning: {msg}", UserWarning, stacklevel=2
                )
        return  # Skip other constraints after enum check

    # Min constraint
    min_val = param_def.get("min")
    if min_val is not None:
        if isinstance(value, (int, float)) and value < min_val:
            raise ValueError(
                f"Parameter '{param_name}': value {value} "
                f"is less than minimum {min_val}"
            )
        elif isinstance(value, str) and len(value) < min_val:
            raise ValueError(
                f"Parameter '{param_name}': string length {len(value)} "
                f"is less than minimum {min_val} (got: '{value}')"
            )

    # Max constraint
    max_val = param_def.get("max")
    if max_val is not None:
        if isinstance(value, (int, float)) and value > max_val:
            raise ValueError(
                f"Parameter '{param_name}': value {value} "
                f"is greater than maximum {max_val}"
            )
        elif isinstance(value, str) and len(value) > max_val:
            raise ValueError(
                f"Parameter '{param_name}': string length {len(value)} "
                f"is greater than maximum {max_val}"
            )

    # Pattern constraint
    pattern = param_def.get("pattern")
    if pattern and isinstance(value, str):
        if not re.match(pattern, value):
            raise ValueError(
                f"Parameter '{param_name}': value '{value}' "
                f"does not match pattern '{pattern}'"
            )


def _validate_array_constraints(value: list[Any], param_def: MarkdownFormField) -> None:
    """Validate array-specific constraints (min_items, max_items, unique_items).

    Args:
        value: The array value to validate
        param_def: Parameter definition containing constraint specifications

    Raises:
        ValueError: If any constraint is violated with descriptive error messages
    """
    # Min items constraint
    min_items = param_def.get("min_items")
    if min_items is not None and len(value) < min_items:
        raise ValueError(
            f"Array must have at least {min_items} items, got {len(value)}"
        )

    # Max items constraint
    max_items = param_def.get("max_items")
    if max_items is not None and len(value) > max_items:
        raise ValueError(f"Array must have at most {max_items} items, got {len(value)}")

    # Unique items constraint
    unique_items = param_def.get("unique_items")
    if unique_items and len(value) != len(set(value)):
        raise ValueError("Array items must be unique")


def _validate_array_item_enum(value: list[Any], param_def: MarkdownFormField) -> None:
    """Validate array items against enum constraints with pattern fallback.

    When item_enum_strict=False and item_pattern is defined, items are accepted
    if they match either the enum OR the pattern. Only warns/errors when items
    match neither.

    Args:
        value: The array value to validate
        param_def: Parameter definition containing enum and pattern specifications

    Raises:
        ValueError: If strict validation fails
        UserWarning: If non-strict validation fails (via warnings.warn)
    """
    item_enum = param_def.get("item_enum")
    if item_enum is None:
        return

    item_enum_strict = param_def.get("item_enum_strict", True)
    item_enum_descriptions = param_def.get("item_enum_descriptions", {})
    item_pattern = param_def.get("item_pattern")

    for i, item in enumerate(value):
        if item not in item_enum:
            # If non-strict and pattern exists, check if item matches pattern
            if not item_enum_strict and item_pattern and isinstance(item, str):
                pattern = re.compile(item_pattern)
                if pattern.match(item):
                    continue  # Item matches pattern, allow it

            # Build helpful message
            allowed_str = ", ".join(str(v) for v in item_enum)
            msg = f"Array item [{i}] = '{item}' not in enum values: [{allowed_str}]"

            if item_enum_descriptions:
                msg += "\n\nAvailable options:"
                for val in item_enum:
                    desc = item_enum_descriptions.get(str(val), "")
                    if desc:
                        msg += f"\n  {val} - {desc}"
                    else:
                        msg += f"\n  {val}"

            if item_enum_strict:
                raise ValueError(msg)
            else:
                warnings.warn(
                    f"Parameter validation warning: {msg}", UserWarning, stacklevel=2
                )


def _validate_array_item_pattern(
    value: list[Any], param_def: MarkdownFormField
) -> None:
    """Validate array items against regex pattern.

    Only validates string items. Skips validation when non-strict item_enum
    is present (handled by _validate_array_item_enum).

    Args:
        value: The array value to validate
        param_def: Parameter definition containing pattern specification

    Raises:
        ValueError: If any string item doesn't match the pattern
    """
    item_pattern = param_def.get("item_pattern")
    if item_pattern is None:
        return

    # If there's a non-strict item_enum, pattern validation is already handled there
    item_enum = param_def.get("item_enum")
    item_enum_strict = param_def.get("item_enum_strict", True)
    if item_enum is not None and not item_enum_strict:
        return

    pattern = re.compile(item_pattern)

    for i, item in enumerate(value):
        # Pattern validation only applies to strings
        if not isinstance(item, str):
            continue

        if not pattern.match(item):
            raise ValueError(
                f"Array item [{i}] = '{item}' does not match pattern '{item_pattern}'"
            )


def _load_params_from_file(filepath: str) -> dict[str, ParameterValue]:
    """Load parameters from JSON/YAML file."""
    if not Path(filepath).exists():
        raise FileNotFoundError(f"Parameter file not found: {filepath}")

    suffix = Path(filepath).suffix.lower()
    file_content: dict[str, ParameterValue]

    if suffix == ".json":
        with open(filepath, encoding="utf-8") as f:
            file_content = json.load(f)
    elif suffix in (".yaml", ".yml"):
        with open(filepath, encoding="utf-8") as f:
            file_content = yaml.safe_load(f)
    else:
        raise ValueError(f"Unsupported parameter file format: {suffix}")

    return file_content


def _read_param_from_file(filepath: str) -> str:
    """Read parameter value from file (@filepath syntax)."""
    if not Path(filepath).exists():
        raise FileNotFoundError(f"Parameter file not found: {filepath}")

    with open(filepath, encoding="utf-8") as f:
        return f.read().strip()


def _read_param_from_stdin(interactive: bool = False) -> str:
    """Read parameter from stdin (- for interactive, @- for piped)."""
    if interactive:
        print("Enter parameter value (Ctrl+D to finish):", file=sys.stderr)
        return input().strip()
    else:
        return sys.stdin.read().strip()


def _parse_cli_params(
    params: list[str],
    definitions: dict[str, MarkdownFormField],
    computed: ResolvedParameters,
    params_file: str | None = None,
    params_dict: dict[str, Any] | None = None,
) -> ResolvedParameters:
    """Parse and validate CLI parameters with precedence.

    Precedence order (lowest to highest):
    1. Computed parameters
    2. Template defaults
    3. Params file
    4. Params dict
    5. CLI params

    NOTE: The operations layer now validates parameters BEFORE calling this function,
    so this validation is a safety net for direct API usage.
    """
    resolved_values: dict[str, ParameterValue] = {}

    # Start with computed parameters (lowest precedence)
    resolved_values.update(computed)

    # Add template defaults (next precedence level)
    for key, param_def in definitions.items():
        default = param_def.get("default")
        if default is not None and key not in resolved_values:
            # Resolve env variables in default values (e.g., "env.VAR_NAME")
            if isinstance(default, str) and default.startswith("env."):
                import os

                env_var_name = default[4:]  # Remove "env." prefix
                default = os.getenv(env_var_name, default)
            resolved_values[key] = default

    # Load from params file if specified
    if params_file:
        file_params = _load_params_from_file(params_file)
        resolved_values.update(file_params)

    # Load from params dict if specified (higher precedence than file)
    if params_dict:
        # Validate and parse each parameter from dict
        for key, value in params_dict.items():
            if key in definitions:
                param_def = definitions[key]
                # Value is already parsed from JSON/YAML, just validate
                try:
                    _validate_param_constraints(key, value, param_def)
                except ValueError as e:
                    # Wrap constraint validation errors in ParameterValidationError
                    raise ParameterValidationError(
                        missing_params=[],
                        provided_params=[key],
                        available_params=list(definitions.keys()),
                        param_definitions=definitions,
                    ) from e
                resolved_values[key] = value

    # Track stdin usage to prevent multiple consumption
    stdin_used = False

    # Parse CLI parameters (highest precedence)
    for param_str in params:
        if "=" not in param_str:
            raise ValueError(f"Invalid parameter format: {param_str}")

        key, value_spec = param_str.split("=", 1)

        if key not in definitions:
            # Raise ParameterValidationError for unknown parameters
            available = list(definitions.keys())
            provided = [k for k in [key]]
            raise ParameterValidationError(
                missing_params=[],
                provided_params=provided,
                available_params=available,
                param_definitions=definitions,
            )

        param_def = definitions[key]

        # Handle different value sources
        raw_value: str
        if value_spec.startswith("@"):
            # From file or stdin
            if value_spec == "@-":
                if stdin_used:
                    raise ValueError("Cannot use stdin for multiple parameters")
                stdin_used = True
                raw_value = _read_param_from_stdin(interactive=False)
            else:
                filepath = value_spec[1:]  # Remove @
                raw_value = _read_param_from_file(filepath)
        elif value_spec == "-":
            # Interactive stdin
            if stdin_used:
                raise ValueError("Cannot use stdin for multiple parameters")
            stdin_used = True
            raw_value = _read_param_from_stdin(interactive=True)
        else:
            # Direct value
            raw_value = value_spec

        # Parse and validate
        try:
            parsed_value = _parse_param_value(raw_value, param_def)
            _validate_param_constraints(key, parsed_value, param_def)
        except ValueError as e:
            # Wrap parsing and constraint validation errors in ParameterValidationError
            raise ParameterValidationError(
                missing_params=[],
                provided_params=[key],
                available_params=list(definitions.keys()),
                param_definitions=definitions,
            ) from e
        resolved_values[key] = parsed_value

    # Check required parameters with enhanced error messages
    missing = []
    for key, param_def in definitions.items():
        if param_def.get("required", False) and key not in resolved_values:
            missing.append(key)

    if missing:
        # Enhanced error message with parameter definitions
        provided = [k for k in resolved_values.keys() if k not in computed]
        available = list(definitions.keys())
        raise ParameterValidationError(
            missing_params=missing,
            provided_params=provided,
            available_params=available,
            param_definitions=definitions,
        )

    return resolved_values


# ==================================================================
# Public API
# ==================================================================


class MarkdownFormFiller:
    """Fill markdown forms with parameter values.

    Takes a MarkdownForm (with parameters) and fills placeholders
    with concrete values to produce MarkdownDataUpdate (complete data).

    Flow:
        MarkdownForm → MarkdownFormFiller.fill() → MarkdownDataUpdate
        (has params)                                (no params, ready to use)

    Renamed from TemplateFiller for consistency with MarkdownForm.
    """

    def __init__(self, form: MarkdownForm) -> None:
        """Initialize filler with a form.

        Args:
            form: MarkdownForm instance (must have parameters)

        Raises:
            TypeError: If form is not a MarkdownForm or MarkdownDataUpdate
                      with parameters
        """
        # Auto-convert MarkdownDataUpdate with parameters to MarkdownForm
        if isinstance(form, MarkdownDataUpdate) and not isinstance(form, MarkdownForm):
            if form.parameters:
                # Convert to MarkdownForm
                form = MarkdownForm(
                    frontmatter=form.frontmatter,
                    content=form.content,
                    frontmatter_policy=form.frontmatter_policy,
                    parameters=form.parameters,
                    sections=form.sections,
                )
            else:
                raise TypeError(
                    f"Expected MarkdownForm with parameters, got "
                    f"{type(form).__name__} without parameters. "
                    "Use MarkdownForm for parameterized templates."
                )
        elif not isinstance(form, MarkdownForm):
            raise TypeError(
                f"Expected MarkdownForm, got {type(form).__name__}. "
                "Use MarkdownForm for parameterized templates."
            )

        self.form = form
        self.parameters = form.parameters
        self._computed_params: ResolvedParameters | None = None

    def fill(
        self,
        cli_params: list[str] | None = None,
        params_file: str | None = None,
        params_dict: dict[str, Any] | None = None,
    ) -> MarkdownDataUpdate:
        """Fill form with parameter values.

        Returns MarkdownDataUpdate (no parameters) because the filled
        result is complete data ready to use.

        Args:
            cli_params: List of KEY=VALUE parameter strings
            params_file: Path to parameter file (JSON/YAML)
            params_dict: Dictionary of parameters (pre-loaded)

        Returns:
            MarkdownDataUpdate with placeholders filled

        Raises:
            ParameterValidationError: On validation failures
        """
        # Resolve all parameters with proper precedence
        resolved_params = self._resolve_all_parameters(
            cli_params or [], params_file, params_dict
        )

        # Convert form to dict for substitution
        form_dict = self.form.to_dict()

        # Substitute placeholders recursively
        substituted_dict = _substitute_in_dict(form_dict, resolved_params)

        # Create filled MarkdownDataUpdate from substituted dict
        # Remove parameters since this is now complete data
        if "parameters" in substituted_dict:
            del substituted_dict["parameters"]

        filled_update = MarkdownDataUpdate.from_dict(substituted_dict)

        return filled_update

    def _resolve_all_parameters(
        self,
        cli_params: list[str],
        params_file: str | None,
        params_dict: dict[str, Any] | None = None,
    ) -> ResolvedParameters:
        """Resolve parameters with proper precedence."""
        # Get computed parameters (cache for efficiency)
        if self._computed_params is None:
            self._computed_params = _resolve_computed_params(self.form)

        computed = self._computed_params

        # Parse CLI params with precedence handling built-in
        resolved = _parse_cli_params(
            cli_params,
            self.form.parameters,
            computed,
            params_file=params_file,
            params_dict=params_dict,
        )

        # Add empty strings for optional parameters that weren't provided
        # This ensures placeholder substitution doesn't fail for optional params
        for key, param_def in self.form.parameters.items():
            if key not in resolved:
                # Only add if parameter is optional (not required)
                if not param_def.get("required", False):
                    resolved[key] = ""

        # Auto-generate {param_name_list} placeholders for array parameters
        # This formats arrays as markdown bullet lists
        for key, value in list(resolved.items()):
            param_def = self.form.parameters.get(key, {})
            if param_def.get("type") == ParameterType.ARRAY and isinstance(value, list):
                # Create formatted list version
                if value:
                    list_content = "\n".join(f"- {item}" for item in value)
                else:
                    list_content = ""
                resolved[f"{key}_list"] = list_content
            elif param_def.get("type") == ParameterType.ARRAY and not value:
                # Empty array or empty string for optional arrays
                resolved[f"{key}_list"] = ""

        # Resolve computed placeholders in parameter values themselves
        final_params: dict[str, ParameterValue] = {}
        for key, value in resolved.items():
            if isinstance(value, str):
                resolved_value = _substitute_placeholders(value, resolved)
                final_params[key] = resolved_value
            else:
                final_params[key] = value

        return final_params

    def get_computed_parameters(self) -> ResolvedParameters:
        """Get computed parameters (date, time, env vars) for this form."""
        if self._computed_params is None:
            self._computed_params = _resolve_computed_params(self.form)
        return self._computed_params.copy()

    def get_parameter_info(self) -> dict[str, object]:
        """Get information about form parameters."""
        return {
            "definitions": self.form.parameters,
            "computed": self.get_computed_parameters(),
        }


# Backward compatibility alias
TemplateFiller = MarkdownFormFiller
