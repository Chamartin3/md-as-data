"""Modify subcommands for mutating markdown file content."""

from pathlib import Path
from typing import Annotated

import typer

from mddata.models import UpdatePolicy

from .utils import (
    InputParser,
    MarkdownPrinter,
    cli_context,
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


@app.command("task")
def task(
    file_path: FilePathArg,
    action: Annotated[
        str, typer.Argument(help="Action: complete, pending, add, remove")
    ],
    task_ref: Annotated[str, typer.Argument(help="Task reference (UID or index)")],
    section: Annotated[
        str | None,
        typer.Option("--section", "-s", help="Section containing the task list"),
    ] = None,
    content: Annotated[
        str | None,
        typer.Option(
            "--content", "-c", help="Content for new task (required for 'add')"
        ),
    ] = None,
    symbol: Annotated[
        str, typer.Option("--symbol", help="Symbol for new task (default: space)")
    ] = " ",
) -> None:
    """Modify task list items.

    Actions:
      - complete: Mark task as completed
      - pending: Mark task as pending
      - add: Add new task to list
      - remove: Remove task from list

    Task Reference:
      - For complete/pending/remove: UID (preferred) or numeric index
      - For add: Section ID where to add the task

    Examples:
      # Mark task as completed by UID
      mddata doc.md modify task complete A1B2

      # Mark task as completed by index
      mddata doc.md modify task complete 0 --section "sprint_planning"

      # Add new task
      mddata doc.md modify task add "sprint_planning" --content "New task"

      # Remove task
      mddata doc.md modify task remove C3D4
    """
    md_file = cli_context.load_file_for_command(file_path)
    printer = MarkdownPrinter(cli_context.console)

    try:
        # For add action, task_ref is the section ID, so get all task lists
        if action == "add":
            task_lists = md_file.mddata.get_task_lists(None)
        else:
            # For other actions, filter by section if specified
            task_lists = md_file.mddata.get_task_lists(section)

        if not task_lists:
            section_msg = f" in section '{section}'" if section else ""
            printer.print_error(f"No task lists found{section_msg}")
            raise typer.Exit(1)

        # For add action, task_ref is the section ID
        if action == "add":
            if not content:
                printer.print_error("Content is required for 'add' action")
                raise typer.Exit(1)

            section_id = task_ref  # For add, task_ref is the section ID

            # Find task list in the specified section
            target_list = None
            for task_list in task_lists:
                if task_list.block.section == section_id:
                    target_list = task_list
                    break

            if not target_list:
                printer.print_error(f"No task list found in section '{section_id}'")
                raise typer.Exit(1)

            # Add the task
            uid = target_list.add_task(content, symbol)
            md_file.save()
            printer.print_success(f"Added task '{content}' with UID '{uid}'")

        else:
            # For other actions, find the task across all lists
            found = False
            for task_list in task_lists:
                try:
                    if action == "complete":
                        task_list.mark_completed(task_ref)
                        found = True
                    elif action == "pending":
                        task_list.mark_pending(task_ref)
                        found = True
                    elif action == "remove":
                        task_list.remove_task(task_ref)
                        found = True
                    else:
                        printer.print_error(f"Unknown action: {action}")
                        raise typer.Exit(1)

                    if found:
                        md_file.save()
                        printer.print_success(f"Task {action}d successfully")
                        break

                except (ValueError, IndexError):
                    continue  # Try next task list

            if not found:
                printer.print_error(f"Task '{task_ref}' not found")
                raise typer.Exit(1)

    except Exception as e:
        printer.print_error(str(e))
        raise typer.Exit(1)
