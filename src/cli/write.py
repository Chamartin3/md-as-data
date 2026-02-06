"""Unified write command for creating and modifying markdown files."""

from pathlib import Path
from typing import Annotated, Any

import typer
from rich.console import Console

from mddata import MarkdownFile
from mddata.models import MarkdownDataDict
from mddata.operations import OperationMode, write_document
from mddata.utils.data_loader import load_data, load_data_update

VALID_POLICIES = {"merge", "replace", "update", "append"}


# OperationMode imported from mddata.operations


def detect_operation_mode(
    target_file: Path | None,
    output: Path | None,
    data: Path | None,
    form: Path | None,
    schema: Path | None,
) -> OperationMode:
    """Detect operation mode based on provided arguments.

    Args:
        target_file: Target file argument
        output: Output file path
        data: Data file path
        form: Form file path
        schema: Schema file path

    Returns:
        Detected operation mode
    """
    # SCHEMA_TEMPLATE mode: only schema provided
    if schema and not data and not form:
        return OperationMode.SCHEMA_TEMPLATE

    # CREATE mode: output specified
    if output:
        return OperationMode.CREATE

    # MODIFY mode: target file exists
    if target_file and target_file.exists():
        return OperationMode.MODIFY

    # STDOUT mode: no output or target
    return OperationMode.STDOUT


write_app = typer.Typer(help="Write and modify markdown files")


@write_app.command("from")
def write_from(
    target_file: Annotated[
        Path | None,
        typer.Argument(help="Target file to modify (optional)"),
    ] = None,
    # Source flags
    data: Annotated[
        Path | None,
        typer.Option("-d", "--data", help="Data file (JSON/YAML) or '-' for stdin"),
    ] = None,
    form: Annotated[
        Path | None,
        typer.Option("-f", "--form", help="Form/template file (YAML) or '-' for stdin"),
    ] = None,
    schema: Annotated[
        Path | None,
        typer.Option("-s", "--schema", help="Schema file (JSON/YAML)"),
    ] = None,
    # Parameters
    param: Annotated[
        list[str],
        typer.Option("-p", "--param", help="Parameter (KEY=VALUE or KEY=@file)"),
    ] = [],
    params_file: Annotated[
        Path | None,
        typer.Option("--params", help="Parameter file (JSON/YAML)"),
    ] = None,
    # Output
    output: Annotated[
        Path | None,
        typer.Option("-o", "--output", help="Output file path"),
    ] = None,
    policy: Annotated[
        str,
        typer.Option(help="Update policy: merge, replace, update, append"),
    ] = "merge",
    force: Annotated[
        bool,
        typer.Option("--force", "-F", help="Overwrite existing files"),
    ] = False,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", "-n", help="Preview without applying"),
    ] = False,
) -> None:
    """Write markdown from various sources with intelligent resolution.

    Examples:
        # From data
        mddata write from -d document.json -o output.md

        # From form with parameters
        mddata write from -f form.yaml -p title="Hello" -o post.md

        # Form + Data + Schema validation
        mddata write from -f form.yaml -d values.json -s schema.json -o out.md

        # Modify existing file
        mddata write from -d changes.json existing.md

        # Stdin/stdout
        cat data.json | mddata write from -d - -o output.md
    """
    from rich.console import Console

    console = Console()

    # Validate policy
    if policy not in VALID_POLICIES:
        valid_policies_str = ", ".join(sorted(VALID_POLICIES))
        raise typer.BadParameter(
            f"Invalid policy '{policy}'. Must be one of: {valid_policies_str}"
        )

    # Validate input sources - at least one source must be provided
    if not any([data, form, schema]):
        raise typer.BadParameter(
            "At least one source must be provided: --data, --form, or --schema"
        )

    # Load and resolve data based on provided sources
    resolved_data = None

    try:
        # Case 1: Form provided - fill form with parameters from data/CLI/params_file
        if form:
            from mddata.forms import MarkdownFormFiller

            # Load form
            form_source = str(form) if form != Path("-") else "-"
            form_data = load_data_update(source=form_source)

            # Load parameter data if provided
            params_dict = None
            if data:
                data_source = str(data) if data != Path("-") else "-"
                params_dict = load_data(data_source)

            # Fill form with parameters
            filler = MarkdownFormFiller(form_data)
            resolved_data = filler.fill(
                cli_params=param if param else None,
                params_file=str(params_file) if params_file else None,
                params_dict=params_dict,
            )

        # Case 2: Data only (no form) - load data directly
        elif data:
            data_source = str(data) if data != Path("-") else "-"
            resolved_data = load_data_update(
                source=data_source,
                cli_params=param if param else None,
                params_file=str(params_file) if params_file else None,
            )

        # Case 3: Schema only - handled differently in template mode
        elif schema:
            schema_data = load_data(str(schema))
            resolved_data = schema_data

    except Exception as e:
        console.print(f"[red]Error loading/resolving data:[/red] {e}")
        raise typer.Exit(1)

    # Detect operation mode
    mode = detect_operation_mode(
        target_file=target_file,
        output=output,
        data=data,
        form=form,
        schema=schema,
    )

    # Execute based on mode
    try:
        if mode == OperationMode.CREATE:
            if not resolved_data:
                raise typer.BadParameter("Data source required for CREATE mode")
            handle_create_mode(
                output=output,
                data=resolved_data.to_dict()
                if hasattr(resolved_data, "to_dict")
                else resolved_data,
                force=force,
                dry_run=dry_run,
            )

        elif mode == OperationMode.MODIFY:
            if not target_file:
                raise typer.BadParameter("Target file required for MODIFY mode")
            if not resolved_data:
                raise typer.BadParameter("Data source required for MODIFY mode")
            handle_modify_mode(
                target_file=target_file,
                data=resolved_data.to_dict()
                if hasattr(resolved_data, "to_dict")
                else resolved_data,
                policy=policy,
                dry_run=dry_run,
            )

        elif mode == OperationMode.STDOUT:
            if not resolved_data:
                raise typer.BadParameter("Data source required for STDOUT mode")
            handle_stdout_mode(
                data=resolved_data.to_dict()
                if hasattr(resolved_data, "to_dict")
                else resolved_data,
            )

        elif mode == OperationMode.SCHEMA_TEMPLATE:
            if not schema:
                raise typer.BadParameter("Schema required for TEMPLATE mode")
            handle_template_mode(
                schema=resolved_data,
                output=output,
                force=force,
            )

    except (FileExistsError, FileNotFoundError, RuntimeError) as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@write_app.command("set-property")
