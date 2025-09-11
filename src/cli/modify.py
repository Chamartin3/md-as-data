"""Modify subcommands for mutating markdown file content."""

import json
import sys
from pathlib import Path
from typing import Annotated

import typer

from md_as_data.models import SectionPolicy, UpdatePolicy
from .utils import cli_context, MarkdownPrinter, section_policy_converter

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
        # Parse value
        if json_value:
            try:
                parsed_value = json.loads(value)
            except json.JSONDecodeError as e:
                printer.print_error(f"Invalid JSON value: {e}")
                raise typer.Exit(1)
        else:
            # Try to parse as JSON, fallback to string
            try:
                parsed_value = json.loads(value)
            except json.JSONDecodeError:
                parsed_value = value

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

        # Validate section path and handle both existing sections and new subsection creation
        existing_section = md_file.mddata.get_section(section_id)

        if not existing_section:
            # Check if it's a path for creating a new subsection
            if "." in section_id:
                # Split path to check if parent exists
                path_parts = section_id.split(".")
                parent_path = ".".join(path_parts[:-1])
                new_section_id = path_parts[-1]

                parent_section = md_file.mddata.get_section(parent_path)
                if parent_section:
                    # Parent exists - this is a new subsection creation
                    # Calculate the new section level (parent level + 1)
                    new_level = parent_section.level + 1
                    section_title = new_section_id.replace("_", " ").title()

                    if not content.strip().startswith('#'):
                        # Add heading with appropriate level
                        heading_marker = '#' * new_level
                        content = f"{heading_marker} {section_title}\n\n{content}"

                    # Create the section - the underlying system will handle the creation
                    existing_section = None  # Signal that this is a new section
                else:
                    # Parent doesn't exist - invalid path
                    printer.print_error(f"Parent path '{parent_path}' not found for new section '{section_id}'.")
                    printer.print_error("Use 'info sections --paths' to see available section paths.")
                    raise typer.Exit(1)
            else:
                # Check for ambiguous single-word references
                all_sections = md_file.mddata.get_all_sections()
                matching_sections = []

                for section in all_sections:
                    # Check if section_id matches exactly the section ID
                    if section.id == section_id:
                        matching_sections.append(section)
                    # Check if section_id appears as part of the path
                    elif section_id in section.path:
                        matching_sections.append(section)

                if len(matching_sections) > 1:
                    printer.print_error(f"Ambiguous section reference '{section_id}' matches multiple sections:")
                    for section in matching_sections:
                        printer.print_error(f"  - {section.title} (path: {section.path})")
                    printer.print_error("Please use a unique path to identify the section.")
                    raise typer.Exit(1)
                elif len(matching_sections) == 0:
                    printer.print_error(f"Section '{section_id}' not found.")
                    printer.print_error("Use 'info sections --paths' to see available section paths.")
                    raise typer.Exit(1)
                else:
                    existing_section = matching_sections[0]

        # Preserve heading level if content doesn't start with heading
        if existing_section and not content.strip().startswith('#'):
            # If content doesn't start with a heading, add the appropriate heading level
            heading_marker = '#' * existing_section.level
            section_title = existing_section.title
            content = f"{heading_marker} {section_title}\n\n{content}"

        # Apply section operation
        if section_policy == SectionPolicy.APPEND:
            md_file.mddata.append_to_section(section_id, content)
            action = "appended to"
        elif section_policy == SectionPolicy.REPLACE:
            md_file.mddata.replace_section(section_id, content)
            action = "replaced"
        else:  # UPDATE
            md_file.mddata.update_section(section_id, content)
            action = "updated"

        md_file.save()
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
                with open(source_path, "r") as f:
                    json_data = json.load(f)
            except json.JSONDecodeError as e:
                printer.print_error(f"Invalid JSON in file '{source}': {e}")
                raise typer.Exit(1)

        if dry_run:
            printer.print_success(f"Dry run - would apply JSON changes from {source}")
            print(json.dumps(json_data, indent=2))
            return

        # Apply changes
        changes_count = _apply_json_changes(md_file.mddata, json_data, printer)

        if changes_count > 0:
            md_file.save()
            printer.print_success(f"Applied {changes_count} changes from {source}")
        else:
            printer.print_warning("No valid changes found in JSON data")

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


def _apply_json_changes(doc, json_data: dict, printer: MarkdownPrinter) -> int:
    """Apply JSON data changes to document."""
    changes = 0

    # Apply frontmatter updates
    if "frontmatter" in json_data:
        frontmatter_data = json_data["frontmatter"]

        # Check if frontmatter policy is specified
        frontmatter_policy_str = json_data.get("frontmatter_policy", "merge").upper()
        try:
            frontmatter_policy = UpdatePolicy[frontmatter_policy_str]
        except KeyError:
            printer.print_warning(
                f"Invalid frontmatter policy '{frontmatter_policy_str}', using MERGE"
            )
            frontmatter_policy = UpdatePolicy.MERGE

        # Apply frontmatter updates with policy
        doc.update_frontmatter(frontmatter_data, frontmatter_policy)

        # Report each property that was updated
        policy_name = frontmatter_policy.value
        for key in frontmatter_data.keys():
            printer.print_success(f"Set property '{key}' from JSON ({policy_name})")
            changes += 1

    # Apply section updates
    if "sections" in json_data:
        for section_update in json_data["sections"]:
            section_id = section_update["id"]
            content = section_update["content"]
            policy_str = section_update.get("policy", "update").upper()

            try:
                policy_enum = SectionPolicy[policy_str]
            except KeyError:
                printer.print_warning(
                    f"Invalid policy '{policy_str}' for section '{section_id}', using UPDATE"
                )
                policy_enum = SectionPolicy.UPDATE

            if policy_enum == SectionPolicy.APPEND:
                doc.append_to_section(section_id, content)
                action = "appended to"
            elif policy_enum == SectionPolicy.REPLACE:
                doc.replace_section(section_id, content)
                action = "replaced"
            else:
                doc.update_section(section_id, content)
                action = "updated"

            printer.print_success(f"Section '{section_id}' {action} from JSON")
            changes += 1

    return changes
