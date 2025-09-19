"""Main CLI application with proper Typer subcommand structure."""

from typing import Annotated

import typer
from rich.console import Console

from . import extract, generate, info, modify, schema
from .utils import cli_context

app = typer.Typer(
    name="mdasdata",
    help="Parse and manipulate markdown files as structured data",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

# Add subcommands that require file_path
app.add_typer(info.app, name="info")
app.add_typer(modify.app, name="modify")
app.add_typer(extract.app, name="extract")
app.add_typer(schema.app, name="schema")

# Register generate command at root level (doesn't use file_path argument)
app.command(name="generate")(generate.generate_command)

console = Console()


@app.callback()
def main(
    ctx: typer.Context,
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="Enable verbose output")
    ] = False,
    version: Annotated[bool, typer.Option("--version", help="Show version")] = False,
) -> None:
    """
    Parse and manipulate markdown files as structured data.

    [bold]Examples:[/bold]

    [dim]# Get file information[/dim]
    mdasdata document.md info
    mdasdata document.md info --verbose

    [dim]# List sections and properties[/dim]
    mdasdata document.md info sections --blocks
    mdasdata document.md info properties

    [dim]# Modify content[/dim]
    mdasdata document.md modify set-property title "New Title"
    mdasdata document.md modify set-section intro "New content" --policy replace

    [dim]# Extract data[/dim]
    mdasdata document.md extract json --pretty
    mdasdata document.md extract frontmatter --format yaml

    [dim]# Generate markdown from schema or data (use - as placeholder)[/dim]
    mdasdata - generate --data data.json --output document.md
    mdasdata - generate --schema schema.json --output template.md
    """
    if version:
        console.print("mdasdata 1.0.0")
        raise typer.Exit()

    # Set global context
    cli_context.verbose = verbose


def main_cli():
    """Entry point for the CLI application."""
    app()


if __name__ == "__main__":
    main_cli()
