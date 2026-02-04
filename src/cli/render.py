"""Render command for creating markdown files from structured data."""

from pathlib import Path
from typing import Annotated, cast

import typer
from rich.markdown import Markdown

from mddata import MarkdownFile
from mddata.models import MarkdownDataDict, MarkdownDataUpdate, MarkdownForm
from mddata.models.schema import DocumentSchema
from mddata.schema import SchemaValidationError, load_schema, validate_schema_structure
from mddata.utils import (
    DataLoadError,
    JSONDataError,
    load_data_update,
    load_markdown_data_dict,
)

from .utils import (
    CLIError,
    MarkdownPrinter,
    OptionalOutputFileArg,
    cli_context,
    data_format_converter,
    handle_cli_errors,
)


def generate_markdown_file(
    data: MarkdownDataDict | None,
    update: MarkdownDataUpdate | None,
    schema: DocumentSchema | None,
    output_path: str | None,
    force: bool,
) -> tuple[MarkdownFile, str]:
    """Generate markdown file based on provided data and/or schema.

    Args:
        data: JSON data in MarkdownDataDict format (optional)
        update: MarkdownDataUpdate with flat sections/template (optional)
        schema: Validated schema dictionary (optional)
        output_path: Output file path (required for schema-only generation)
        force: Whether to overwrite existing files

    Returns:
        Tuple of (generated MarkdownFile, source description message)

    Raises:
        ValueError: If output_path is missing for schema-only generation
        FileExistsError: If output file exists and force=False
    """
    if data:
        # Generate from hierarchical data (with optional schema validation)
        md_file = MarkdownFile.from_dict(data, filepath=output_path, schema=schema)
        source_msg = "data" if not schema else "data (validated against schema)"
        return md_file, source_msg

    if update:
        # Generate from template with flat sections
        # Create minimal empty document
        empty_data: MarkdownDataDict = {
            "frontmatter": {},
            "content": {
                "id": "root",
                "title": "Document",
                "level": 0,
                "path": "",
                "blocks": [],
                "children": [],
            },
        }
        md_file = MarkdownFile.from_dict(
            empty_data, filepath=output_path, schema=schema
        )

        # Apply template updates
        result = md_file.mddata.apply_batch_changes(update)
        if not result["success"]:
            errors = "\n".join(result["errors"])
            raise CLIError(f"Failed to apply template changes:\n{errors}")

        source_msg = "data" if not isinstance(update, MarkdownForm) else "form"
        return md_file, source_msg

    # Generate from schema template
    if not output_path:
        raise CLIError(
            "Output file path (--output) is required when generating from schema"
        )

    md_file = MarkdownFile.create_from_schema(schema, output_path, overwrite=force)
    source_msg = "schema template"
    return md_file, source_msg


def load_schema_safely(schema_path: str | None) -> DocumentSchema | None:
    """Load and validate schema with error handling.

    Args:
        schema_path: Path to schema file or None

    Returns:
        Validated schema or None if no schema provided

    Raises:
        CLIError: On any error during schema loading
    """
    if not schema_path:
        return None

    try:
        schema = load_schema(schema_path)
        validate_schema_structure(schema)
        return schema
    except SchemaValidationError as e:
        raise CLIError("Schema validation failed", details=f"\n{str(e)}\n")
    except Exception as e:
        raise CLIError(f"Error loading schema: {e}")


def load_data_safely(
    data_path: str | None,
    format: str | None = None,
    cli_params: list[str] | None = None,
    params_file: str | None = None,
) -> tuple[MarkdownDataDict | None, MarkdownDataUpdate | None]:
    """Load and validate data with template parameter support.

    This function handles two types of data:
    1. Complete MarkdownDataDict (full document data with hierarchical content)
    2. Templates (MarkdownDataUpdate with flat sections and parameters)

    Args:
        data_path: Path to data file, '-' for stdin, or None
        format: Data format (optional, auto-detected from file extension)
        cli_params: Template parameters in KEY=VALUE format (optional)
        params_file: JSON/YAML file with parameter definitions (optional)

    Returns:
        Tuple of (MarkdownDataDict or None, MarkdownDataUpdate or None)
        - If hierarchical content: (MarkdownDataDict, None)
        - If flat sections/template: (None, MarkdownDataUpdate)

    Raises:
        CLIError: On any error during data loading
    """
    if not data_path:
        return None, None

    data_format = data_format_converter(format)

    try:
        # Try loading as MarkdownDataUpdate (supports both formats)
        update = load_data_update(
            data_path,
            format=data_format,
            cli_params=cli_params or [],
            params_file=params_file,
        )

        # Check if it has hierarchical content or flat sections
        if update.has_hierarchical_content():
            # Convert to MarkdownDataDict for rendering
            return cast(MarkdownDataDict, update.as_markdown_dict()), None
        else:
            # Return as update to be applied to empty document
            return None, update

    except DataLoadError as e:
        # If it's not a template, try as MarkdownDataDict
        try:
            data_dict = load_markdown_data_dict(data_path, format=data_format)
            return data_dict, None
        except (JSONDataError, DataLoadError) as fallback_error:
            raise CLIError(
                f"Failed to load data: {e}\n"
                f"Also tried as MarkdownDataDict: {fallback_error}"
            )
    except Exception as e:
        raise CLIError(f"Unexpected error loading data: {e}")


