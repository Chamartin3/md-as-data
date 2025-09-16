"""Info subcommands for querying markdown file information."""

from typing import Annotated

import typer
from rich.table import Table

from .utils import BlockTypeArg, MarkdownPrinter, cli_context

app = typer.Typer(
    name="info", help="Query information about markdown files", no_args_is_help=False
)

VerboseOpt = Annotated[
    bool, typer.Option("--verbose", "-v", help="Show verbose output")
]


@app.callback(invoke_without_command=True)
def info_default(
    ctx: typer.Context,
    verbose: VerboseOpt = False,
) -> None:
    """Show file information. Default: quick summary.

    Use --help to see other commands.
    """
    if ctx.invoked_subcommand is None:
        # No subcommand specified, run quick-info (summary)
        cli_context.verbose = verbose
        file_path = cli_context.ensure_file_path()
        md_file = cli_context.ensure_file_loaded()

        printer = MarkdownPrinter(cli_context.console)
        printer.print_file_summary(file_path, md_file, verbose)


@app.command("summary")
def summary(verbose: VerboseOpt = False) -> None:
    """Show file summary with basic statistics."""
    cli_context.verbose = verbose
    file_path = cli_context.ensure_file_path()
    md_file = cli_context.ensure_file_loaded()

    printer = MarkdownPrinter(cli_context.console)
    printer.print_file_summary(file_path, md_file, verbose)


@app.command("properties")
def properties(verbose: VerboseOpt = False) -> None:
    """List all frontmatter properties."""
    cli_context.verbose = verbose
    file_path = cli_context.ensure_file_path()
    md_file = cli_context.ensure_file_loaded()

    frontmatter = md_file.mddata.frontmatter
    printer = MarkdownPrinter(cli_context.console)
    printer.print_frontmatter_properties(file_path, frontmatter, verbose)


@app.command("sections")
def sections(
    show_blocks: Annotated[
        bool, typer.Option("--blocks", "-b", help="Show block count for each section")
    ] = False,
    show_paths: Annotated[
        bool, typer.Option("--paths/--no-paths", "-p/-P", help="Show section paths")
    ] = True,
) -> None:
    """List all document sections with hierarchy."""
    file_path = cli_context.ensure_file_path()
    md_file = cli_context.ensure_file_loaded()

    sections = md_file.mddata.get_all_sections()
    printer = MarkdownPrinter(cli_context.console)
    printer.print_document_sections(file_path, sections, show_blocks, show_paths)


@app.command("blocks")
def blocks(
    block_type: BlockTypeArg = None,
    limit: Annotated[
        int | None, typer.Option("--limit", "-l", help="Limit number of blocks shown")
    ] = None,
) -> None:
    """List document blocks with optional filtering."""
    file_path = cli_context.ensure_file_path()
    md_file = cli_context.ensure_file_loaded()

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
    md_file = cli_context.ensure_file_loaded()
    doc = md_file.mddata
    console = cli_context.console

    # Get task lists with optional section filter
    task_lists = doc.get_task_lists(section)

    if not task_lists:
        section_msg = f" in section '{section}'" if section else ""
        console.print(f"[yellow]No task lists found{section_msg}[/yellow]")
        return

    # Apply filters and collect tasks
    all_tasks = []
    for task_list in task_lists:
        for task in task_list.tasks:
            # Apply symbol filter
            if symbol and task["symbol"] != symbol:
                continue

            # Apply completion filter
            is_completed = task["symbol"].lower() == "x"
            if completed is not None and is_completed != completed:
                continue

            if pending and is_completed:
                continue

            all_tasks.append(
                {
                    "content": task["content"],
                    "symbol": task["symbol"],
                    "completed": is_completed,
                }
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
    """Display tasks in compact format."""
    for task in tasks:
        symbol = task["symbol"]
        content = task["content"]

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

        if content_style:
            console.print(
                f"{symbol_display} [{content_style}]{content}[/{content_style}]"
            )
        else:
            console.print(f"{symbol_display} {content}")


def _display_tasks_verbose(tasks: list[dict], console) -> None:
    """Display tasks in detailed table format."""
    table = Table(title="Task List")
    table.add_column("Status", style="cyan")
    table.add_column("Symbol", style="magenta")
    table.add_column("Content")

    for task in tasks:
        symbol = task["symbol"]
        content = task["content"]

        if symbol.lower() == "x":
            status = "[green]Completed[/green]"
        elif symbol == " ":
            status = "[yellow]Pending[/yellow]"
        elif symbol == "!":
            status = "[red]Priority[/red]"
        else:
            status = "[cyan]Custom[/cyan]"

        table.add_row(status, f"[{symbol}]", content)

    console.print(table)
