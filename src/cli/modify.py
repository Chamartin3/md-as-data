"""Modify subcommands for mutating markdown file content."""

import json
from pathlib import Path
from typing import Annotated, Any

import typer

from mddata.models import UpdatePolicy
from mddata.templates.computed import resolve_computed_params
from mddata.templates.engine import load_template, load_template_from_stdin
from mddata.templates.parameters import parse_cli_params
from mddata.templates.substitution import substitute_in_dict, substitute_placeholders
from mddata.utils import JSONDataError, load_json

from .utils import InputParser, MarkdownPrinter, cli_context, section_policy_converter

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


@app.command("from-json")
def from_json(
    file_path: FilePathArg,
    source: Annotated[str, typer.Argument(help="JSON file path or '-' for stdin")],
    dry_run: Annotated[
        bool, typer.Option("--dry-run", "-n", help="Show changes without applying")
    ] = False,
) -> None:
    """Apply changes from JSON file or stdin."""
    md_file = cli_context.load_file_for_command(file_path)
    printer = MarkdownPrinter(cli_context.console)

    try:
        # Load JSON data using centralized loader
        try:
            json_data = load_json(source)
        except JSONDataError as e:
            printer.print_error(str(e))
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


@app.command("from-template")
def from_template(
    file_path: FilePathArg,
    template_path: Annotated[
        str, typer.Argument(help="Template file or '-' for stdin")
    ],
    param: Annotated[
        list[str],
        typer.Option(
            "-p", "--param", help="Parameter (KEY=VALUE, KEY=@file, KEY=-, KEY=@-)"
        ),
    ] = [],
    params_file: Annotated[
        Path | None,
        typer.Option("--params", help="Load all parameters from JSON/YAML file"),
    ] = None,
    format: Annotated[
        str, typer.Option("--format", help="Template format for stdin (yaml|json)")
    ] = "yaml",
    dry_run: Annotated[
        bool, typer.Option("--dry-run", "-n", help="Show changes without applying")
    ] = False,
) -> None:
    """Apply template with parameter substitution."""
    md_file = cli_context.load_file_for_command(file_path)
    printer = MarkdownPrinter(cli_context.console)

    try:
        # Load template
        if template_path == "-":
            template = load_template_from_stdin(format)
        else:
            template = load_template(template_path)

        # Resolve computed parameters
        computed_params = resolve_computed_params(template)

        # Parse CLI parameters
        resolved_params = parse_cli_params(
            param,
            template["parameters"],
            computed_params,
            params_file=str(params_file) if params_file else None,
        )

        # Resolve computed parameters in parameter values
        final_params: dict[str, Any] = {}
        for key, value in resolved_params.items():
            if isinstance(value, str):
                # Substitute computed params in the value
                resolved_value = substitute_placeholders(value, resolved_params)
                final_params[key] = resolved_value
            else:
                final_params[key] = value

        # Substitute placeholders in template changes
        substituted_changes = substitute_in_dict(template["changes"], final_params)

        if dry_run:
            printer.print_success("Dry run - changes not applied")
            printer.print_success("Template changes:")
            print(json.dumps(substituted_changes, indent=2))
            return

        # Apply changes using core functionality
        result = md_file.mddata.apply_batch_changes(substituted_changes)

        # Report warnings
        for warning in result["warnings"]:
            printer.print_warning(warning)

        # Report errors
        for error in result["errors"]:
            printer.print_error(error)

        if result["success"] and result["changes_count"] > 0:
            md_file.save()
            printer.print_success(
                f"Applied template '{template_path}' with "
                f"{result['changes_count']} changes "
                f"({result['frontmatter_changes']} frontmatter, "
                f"{result['section_changes']} sections)"
            )
        elif result["changes_count"] == 0:
            printer.print_warning("No valid changes found in template")
        else:
            printer.print_error("Template application failed")
            raise typer.Exit(1)

    except Exception as e:
        printer.print_error(str(e))
        raise typer.Exit(1)
