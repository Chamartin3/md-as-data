"""Unified write command for creating and modifying markdown files."""

from pathlib import Path
from typing import Annotated, Any

import typer

from mddata.models.schema import DocumentSchema
from mddata.operations import (
    DataStructureError,
    OperationMode,
    OperationResult,
    ParameterValidationError,
    determine_operation_mode,
    load_and_validate_data,
    write_document,
)
from mddata.schema import SchemaValidationError, load_schema, validate_schema_structure

from .utils import (
    CLIError,
    MarkdownPrinter,
    OptionalOutputFileArg,
    cli_context,
    handle_cli_errors,
)


def load_parameters_from_file(params_file: Path | None) -> dict[str, Any]:
    """Load parameters from JSON/YAML file.

    Args:
        params_file: Path to parameter file or None

    Returns:
        Dict of parameter key-value pairs with their original types

    Raises:
        CLIError: On parameter file loading errors
    """
    if not params_file:
        return {}

    try:
        # Load as raw dict preserving original data types
        import json

        import yaml

        with open(params_file) as f:
            if params_file.suffix.lower() in (".yaml", ".yml"):
                data = yaml.safe_load(f)
            else:
                data = json.load(f)

        if not isinstance(data, dict):
            raise CLIError("Parameter file must contain a dictionary")

        # Return with original types preserved (arrays, strings, numbers, etc.)
        return data
    except Exception as e:
        raise CLIError(f"Error loading parameters file: {e}")