def set_property(
    file: Annotated[Path, typer.Argument(help="Markdown file to modify")],
    property_name: Annotated[str, typer.Argument(help="Property name")],
    value: Annotated[str, typer.Argument(help="Property value")],
    json_value: Annotated[
        bool, typer.Option("--json", help="Parse value as JSON")
    ] = False,
) -> None:
    """Set frontmatter property.

    Examples:
        # Set string property
        mddata write set-property document.md title "New Title"

        # Set JSON property
        mddata write set-property document.md tags '["tag1", "tag2"]' --json
    """
    import json as json_lib

    from rich.console import Console

    console = Console()

    try:
        # Validate file exists
        if not file.exists():
            raise FileNotFoundError(f"File not found: {file}")

        # Parse value if JSON
        if json_value:
            try:
                parsed_value = json_lib.loads(value)
            except json_lib.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON value: {e}")
        else:
            parsed_value = value

        # Load file
        doc = MarkdownFile(file)

        # Set property
        doc.mddata.frontmatter[property_name] = parsed_value

        # Save file
        doc.save()

        # Display result
        console.print(
            f"[green]Set property:[/green] {property_name} = {parsed_value!r}"
        )
        console.print(f"[green]Saved:[/green] {file}")

    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)

    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@write_app.command("remove-property")
