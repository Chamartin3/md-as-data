"""Info subcommands for querying markdown file information."""

from pathlib import Path
from typing import Annotated

import typer
from rich.table import Table

from .utils import BlockTypeArg, MarkdownPrinter, cli_context

app = typer.Typer(
    name="info", help="Query information about markdown files", no_args_is_help=True
)

VerboseOpt = Annotated[
    bool, typer.Option("--verbose", "-v", help="Show verbose output")
]
FilePathArg = Annotated[Path, typer.Argument(help="Path to the markdown file")]


@app.callback()
def info_callback(
    ctx: typer.Context,
) -> None:
    """Show file information.

    Use --help to see available commands.
    """
    # Just a placeholder callback - file_path is handled by individual commands
    pass


@app.command("summary")
def summary(file_path: FilePathArg, verbose: VerboseOpt = False) -> None:
    """Show file summary with basic statistics."""
    cli_context.verbose = verbose
    md_file = cli_context.load_file_for_command(file_path)

    printer = MarkdownPrinter(cli_context.console)
    printer.print_file_summary(file_path, md_file, verbose)


@app.command("properties")
def properties(file_path: FilePathArg, verbose: VerboseOpt = False) -> None:
    """List all frontmatter properties."""
    cli_context.verbose = verbose
    md_file = cli_context.load_file_for_command(file_path)

    frontmatter = md_file.mddata.frontmatter
    printer = MarkdownPrinter(cli_context.console)
    printer.print_frontmatter_properties(file_path, frontmatter, verbose)


@app.command("sections")
def sections(
    file_path: FilePathArg,
    show_blocks: Annotated[
        bool, typer.Option("--blocks", "-b", help="Show block count for each section")
    ] = False,
    show_paths: Annotated[
        bool, typer.Option("--paths/--no-paths", "-p/-P", help="Show section paths")
    ] = True,
) -> None:
    """List all document sections with hierarchy."""
    md_file = cli_context.load_file_for_command(file_path)

    sections = md_file.mddata.get_all_sections()
    printer = MarkdownPrinter(cli_context.console)
    printer.print_document_sections(file_path, sections, show_blocks, show_paths)


@app.command("blocks")
def blocks(
    file_path: FilePathArg,
    block_type: BlockTypeArg = None,
    limit: Annotated[
        int | None, typer.Option("--limit", "-l", help="Limit number of blocks shown")
    ] = None,
) -> None:
    """List document blocks with optional filtering."""
    md_file = cli_context.load_file_for_command(file_path)

    # Get filtered blocks using core functionality
    result = md_file.mddata.find_blocks(
        block_type=block_type.value if block_type else None
    )

    # Apply CLI-level limit if specified (presentation layer concern)
    display_blocks = result.blocks[:limit] if limit else result.blocks

    printer = MarkdownPrinter(cli_context.console)
    printer.print_document_blocks(
        file_path,
        [b.to_dict() for b in display_blocks],
        block_type.value if block_type else None,
        limit,
        result.total,
    )


@app.command("tasks")
def tasks(
    file_path: FilePathArg,
    section: Annotated[
        str | None,
        typer.Option("--section", "-s", help="Filter tasks by section"),
    ] = None,
    symbol: Annotated[
        str | None,
        typer.Option("--symbol", help="Filter by specific checkbox symbol"),
    ] = None,
    completed: Annotated[
        bool | None,
        typer.Option("--completed", help="Filter by completion status"),
    ] = None,
    pending: Annotated[
        bool | None,
        typer.Option("--pending", help="Show only pending tasks"),
    ] = None,
    verbose: VerboseOpt = False,
) -> None:
    """Display task list information from document.

    Examples:
        mdasdata doc.md info tasks
        mdasdata doc.md info tasks --section "sprint_planning"
        mdasdata doc.md info tasks --symbol "x"
        mdasdata doc.md info tasks --completed
        mdasdata doc.md info tasks --pending
    """
    md_file = cli_context.load_file_for_command(file_path)
    doc = md_file.mddata
    console = cli_context.console

    # Get task lists with optional section filter
    task_lists = doc.get_task_lists(section)

    if not task_lists:
        section_msg = f" in section '{section}'" if section else ""
        console.print(f"[yellow]No task lists found{section_msg}[/yellow]")
        return

    # Apply filters and collect tasks (including subtasks)
    all_tasks = []
    for task_list in task_lists:
        _collect_tasks_hierarchical(
            task_list.tasks, "", symbol, completed, pending, all_tasks
        )

    if not all_tasks:
        console.print("[yellow]No tasks match the specified filters[/yellow]")
        return

    # Display results
    if verbose:
        _display_tasks_verbose(all_tasks, console)
    else:
        _display_tasks_compact(all_tasks, console)

    # Summary
    completed_count = sum(1 for t in all_tasks if t["completed"])
    pending_count = len(all_tasks) - completed_count
    console.print(
        f"\n[bold]Total:[/bold] {len(all_tasks)} tasks "
        f"([green]{completed_count} completed[/green], "
        f"[yellow]{pending_count} pending[/yellow])"
    )


