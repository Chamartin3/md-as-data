"""Main CLI application with proper Typer subcommand structure."""

from typing import Annotated

import typer
from rich.console import Console

from . import extract, info, schema, write
from .utils import cli_context

app = typer.Typer(
    name="mdasdata",
    help="Parse and manipulate markdown files as structured data",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

# Add subcommands that require file_path
app.add_typer(info.app, name="info")
app.add_typer(extract.app, name="extract")
app.add_typer(schema.app, name="schema")

# Add write command group
app.add_typer(write.write_app, name="write", help="Write and modify markdown files")

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
    mdasdata info summary document.md
    mdasdata info sections document.md --blocks
    mdasdata info properties document.md

    [dim]# Write and modify documents[/dim]
    mdasdata write from -d data.json -o document.md
    mdasdata write set-property document.md title "New Title"
    mdasdata write set-section document.md intro "New content" --policy replace

    [dim]# Extract data[/dim]
    mdasdata extract json document.md --pretty
    mdasdata extract frontmatter document.md --format yaml

    [dim]# Schema operations[/dim]
    mdasdata schema infer document.md --output schema.json
    mdasdata schema validate document.md schema.json
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
