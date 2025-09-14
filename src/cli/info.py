"""Info subcommands for querying markdown file information."""

from typing import Annotated

import typer

from .utils import MarkdownPrinter, cli_context

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
        file_path = cli_context.file_path
        md_file = cli_context.ensure_file_loaded()

        printer = MarkdownPrinter(cli_context.console)
        printer.print_file_summary(file_path, md_file, verbose)


@app.command("summary")
def summary(verbose: VerboseOpt = False) -> None:
    """Show file summary with basic statistics."""
    cli_context.verbose = verbose
    file_path = cli_context.file_path
    md_file = cli_context.ensure_file_loaded()

    printer = MarkdownPrinter(cli_context.console)
    printer.print_file_summary(file_path, md_file, verbose)


@app.command("properties")
def properties(verbose: VerboseOpt = False) -> None:
    """List all frontmatter properties."""
    cli_context.verbose = verbose
    file_path = cli_context.file_path
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
    file_path = cli_context.file_path
    md_file = cli_context.ensure_file_loaded()

    sections = md_file.mddata.get_all_sections()
    printer = MarkdownPrinter(cli_context.console)
    printer.print_document_sections(file_path, sections, show_blocks, show_paths)


@app.command("blocks")
def blocks(
    block_type: Annotated[
        str | None,
        typer.Option(
            "--type",
            "-t",
            help="Filter by block type (paragraph, list, code_block, etc.)",
        ),
    ] = None,
    limit: Annotated[
        int | None, typer.Option("--limit", "-l", help="Limit number of blocks shown")
    ] = None,
) -> None:
    """List document blocks with optional filtering."""
    file_path = cli_context.file_path
    md_file = cli_context.ensure_file_loaded()

    blocks_data = md_file.mddata.get_blocks()
    all_blocks = blocks_data["blocks"]

    # Filter by type if specified
    if block_type:
        filtered_blocks = [b for b in all_blocks if b["type"] == block_type]
    else:
        filtered_blocks = all_blocks

    # Apply limit if specified
    display_blocks = filtered_blocks[:limit] if limit else filtered_blocks

    printer = MarkdownPrinter(cli_context.console)
    printer.print_document_blocks(
        file_path, display_blocks, block_type, limit, len(all_blocks)
    )
