"""Modify subcommands for mutating markdown file content."""

import json
import sys
from pathlib import Path
from typing import Annotated

import typer

from md_as_data.models import SectionPolicy

from .utils import InputParser, MarkdownPrinter, cli_context, section_policy_converter

app = typer.Typer(
    name="modify",
    help="Modify markdown file content and properties",
    no_args_is_help=True,
)


@app.command("set-property")
def set_property(
    key: Annotated[str, typer.Argument(help="Property key to set")],
    value: Annotated[
        str, typer.Argument(help="Property value to set (JSON or string)")
    ],
    json_value: Annotated[
        bool, typer.Option("--json", "-j", help="Parse value as JSON")
    ] = False,
) -> None:
    """Set a frontmatter property."""
    md_file = cli_context.ensure_file_loaded()
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
    md_file = cli_context.ensure_file_loaded()
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
        if section_policy == SectionPolicy.APPEND:
            action = "appended to"
        elif section_policy == SectionPolicy.REPLACE:
            action = "replaced"
        else:  # UPDATE
            action = "updated"

        printer.print_success(f"Section '{section_id}' {action}")

    except Exception as e:
        printer.print_error(str(e))
        raise typer.Exit(1)


@app.command("from-json")
def from_json(
    source: Annotated[str, typer.Argument(help="JSON file path or '-' for stdin")],
    dry_run: Annotated[
        bool, typer.Option("--dry-run", "-n", help="Show changes without applying")
    ] = False,
) -> None:
    """Apply changes from JSON file or stdin."""
    md_file = cli_context.ensure_file_loaded()
    printer = MarkdownPrinter(cli_context.console)

    try:
        # Load JSON data
        if source == "-":
            try:
                json_data = json.load(sys.stdin)
            except json.JSONDecodeError as e:
                printer.print_error(f"Invalid JSON from stdin: {e}")
                raise typer.Exit(1)
        else:
            source_path = Path(source)
            if not source_path.exists():
                printer.print_error(f"JSON file '{source}' not found")
                raise typer.Exit(1)

            try:
                with open(source_path) as f:
                    json_data = json.load(f)
            except json.JSONDecodeError as e:
                printer.print_error(f"Invalid JSON in file '{source}': {e}")
                raise typer.Exit(1)

        if dry_run:
            printer.print_success(f"Dry run - would apply JSON changes from {source}")
            print(json.dumps(json_data, indent=2))
            return

        # Apply changes using core functionality
        result = md_file.mddata.apply_batch_changes(json_data)

        # Report warnings
        for warning in result["warnings"]:
            printer.print_warning(warning)

        # Report errors
        for error in result["errors"]:
            printer.print_error(error)

        if result["success"] and result["changes_count"] > 0:
            md_file.save()
            printer.print_success(
                f"Applied {result['changes_count']} changes from {source} "
                f"({result['frontmatter_changes']} frontmatter, "
                f"{result['section_changes']} sections)"
            )
        elif result["changes_count"] == 0:
            printer.print_warning("No valid changes found in JSON data")
        else:
            printer.print_error("Batch operation failed")
            raise typer.Exit(1)

    except Exception as e:
        printer.print_error(str(e))
        raise typer.Exit(1)


@app.command("remove-property")
def remove_property(
    key: Annotated[str, typer.Argument(help="Property key to remove")],
) -> None:
    """Remove a frontmatter property."""
    md_file = cli_context.ensure_file_loaded()
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