def remove_property(
    file: Annotated[Path, typer.Argument(help="Markdown file to modify")],
    property_name: Annotated[str, typer.Argument(help="Property name to remove")],
) -> None:
    """Remove frontmatter property.

    Examples:
        # Remove a property
        mddata write remove-property document.md draft
    """
    from rich.console import Console

    console = Console()

    try:
        # Validate file exists
        if not file.exists():
            raise FileNotFoundError(f"File not found: {file}")

        # Load file
        doc = MarkdownFile(file)

        # Remove property if it exists
        if property_name in doc.mddata.frontmatter:
            del doc.mddata.frontmatter[property_name]
            doc.save()
            console.print(f"[green]Removed property:[/green] {property_name}")
            console.print(f"[green]Saved:[/green] {file}")
        else:
            console.print(f"[yellow]Property not found:[/yellow] {property_name}")
            console.print(f"[yellow]No changes made to:[/yellow] {file}")

    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@write_app.command("set-section")
def set_section(
    file: Annotated[Path, typer.Argument(help="Markdown file to modify")],
    section_id: Annotated[str, typer.Argument(help="Section ID or path")],
    content: Annotated[str, typer.Argument(help="Section content")],
    policy: Annotated[str, typer.Option("--policy", help="Update policy")] = "update",
) -> None:
    """Set section content with policy-based updates.

    Examples:
        # Update section (merge content)
        mddata write set-section document.md intro "New content"

        # Replace section entirely
        mddata write set-section document.md intro "Replace all" --policy replace

        # Append to section
        mddata write set-section document.md notes "More notes" --policy append

        # Create nested section
        mddata write set-section document.md introduction.overview "Overview text"
    """
    from rich.console import Console

    from mddata.models import UpdatePolicy

    console = Console()

    try:
        # Validate file exists
        if not file.exists():
            raise FileNotFoundError(f"File not found: {file}")

        # Validate policy
        valid_policies = ["update", "replace", "append"]
        if policy not in valid_policies:
            raise ValueError(
                f"Invalid policy: {policy}\nValid policies: {', '.join(valid_policies)}"
            )

        # Load file
        doc = MarkdownFile(file)

        # Convert policy string to enum
        policy_enum = UpdatePolicy[policy.upper()]

        # Set section using SDK method
        doc.mddata.set_section(section_id, content, policy=policy_enum)

        # Save file
        doc.save()

        # Display result
        console.print(f"[green]Set section:[/green] {section_id} (policy: {policy})")
        console.print(f"[green]Saved:[/green] {file}")

    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)

    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@write_app.command("task")
