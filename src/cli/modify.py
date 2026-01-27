"""Modify subcommands for mutating markdown file content."""

import json
from pathlib import Path
from typing import Annotated

import typer

from mddata.models import UpdatePolicy
from mddata.utils import DataLoadError, load_data_update

from .utils import (
    InputParser,
    MarkdownPrinter,
    cli_context,
    data_format_converter,
    section_policy_converter,
)

app = typer.Typer(
    name="modify",
    help="Modify markdown file content and properties",
    no_args_is_help=True,
)

FilePathArg = Annotated[Path, typer.Argument(help="Path to the markdown file")]


@app.command("set-property")
def set_property(
    file_path: FilePathArg,
    key: Annotated[str, typer.Argument(help="Property key to set")],
    value: Annotated[
        str, typer.Argument(help="Property value to set (JSON or string)")
    ],
    json_value: Annotated[
        bool, typer.Option("--json", "-j", help="Parse value as JSON")
    ] = False,
) -> None:
    """Set a frontmatter property."""
    md_file = cli_context.load_file_for_command(file_path)
    printer = MarkdownPrinter(cli_context.console)

    try:
        # Parse value using core functionality
        if json_value:
            # Force JSON parsing
            try:
                parsed_value = InputParser.parse_value_strict(value)
            except ValueError as e:
                printer.print_error(str(e))
                raise typer.Exit(1)
        else:
            # Auto-parse with fallback to string
            parsed_value = InputParser.parse_value_auto(value)

        # Set property
        setattr(md_file.mddata, key, parsed_value)
        md_file.save()

        printer.print_success(f"Set property '{key}' = {parsed_value}")
    except Exception as e:
        printer.print_error(str(e))
        raise typer.Exit(1)


@app.command("set-section")
def set_section(
    file_path: FilePathArg,
    section_id: Annotated[str, typer.Argument(help="Section ID or path to modify")],
    content: Annotated[str, typer.Argument(help="New section content")],
    policy: Annotated[
        str,
        typer.Option(
            "--policy", "-p", help="Section policy: replace (r), append (a), update (u)"
        ),
    ] = "update",
) -> None:
    """Set section content with specified policy."""
    md_file = cli_context.load_file_for_command(file_path)
    printer = MarkdownPrinter(cli_context.console)

    try:
        # Parse policy using converter
        section_policy = section_policy_converter(policy)

        # Query section with comprehensive validation
        query = md_file.mddata.query_section(section_id)

        if query.error:
            printer.print_error(query.error)
            if len(query.matched) > 1:
                # Ambiguous reference
                printer.print_error("Matching sections:")
                for section in query.matched:
                    printer.print_error(f"  - {section.title} (path: {section.path})")
                printer.print_error("Please use a unique path to identify the section.")
            else:
                printer.print_error(
                    "Use 'info sections --paths' to see available section paths."
                )
            raise typer.Exit(1)

        # All section creation/update logic is handled by the core
        # Just pass the section_id and content with the policy
        md_file.mddata.set_section(section_id, content, policy=section_policy)

        md_file.save()

        # Determine action for success message
        if section_policy == UpdatePolicy.APPEND:
            action = "appended to"
        elif section_policy == UpdatePolicy.REPLACE:
            action = "replaced"
        else:  # UPDATE
            action = "updated"

        printer.print_success(f"Section '{section_id}' {action}")

    except Exception as e:
        printer.print_error(str(e))
        raise typer.Exit(1)


@app.command("remove-property")
def remove_property(
    file_path: FilePathArg,
    key: Annotated[str, typer.Argument(help="Property key to remove")],
) -> None:
    """Remove a frontmatter property."""
    md_file = cli_context.load_file_for_command(file_path)
    printer = MarkdownPrinter(cli_context.console)

    try:
        frontmatter = md_file.mddata.frontmatter

        if key not in frontmatter:
            printer.print_warning(f"Property '{key}' not found")
            return

        # Remove property directly from frontmatter dictionary
        del frontmatter[key]
        md_file.save()

        printer.print_success(f"Removed property '{key}'")

    except Exception as e:
        printer.print_error(str(e))
        raise typer.Exit(1)


@app.command("from-data")
def from_data(
    file_path: FilePathArg,
    source: Annotated[str, typer.Argument(help="Data file path or '-' for stdin")],
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
    dry_run: Annotated[
        bool, typer.Option("--dry-run", "-n", help="Show changes without applying")
    ] = False,
) -> None:
    """Apply changes from JSON/YAML file or template with unified interface.

    This command replaces both 'from-json' and 'from-template' with a single
    unified interface that auto-detects the data format and handles templates
    with parameter substitution when applicable.

    Data Formats:
      - JSON batch changes (MarkdownDataUpdate format)
      - YAML template files with optional parameters
      - Auto-detection based on file extension (.json, .yaml, .yml)
      - Override auto-detection with --format option

    Template Parameters:
      If the data file contains a 'parameters' section, you can provide values:
      - Direct value: -p title="My Document"
      - From file: -p content=@content.txt
      - From stdin: -p description=- (interactive) or -p description=@- (piped)
      - From params file: --params params.json

    Examples:
      # Apply JSON batch changes (auto-detected)
      mddata modify from-data doc.md changes.json

      # Apply YAML template with parameters (auto-detected)
      mddata modify from-data doc.md template.yaml -p title="My Doc" -p author=John

      # Load from stdin with explicit format
      cat changes.json | mddata modify from-data doc.md - --format json

      # Override auto-detection
      mddata modify from-data doc.md data.txt --format yaml

      # Use parameter file
      mddata modify from-data doc.md template.yaml --params params.json
    """
    md_file = cli_context.load_file_for_command(file_path)
    printer = MarkdownPrinter(cli_context.console)

    try:
        # Load data using unified loader
        try:
            # Convert string format to DataFormat enum
            data_format = data_format_converter(format)
            update = load_data_update(
                source,
                format=data_format,
                cli_params=param if param else None,
                params_file=str(params_file) if params_file else None,
            )
        except DataLoadError as e:
            printer.print_error(str(e))
            raise typer.Exit(1)

        if dry_run:
            source_name = "stdin" if source == "-" else source
            printer.print_success(f"Dry run - would apply changes from {source_name}")
            print(json.dumps(update.to_dict(), indent=2))
            return

        # Apply changes using core functionality
        result = md_file.mddata.apply_batch_changes(update.to_dict())

        # Report warnings
        for warning in result["warnings"]:
            printer.print_warning(warning)

        # Report errors
        for error in result["errors"]:
            printer.print_error(error)

        if result["success"] and result["changes_count"] > 0:
            md_file.save()
            source_name = "stdin" if source == "-" else source
            printer.print_success(
                f"Applied {result['changes_count']} changes from {source_name} "
                f"({result['frontmatter_changes']} frontmatter, "
                f"{result['section_changes']} sections)"
            )
        elif result["changes_count"] == 0:
            printer.print_warning("No valid changes found in data")
        else:
            printer.print_error("Operation failed")
            raise typer.Exit(1)

    except Exception as e:
        printer.print_error(str(e))
        raise typer.Exit(1)