def save_markdown(
    md_file: MarkdownFile,
    output_path: str,
    source_msg: str,
    printer: MarkdownPrinter,
    from_schema: bool = False,
) -> None:
    """Save markdown file to disk or print to stdout.

    Args:
        md_file: Generated MarkdownFile instance
        output_path: Output file path (None prints to stdout)
        source_msg: Description of generation source
        printer: Printer instance for console output
        from_schema: Whether file was generated from schema (already saved)

    Raises:
        Exception: If file save operation fails
    """
    # Save to file (if not already saved by create_from_schema)
    if not from_schema:
        md_file.save(output_path)

    printer.print_success(f"Generated markdown file: {output_path}")
    printer.console.print(f"  Source: {source_msg}")


# Create a simple function that will be registered directly as a command
# No Typer app nesting needed since this is a standalone command
@handle_cli_errors
def render_command(
    schema: Annotated[
        str | None,
        typer.Option(
            "--schema",
            "-s",
            help="Path to schema file (JSON or YAML) for template generation",
        ),
    ] = None,
    data: Annotated[
        str | None,
        typer.Option(
            "--data",
            "-d",
            help=(
                "Path to data/template file "
                "(use '-' for stdin, supports MarkdownDataDict or templates)"
            ),
        ),
    ] = None,
    format: Annotated[
        str | None,
        typer.Option(
            "--format",
            "-f",
            help="Data format: json or yaml (auto-detected from file extension)",
        ),
    ] = None,
    param: Annotated[
        list[str],
        typer.Option(
            "-p",
            "--param",
            help="Template parameter (KEY=VALUE, KEY=@file, KEY=-, KEY=@-)",
        ),
    ] = [],
    params_file: Annotated[
        Path | None,
        typer.Option("--params", help="Load all parameters from JSON/YAML file"),
    ] = None,
    output: OptionalOutputFileArg = None,
    force: Annotated[
        bool, typer.Option("--force", "-F", help="Force overwrite existing file")
    ] = False,
) -> None:
    """Render markdown file from schema, template, or JSON data.

    You can provide either --schema, --data, or both:

    - --schema: Render template from schema definition
    - --data: Render from data (MarkdownDataDict) or template with parameters
    - Both: Render from data and validate against schema

    Template Parameters:
      If the data file contains a 'parameters' section, you can provide values:
      - Direct value: -p title="My Document"
      - From file: -p content=@content.txt
      - From stdin: -p description=- (interactive) or -p description=@- (piped)
      - From params file: --params params.json

    Examples:

        # Render template from schema
        mddata render --schema schema.json --output template.md

        # Render from JSON data
        mddata render --data data.json --output document.md

        # Render from template with parameters
        mddata render --data template.yaml -p title="My Doc" \\
            -p author=John --output document.md

        # Use parameter file
        mddata render --data template.yaml --params params.json --output document.md

        # Render from stdin
        cat data.json | mddata render --data - --output document.md

        # Render from data with schema validation
        mddata render --data data.json --schema schema.json --output document.md

        # Print to stdout (no --output)
        mddata render --data data.json
    """
    printer = MarkdownPrinter(cli_context.console)

    # Validate that at least one source is provided
    if not schema and not data:
        raise CLIError(
            "Must provide either --schema or --data (or both)",
            details=[
                "\nExamples:",
                "mddata render --schema schema.json -o template.md",
                "mddata render --data data.json -o document.md",
                "mddata render --data data.json --schema schema.json -o document.md",
            ],
            style="dim",
        )

    # Load schema (single line with error handling via CLIError)
    loaded_schema = load_schema_safely(schema)

    # Load data with template parameter support
    json_data, update_data = load_data_safely(
        data,
        format=format,
        cli_params=param if param else None,
        params_file=str(params_file) if params_file else None,
    )

    # TODO: Cattch the valication errors and structural issues and report them nicely
    md_file, source_msg = generate_markdown_file(
        json_data, update_data, loaded_schema, output, force
    )
    # If no output path, print to stdout using Rich markdown formatter
    if not output:
        markdown_content = md_file.to_markdown()
        rendered_markdown = Markdown(markdown_content)
        printer.console.print(rendered_markdown)
        return
    try:
        from_schema = bool(schema and not data)
        save_markdown(md_file, output, source_msg, printer, from_schema)
    except Exception as e:
        raise CLIError(f"Error saving file: {e}")