def task(
    file: Annotated[Path, typer.Argument(help="Markdown file to modify")],
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
      mddata write task document.md complete A1B2

      # Mark task as completed by index
      mddata write task document.md complete 0 --section "sprint_planning"

      # Add new task
      mddata write task document.md add "sprint_planning" --content "New task"

      # Remove task
      mddata write task document.md remove C3D4
    """
    from rich.console import Console

    console = Console()

    try:
        # Load file
        md_file = MarkdownFile(file)

        # For add action, task_ref is the section ID, so get all task lists
        if action == "add":
            task_lists = md_file.mddata.get_task_lists(None)
        else:
            # For other actions, filter by section if specified
            task_lists = md_file.mddata.get_task_lists(section)

        if not task_lists:
            section_msg = f" in section '{section}'" if section else ""
            console.print(
                f"[red]Error:[/red] No task lists found{section_msg}", style="bold"
            )
            raise typer.Exit(1)

        # For add action, task_ref is the section ID
        if action == "add":
            if not content:
                console.print(
                    "[red]Error:[/red] Content is required for 'add' action",
                    style="bold",
                )
                raise typer.Exit(1)

            section_id = task_ref  # For add, task_ref is the section ID

            # Find task list in the specified section
            target_list = None
            for task_list in task_lists:
                if task_list.block.section == section_id:
                    target_list = task_list
                    break

            if not target_list:
                console.print(
                    f"[red]Error:[/red] No task list found in section '{section_id}'",
                    style="bold",
                )
                raise typer.Exit(1)

            # Add the task
            uid = target_list.add_task(content, symbol)
            md_file.save()
            console.print(f"[green]Added task:[/green] '{content}' with UID '{uid}'")

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
                        console.print(
                            f"[red]Error:[/red] Unknown action: {action}", style="bold"
                        )
                        raise typer.Exit(1)

                    if found:
                        md_file.save()
                        console.print(f"[green]Task {action}d successfully[/green]")
                        break

                except (ValueError, IndexError):
                    continue  # Try next task list

            if not found:
                console.print(
                    f"[red]Error:[/red] Task '{task_ref}' not found", style="bold"
                )
                raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}", style="bold")
        raise typer.Exit(1)


def handle_create_mode(
    output: Path, data: dict[str, Any], force: bool, dry_run: bool
) -> None:
    """Handle CREATE mode - create new file.

    Args:
        output: Output file path
        data: Resolved document data
        force: Force overwrite existing file
        dry_run: Preview mode without applying

    Raises:
        FileExistsError: If file exists and force=False
    """
    console = Console()

    if output.exists() and not force:
        raise FileExistsError(
            f"Output file already exists: {output}\nUse --force to overwrite"
        )

    if dry_run:
        console.print(f"[yellow]Would create:[/yellow] {output}")
        console.print(data)
        return

    # Use operations module to create the file

    # Convert dict to MarkdownDataDict
    markdown_data = MarkdownDataDict(**data)

    result = write_document(
        data=markdown_data,
        output_file=output,
        operation_mode=OperationMode.CREATE,
        force_overwrite=force,
    )

    if not result.success:
        error_msg = "; ".join(result.errors or ["Unknown error"])
        if "already exists" in error_msg:
            raise FileExistsError(error_msg)
        raise RuntimeError(f"Failed to create file: {error_msg}")

    console.print(f"[green]Created:[/green] {output}")


def handle_modify_mode(
    target_file: Path, data: dict[str, Any], policy: str, dry_run: bool
) -> None:
    """Handle MODIFY mode - modify existing file.

    Args:
        target_file: File to modify
        data: Update data
        policy: Update policy (merge/replace/append)
        dry_run: Preview mode without applying

    Raises:
        FileNotFoundError: If target file doesn't exist
    """
    console = Console()

    if not target_file.exists():
        raise FileNotFoundError(f"Target file not found: {target_file}")

    if dry_run:
        console.print(f"[yellow]Would modify:[/yellow] {target_file}")
        console.print(f"[yellow]Policy:[/yellow] {policy}")
        console.print(data)
        return

    # Use operations module to modify the file
    from mddata.models import MarkdownDataUpdate

    # Convert dict to MarkdownDataUpdate
    update_data = MarkdownDataUpdate.from_dict(data)

    result = write_document(
        data=update_data,
        target_file=target_file,
        operation_mode=OperationMode.MODIFY,
        policy=policy,
    )

    if not result.success:
        error_msg = "; ".join(result.errors or ["Unknown error"])
        raise RuntimeError(f"Failed to modify file: {error_msg}")

    console.print(f"[green]Modified:[/green] {target_file}")


def handle_stdout_mode(data: dict[str, Any]) -> None:
    """Handle STDOUT mode - output to console.

    Args:
        data: Resolved document data
    """
    # Use operations module to render to stdout
    from mddata.models import MarkdownDataDict

    result = write_document(
        data=MarkdownDataDict(**data),
        operation_mode=OperationMode.STDOUT,
    )

    if not result.success:
        error_msg = "; ".join(result.errors or ["Unknown error"])
        raise RuntimeError(f"Failed to render to stdout: {error_msg}")


def handle_template_mode(
    schema: dict[str, Any], output: Path | None, force: bool
) -> None:
    """Handle TEMPLATE mode - generate template from schema.

    Args:
        schema: Schema to generate template from
        output: Output file path (None for stdout)
        force: Force overwrite existing file

    Raises:
        FileExistsError: If file exists and force=False
    """
    console = Console()

    result = write_document(
        schema=schema,
        output_file=output,
        operation_mode=OperationMode.SCHEMA_TEMPLATE,
        force_overwrite=force,
    )

    if not result.success:
        error_msg = "; ".join(result.errors or ["Unknown error"])
        if "already exists" in error_msg:
            raise FileExistsError(error_msg)
        raise RuntimeError(f"Failed to create template: {error_msg}")

    if output:
        console.print(f"[green]Created template:[/green] {output}")
    # For stdout, write_document already printed the result
