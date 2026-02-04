"""Source resolution engine for unified write operations."""

import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


@dataclass
class SourceContext:
    """Context containing all loaded sources.

    Attributes:
        form: Form/template structure with parameter definitions
        data: Data values for document creation/modification
        schema: Schema for validation
        cli_params: Parameters from CLI arguments
        params_file: Parameters from parameter file
    """

    form: dict[str, Any] | None = None
    data: dict[str, Any] | None = None
    schema: dict[str, Any] | None = None
    cli_params: dict[str, Any] | None = None
    params_file: dict[str, Any] | None = None


def load_source_file(file_path: Path | str) -> dict[str, Any]:
    """Load JSON or YAML file with automatic format detection.

    Args:
        file_path: Path to file or "-" for stdin

    Returns:
        Parsed file contents as dictionary

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is invalid
    """
    # Handle stdin
    if str(file_path) == "-":
        content = sys.stdin.read()
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            try:
                return yaml.safe_load(content)
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid JSON/YAML from stdin: {e}")

    # Handle file
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Source file not found: {path}")

    content = path.read_text()
    suffix = path.suffix.lower()

    # Try format based on extension
    if suffix == ".json":
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {path}: {e}")
    elif suffix in {".yaml", ".yml"}:
        try:
            return yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {path}: {e}")
    else:
        # Try both formats
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            try:
                return yaml.safe_load(content)
            except yaml.YAMLError as e:
                raise ValueError(f"Could not parse {path} as JSON or YAML: {e}")


def create_source_context(
    data_path: Path | None = None,
    form_path: Path | None = None,
    schema_path: Path | None = None,
    cli_params: dict[str, Any] | None = None,
    params_file_path: Path | None = None,
) -> SourceContext:
    """Create SourceContext by loading all specified sources.

    Args:
        data_path: Path to data file
        form_path: Path to form file
        schema_path: Path to schema file
        cli_params: CLI parameter dictionary
        params_file_path: Path to parameter file

    Returns:
        Populated SourceContext instance

    Raises:
        FileNotFoundError: If any specified file doesn't exist
        ValueError: If any file has invalid format
    """
    return SourceContext(
        data=load_source_file(data_path) if data_path else None,
        form=load_source_file(form_path) if form_path else None,
        schema=load_source_file(schema_path) if schema_path else None,
        cli_params=cli_params,
        params_file=load_source_file(params_file_path) if params_file_path else None,
    )


class SourceResolver:
    """Resolves multiple sources into final document data.

    Resolution order:
    1. Load form structure (if present)
    2. Merge data values (if present)
    3. Apply parameter file (if present)
    4. Apply CLI parameter overrides
    5. Resolve computed parameters
    6. Fill template placeholders
    7. Validate against schema (if present)
    """

    def __init__(self, context: SourceContext):
        """Initialize resolver with source context.

        Args:
            context: SourceContext with loaded sources
        """
        self.context = context

    def resolve(self) -> dict[str, Any]:
        """Resolve all sources into final document data.

        Returns:
            Final resolved document data

        Raises:
            ValueError: If validation fails or parameters are invalid
        """
        result: dict[str, Any] = {}

        # Step 1: Load form structure
        if self.context.form:
            result = self._load_form_structure()

        # Step 2: Merge data
        if self.context.data:
            result = self._merge_data(result, self.context.data)

        # Step 3: Apply parameter file
        if self.context.params_file:
            result = self._apply_parameters(result, self.context.params_file)

        # Step 4: Apply CLI parameters (highest priority)
        if self.context.cli_params:
            result = self._apply_parameters(result, self.context.cli_params)

        # Step 5: Resolve computed parameters
        result = self._resolve_computed_params(result)

        # Step 6: Fill template placeholders
        result = self._fill_placeholders(result)

        # Step 7: Validate if schema present
        if self.context.schema:
            self._validate(result, self.context.schema)

        return result

    def _load_form_structure(self) -> dict[str, Any]:
        """Load form structure from context.

        Returns:
            Form structure as base document data
        """
        if not self.context.form:
            return {}

        # Form should be MarkdownDataUpdate format
        return dict(self.context.form)

    def _merge_data(self, base: dict[str, Any], data: dict[str, Any]) -> dict[str, Any]:
        """Deep merge data into base structure.

        Args:
            base: Base structure (from form)
            data: Data to merge in

        Returns:
            Merged result
        """
        result = dict(base)

        for key, value in data.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._merge_data(result[key], value)
            else:
                result[key] = value

        return result

    def _apply_parameters(
        self, data: dict[str, Any], params: dict[str, Any]
    ) -> dict[str, Any]:
        """Apply parameters to document data.

        Args:
            data: Current document data
            params: Parameters to apply

        Returns:
            Data with parameters applied
        """
        result = dict(data)

        # Apply to frontmatter
        if "frontmatter" in result:
            for key, value in params.items():
                result["frontmatter"][key] = value

        return result

    def _resolve_computed_params(self, data: dict[str, Any]) -> dict[str, Any]:
        """Resolve computed parameter values.

        Computed parameters:
        - date: Current date (YYYY-MM-DD)
        - time: Current time (HH:MM:SS)
        - env.*: Environment variables

        Args:
            data: Document data

        Returns:
            Data with computed parameters resolved
        """
        result = dict(data)

        if "frontmatter" not in result:
            return result

        frontmatter = dict(result["frontmatter"])

        for key, value in frontmatter.items():
            if not isinstance(value, str):
                continue

            # Resolve computed values
            if value == "@computed" or value == "{{date}}":
                if key == "date" or "date" in key.lower():
                    frontmatter[key] = datetime.now().strftime("%Y-%m-%d")
            elif value == "{{time}}":
                frontmatter[key] = datetime.now().strftime("%H:%M:%S")
            elif value.startswith("$"):
                # Environment variable
                env_var = value[1:]
                frontmatter[key] = os.getenv(env_var, value)

        result["frontmatter"] = frontmatter
        return result

    def _fill_placeholders(self, data: dict[str, Any]) -> dict[str, Any]:
        """Fill template placeholders with parameter values.

        Args:
            data: Document data with possible {{placeholder}} values

        Returns:
            Data with placeholders filled
        """
        if "frontmatter" not in data:
            return data

        result = dict(data)
        frontmatter = dict(result["frontmatter"])

        # Build parameter map
        params = dict(frontmatter)

        # Fill placeholders
        for key, value in frontmatter.items():
            if isinstance(value, str):
                frontmatter[key] = self._replace_placeholders(value, params)

        result["frontmatter"] = frontmatter
        return result

    def _replace_placeholders(self, text: str, params: dict[str, Any]) -> str:
        """Replace {{placeholder}} patterns with parameter values.

        Args:
            text: Text with placeholders
            params: Parameter values

        Returns:
            Text with placeholders replaced
        """
        pattern = r"\{\{(\w+)\}\}"

        def replace(match: re.Match[str]) -> str:
            param_name = match.group(1)
            return str(params.get(param_name, match.group(0)))

        return re.sub(pattern, replace, text)

    def _validate(self, data: dict[str, Any], schema: dict[str, Any]) -> None:
        """Validate data against schema.

        Args:
            data: Document data to validate
            schema: Schema to validate against

        Raises:
            ValueError: If validation fails
        """
        # Use existing validation system
        from mddata.schema import SchemaValidator

        validator = SchemaValidator(schema)
        result = validator.validate(data)

        if not result.is_valid:
            errors = "\n".join(f"  - {err}" for err in result.errors)
            raise ValueError(f"Schema validation failed:\n{errors}")