def load_schema_safely(schema_path: str | None) -> DocumentSchema | None:
    """Load and validate schema from file.

    Args:
        schema_path: Path to schema file or None

    Returns:
        Loaded schema dict or None

    Raises:
        CLIError: On schema loading/validation errors
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


@handle_cli_errors
def write_command(
    target_file: Annotated[
        Path | None,
        typer.Argument(
            help=(
                "Target file to modify (for modify mode) "
                "or positional argument for data file"
            )
        ),
    ] = None,
    data: Annotated[
        str | None,
        typer.Option(
            "--data", "-d", help="Path to data/template file (use '-' for stdin)"
        ),
    ] = None,
    schema: Annotated[
        str | None,
        typer.Option(
            "--schema",
            "-s",
            help="Path to schema file for validation/template generation",
        ),
    ] = None,
    output: OptionalOutputFileArg = None,
    format: Annotated[
        str,
        typer.Option(
            "--format", "-f", help="Data format: json or yaml (default: auto-detect)"
        ),
    ] = "json",
    param: Annotated[
        list[str],
        typer.Option(
            "-p",
            "--param",
            help="Template parameter (KEY=VALUE format)",
        ),
    ] = [],
    params_file: Annotated[
        Path | None,
        typer.Option("--params", help="Load parameters from JSON/YAML file"),
    ] = None,
    policy: Annotated[
        str,
        typer.Option(
            "--policy",
            help="Merge policy: replace, update, merge, append (default: update)",
        ),
    ] = "update",
    force: Annotated[
        bool, typer.Option("--force", "-F", help="Force overwrite existing files")
    ] = False,
    dry_run: Annotated[
        bool, typer.Option("--dry-run", "-n", help="Preview changes without applying")
    ] = False,
    debug: Annotated[
        bool,
        typer.Option(
            "--debug", help="Show detailed error information and stack traces"
        ),
    ] = False,
) -> None:
    """Write markdown files from data, templates, or schemas.

    Intelligent auto-detection of operation mode:
    - CREATE: Generate new file from data/template/schema
    - MODIFY: Update existing file (when target file exists)
    - SCHEMA_TEMPLATE: Generate template from schema only
    - STDOUT: Render to stdout (no output file specified)

    Examples:

        # Create from data
        mddata write --data document.json --output new.md

        # Modify existing file
        mddata write --data changes.json existing.md

        # Generate template from schema
        mddata write --schema schema.json --output template.md

        # Render to stdout
        mddata write --data document.json

        # With template parameters
        mddata write --data template.yaml -p title="My Doc" --output result.md

        # Dry run to preview
        mddata write --data changes.json existing.md --dry-run
    """
    import logging

    printer = MarkdownPrinter(cli_context.console)

    # Configure logging based on debug flag
    if debug:
        logging.basicConfig(
            level=logging.DEBUG, format="%(levelname)s [%(name)s]: %(message)s"
        )
        printer.console.print("[yellow]Debug mode enabled[/yellow]")
    else:
        logging.basicConfig(level=logging.WARNING)

    # Parse parameters
    parameters = {}
    for param_str in param:
        if "=" not in param_str:
            raise CLIError(f"Invalid parameter format: {param_str} (use KEY=VALUE)")
        key, value = param_str.split("=", 1)
        parameters[key] = value

    # Load additional parameters from file if specified
    file_params = load_parameters_from_file(params_file)
    parameters.update(file_params)

    # Show parameter info in debug mode
    if debug and parameters:
        printer.console.print(
            f"[dim]Loaded parameters: {list(parameters.keys())}[/dim]"
        )

    # Determine operation mode
    operation_mode = determine_operation_mode(data, schema, target_file, output)

    if debug:
        printer.console.print(f"[dim]Operation mode: {operation_mode.value}[/dim]")

    # Auto-detect format from file extension if using default
    if format == "json" and data and data != "-":
        if data.endswith(('.yaml', '.yml')):
            format = "yaml"
            if debug:
                printer.console.print("[dim]Auto-detected format: yaml[/dim]")

    # Load data
    try:
        # Pass parameters for template processing
        params_file_str = str(params_file) if params_file else None
        data_dict, data_update = load_and_validate_data(
            data,
            format,
            cli_params=param,
            params_file=params_file_str,
        )

        # Show data validation info in debug mode
        if debug:
            if data_dict:
                printer.console.print(
                    "[dim]✓ Loaded complete document (MarkdownDataDict)[/dim]"
                )
                if "frontmatter" in data_dict:
                    fm_keys = list(data_dict["frontmatter"].keys())
                    printer.console.print(f"[dim]  Frontmatter keys: {fm_keys}[/dim]")
            elif data_update:
                printer.console.print(
                    "[dim]✓ Loaded template/update (MarkdownDataUpdate)[/dim]"
                )
                if data_update.parameters:
                    param_count = len(data_update.parameters)
                    printer.console.print(
                        f"[dim]  Template parameters: {param_count}[/dim]"
                    )
                    required = [
                        name
                        for name, config in data_update.parameters.items()
                        if isinstance(config, dict) and config.get("required", False)
                    ]
                    if required:
                        printer.console.print(
                            f"[dim]  Required parameters: {required}[/dim]"
                        )
            else:
                printer.console.print("[yellow]Warning: No data loaded[/yellow]")
    except Exception as e:
        details = str(e)
        if debug:
            import traceback

            details = f"{details}\n\n{traceback.format_exc()}"
        raise CLIError(f"Error loading data: {e}", details=details if debug else None)

    # Load schema
    schema_dict = load_schema_safely(schema)

    if debug and schema_dict:
        printer.console.print("[dim]✓ Loaded schema for validation[/dim]")

    # Prepare arguments for write_document
    write_args = {
        "data": data_dict or data_update,
        "schema": schema_dict,
        "operation_mode": operation_mode,
        "parameters": parameters or None,
        "policy": policy,
        "force_overwrite": force,
    }

    # Set file arguments based on mode
    if operation_mode == OperationMode.MODIFY:
        write_args["target_file"] = target_file
    elif operation_mode in (OperationMode.CREATE, OperationMode.SCHEMA_TEMPLATE):
        if not output:
            raise CLIError("Output file required for create/schema_template modes")
        write_args["output_file"] = Path(output)
    # STDOUT mode doesn't need file arguments

    # Dry run mode
    if dry_run:
        _print_dry_run(operation_mode, write_args, printer)
        return

    # Execute operation
    try:
        result = write_document(**write_args)
    except ParameterValidationError as e:
        details = str(e)
        if debug:
            import traceback

            details = f"{details}\n\n{traceback.format_exc()}"
        raise CLIError("Parameter validation failed", details=details)
    except DataStructureError as e:
        details = str(e)
        if debug:
            import traceback

            details = f"{details}\n\n{traceback.format_exc()}"
        raise CLIError("Data structure error", details=details)
    except Exception as e:
        details = str(e)
        if debug:
            import traceback

            details = (
                f"{details}\n\n[bold]Full traceback:[/bold]\n{traceback.format_exc()}"
            )
        raise CLIError(f"Write operation failed: {e}", details=details)

    # Handle result
    if not result.success:
        error_msg = "; ".join(result.errors or ["Unknown error"])
        details = None
        if debug and result.errors:
            details = "\n".join(result.errors)
        raise CLIError(f"Operation failed: {error_msg}", details=details)

    # Report success
    _handle_success(result, operation_mode, printer)


def _print_dry_run(
    operation_mode: OperationMode, args: dict, printer: MarkdownPrinter
) -> None:
    """Print dry run information."""
    printer.console.print("[bold blue]Dry Run Mode[/bold blue]")
    printer.console.print(f"Operation: {operation_mode.value}")

    if operation_mode == OperationMode.MODIFY:
        printer.console.print(f"Target file: {args.get('target_file')}")
    elif operation_mode in (OperationMode.CREATE, OperationMode.SCHEMA_TEMPLATE):
        printer.console.print(f"Output file: {args.get('output_file')}")

    if args.get("data"):
        printer.console.print(f"Data source: {args['data']}")
    if args.get("schema"):
        printer.console.print(f"Schema: {args['schema']}")
    if args.get("parameters"):
        printer.console.print(f"Parameters: {args['parameters']}")

    printer.console.print("\n[yellow]No files will be created or modified[/yellow]")


def _handle_success(
    result: OperationResult, mode: OperationMode, printer: MarkdownPrinter
) -> None:
    """Handle successful operation result."""
    if mode == OperationMode.STDOUT:
        # Print rendered content to stdout
        if result.metadata and "rendered_content" in result.metadata:
            printer.console.print(result.metadata["rendered_content"])
        else:
            printer.print_success("Rendered to stdout")
    elif mode == OperationMode.MODIFY:
        target_file = result.metadata.get("target_file") if result.metadata else None
        printer.print_success(f"Modified file: {target_file}")
    elif mode == OperationMode.CREATE:
        output_file = result.metadata.get("output_file") if result.metadata else None
        printer.print_success(f"Created file: {output_file}")
    elif mode == OperationMode.SCHEMA_TEMPLATE:
        output_file = result.metadata.get("output_file") if result.metadata else None
        printer.print_success(f"Generated template: {output_file}")

    # Print warnings if any
    if result.warnings:
        for warning in result.warnings:
            printer.console.print(f"[yellow]Warning: {warning}[/yellow]")
