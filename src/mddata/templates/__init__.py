"""Template functionality for markdown data generation."""

from .computed import (
    extract_computed_params,
    get_date_param,
    get_env_param,
    get_now_param,
    get_time_param,
    resolve_computed_params,
)
from .engine import detect_template_format, load_template, load_template_from_stdin
from .models import ParameterDefinition, ParameterType, ResolvedParameters, TemplateFile
from .parameters import (
    load_params_from_file,
    parse_array_param,
    parse_cli_params,
    parse_param_value,
    read_param_from_file,
    read_param_from_stdin,
    validate_param_constraints,
)
from .substitution import (
    find_placeholders,
    format_array_value,
    substitute_in_dict,
    substitute_in_list,
    substitute_placeholders,
    unescape_literal_braces,
    validate_placeholders,
)

__all__ = [
    "ParameterType",
    "ParameterDefinition",
    "TemplateFile",
    "ResolvedParameters",
    "detect_template_format",
    "load_template",
    "load_template_from_stdin",
    "get_date_param",
    "get_time_param",
    "get_now_param",
    "get_env_param",
    "extract_computed_params",
    "resolve_computed_params",
    "load_params_from_file",
    "parse_array_param",
    "parse_cli_params",
    "parse_param_value",
    "read_param_from_file",
    "read_param_from_stdin",
    "validate_param_constraints",
    "find_placeholders",
    "format_array_value",
    "substitute_in_dict",
    "substitute_in_list",
    "substitute_placeholders",
    "unescape_literal_braces",
    "validate_placeholders",
]
