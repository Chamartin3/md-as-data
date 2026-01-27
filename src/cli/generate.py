"""Generate command for creating markdown files from structured data."""

from typing import Annotated

import typer

from mddata import MarkdownFile
from mddata.models import MarkdownDataDict
from mddata.models.schemas import DocumentSchema
from mddata.schema import SchemaValidationError, load_schema, validate_schema_structure
from mddata.utils import (
    JSONDataError,
    load_markdown_data_dict,
)

from .utils import (
    CLIError,
    MarkdownPrinter,
    OptionalOutputFileArg,
    cli_context,
    handle_cli_errors,
)


def generate_markdown_file(
    data: MarkdownDataDict | None,
    schema: DocumentSchema | None,
    output_path: str | None,
    force: bool,
) -> tuple[MarkdownFile, str]:
    """Generate markdown file based on provided data and/or schema.

    Args:
        data: JSON data in MarkdownDataDict format (optional)
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
        # Generate from data (with optional schema validation)
        md_file = MarkdownFile.from_dict(data, filepath=output_path, schema=schema)
        source_msg = "data" if not schema else "data (validated against schema)"
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


def load_data_safely(data_path: str | None) -> MarkdownDataDict | None:
    """Load and validate JSON data with error handling.

    Args:
        data_path: Path to data file, '-' for stdin, or None

    Returns:
        Validated MarkdownDataDict or None if no data provided

    Raises:
        CLIError: On any error during data loading
    """
    if not data_path:
        return None

    try:
        return load_markdown_data_dict(data_path)
    except JSONDataError as e:
        raise CLIError(str(e))


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
def generate_command(
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
            help="Path to JSON data file (use '-' for stdin, MarkdownDataDict format)",
        ),
    ] = None,
    output: OptionalOutputFileArg = None,
    force: Annotated[
        bool, typer.Option("--force", "-F", help="Force overwrite existing file")
    ] = False,
) -> None:
    """Generate markdown file from schema template or JSON data.

    You can provide either --schema, --data, or both:

    - --schema: Generate template from schema definition
    - --data: Generate from JSON data (MarkdownDataDict format)
    - Both: Generate from data and validate against schema

    Examples:

        # Generate template from schema
        mddata generate --schema schema.json --output template.md

        # Generate from JSON data
        mddata generate --data data.json --output document.md

        # Generate from stdin
        cat data.json | mddata generate --data - --output document.md

        # Generate from data with schema validation
        mddata generate --data data.json --schema schema.json --output document.md

        # Print to stdout (no --output)
        mddata generate --data data.json
    """
    printer = MarkdownPrinter(cli_context.console)

    # Validate that at least one source is provided
    if not schema and not data:
        raise CLIError(
            "Must provide either --schema or --data (or both)",
            details=[
                "\nExamples:",
                "mddata generate --schema schema.json -o template.md",
                "mddata generate --data data.json -o document.md",
                "mddata generate --data data.json --schema schema.json -o document.md",
            ],
            style="dim",
        )

    # Load schema (single line with error handling via CLIError)
    loaded_schema = load_schema_safely(schema)

    # Load data (single line with error handling via CLIError)
    json_data = load_data_safely(data)

    md_file, source_msg = generate_markdown_file(
        json_data, loaded_schema, output, force
    )
    # If no output path, print to stdout
    if not output:
        markdown_content = md_file.to_markdown()
        print(markdown_content)
        return
    try:
        from_schema = bool(schema and not data)
        save_markdown(md_file, output, source_msg, printer, from_schema)
    except Exception as e:
        raise CLIError(f"Error saving file: {e}")