def _display_tasks_compact(tasks: list[dict], console) -> None:
    """Display tasks in compact format with hierarchical indentation."""
    for task in tasks:
        symbol = task["symbol"]
        content = task["content"]
        uid = task.get("uid", "")
        level = task.get("level", 0)

        # Style based on symbol
        if symbol.lower() == "x":
            symbol_display = "[green]✓[/green]"
            content_style = "dim"
        elif symbol == " ":
            symbol_display = "[yellow]○[/yellow]"
            content_style = None
        elif symbol == "!":
            symbol_display = "[red]![/red]"
            content_style = "bold"
        else:
            symbol_display = f"[cyan][{symbol}][/cyan]"
            content_style = None

        # Add indentation for subtasks
        indent = "  " * level
        uid_display = f"[blue]{uid}[/blue]" if uid else ""

        if content_style:
            content_fmt = f"[{content_style}]{content}[/{content_style}]"
            console.print(f"{indent}{symbol_display} {uid_display} {content_fmt}")
        else:
            console.print(f"{indent}{symbol_display} {uid_display} {content}")


def _display_tasks_verbose(tasks: list[dict], console) -> None:
    """Display tasks in detailed table format with hierarchical indentation."""
    table = Table(title="Task List")
    table.add_column("UID", style="blue")
    table.add_column("Status", style="cyan")
    table.add_column("Symbol", style="magenta")
    table.add_column("Content")

    for task in tasks:
        symbol = task["symbol"]
        content = task["content"]
        uid = task.get("uid", "")
        level = task.get("level", 0)

        if symbol.lower() == "x":
            status = "[green]Completed[/green]"
        elif symbol == " ":
            status = "[yellow]Pending[/yellow]"
        elif symbol == "!":
            status = "[red]Priority[/red]"
        else:
            status = "[cyan]Custom[/cyan]"

        # Add indentation for subtasks
        indent = "  " * level
        indented_content = f"{indent}{content}" if level > 0 else content

        table.add_row(uid, status, f"[{symbol}]", indented_content)

    console.print(table)


def _collect_tasks_hierarchical(
    tasks: list[dict],
    parent_uid: str,
    symbol_filter: str | None,
    completed_filter: bool | None,
    pending_filter: bool | None,
    result: list[dict],
    level: int = 0,
) -> None:
    """Recursively collect tasks with hierarchical UIDs."""
    for task in tasks:
        # Apply symbol filter
        if symbol_filter and task["symbol"] != symbol_filter:
            continue

        # Apply completion filter
        is_completed = task["symbol"].lower() == "x"
        if completed_filter is not None and is_completed != completed_filter:
            continue

        if pending_filter and is_completed:
            continue

        # Build hierarchical UID
        task_uid = task.get("uid", "")
        hierarchical_uid = f"{parent_uid}.{task_uid}" if parent_uid else task_uid

        result.append(
            {
                "content": task["content"],
                "symbol": task["symbol"],
                "completed": is_completed,
                "uid": hierarchical_uid,
                "level": level,  # Indentation level for display
            }
        )

        # Recursively collect subtasks
        if "subtasks" in task:
            _collect_tasks_hierarchical(
                task["subtasks"],
                hierarchical_uid,
                symbol_filter,
                completed_filter,
                pending_filter,
                result,
                level + 1,
            )
