"""Main CLI application with proper Typer subcommand structure."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from . import export, info, modify
from .utils import MarkdownFileArg, cli_context

app = typer.Typer(
    name="mdasdata",
    help="Parse and manipulate markdown files as structured data",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

# Add subcommands
app.add_typer(info.app, name="info")
app.add_typer(modify.app, name="modify")
app.add_typer(export.app, name="export")

console = Console()


@app.callback()
def main(
    file_path: Annotated[Path, typer.Argument(help="Path to the markdown file")],
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="Enable verbose output")
    ] = False,
    version: Annotated[bool, typer.Option("--version", help="Show version")] = False,
) -> None:
    """
    Parse and manipulate markdown files as structured data.

    [bold]Examples:[/bold]

    [dim]# Get file information (default: quick summary)[/dim]
    mdasdata document.md info
    mdasdata document.md info --verbose

    [dim]# List sections and properties[/dim]
    mdasdata document.md info sections --blocks
    mdasdata document.md info properties

    [dim]# Modify content[/dim]
    mdasdata document.md modify set-property title "New Title"
    mdasdata document.md modify set-section intro "New content" --policy replace

    [dim]# Export data[/dim]
    mdasdata document.md export json --pretty
    mdasdata document.md export frontmatter --format yaml
    """
    if version:
        console.print("mdasdata 1.0.0")
        raise typer.Exit()

    # Set global context
    cli_context.verbose = verbose
    cli_context.load_file(file_path)


@app.command("quick-info")
def quick_info() -> None:
    """Quick file information (shortcut for info summary)."""
    file_path = cli_context.file_path
    md_file = cli_context.ensure_file_loaded()

    from .utils import MarkdownPrinter

    printer = MarkdownPrinter(cli_context.console)
    printer.print_file_summary(file_path, md_file, verbose=False)


@app.command("help-examples")
def help_examples() -> None:
    """Show detailed usage examples."""
    console.print("\n[bold]mdasdata - Markdown as Structured Data[/bold]\n")

    console.print("[bold]INFORMATION COMMANDS[/bold]")
    console.print("  mdasdata document.md info                   # Quick file overview (default)")
    console.print("  mdasdata document.md info --verbose         # Detailed file overview")
    console.print("  mdasdata document.md info properties -v     # List all frontmatter")
    console.print(
        "  mdasdata document.md info sections -b -p    # Sections with blocks/paths"
    )
    console.print(
        "  mdasdata document.md info blocks -t paragraph -l 5  # Filter blocks"
    )
    console.print("  mdasdata document.md quick-info             # Same as info (shortcut)\n")

    console.print("[bold]MODIFICATION COMMANDS[/bold]")
    console.print("  mdasdata modify set-property document.md title 'New Title'")
    console.print(
        "  mdasdata modify set-section document.md intro 'Content' -p replace"
    )
    console.print("  mdasdata modify from-json document.md changes.json")
    console.print("  mdasdata modify remove-property document.md draft\n")

    console.print("[bold]EXPORT COMMANDS[/bold]")
    console.print("  mdasdata export json document.md --pretty")
    console.print("  mdasdata export yaml document.md -o data.yaml")
    console.print("  mdasdata export frontmatter document.md -f json\n")

    console.print("[bold]POLICY OPTIONS (for sections)[/bold]")
    console.print("  -p replace (r)    # Replace entire section")
    console.print("  -p update (u)     # Update preserving subsections")
    console.print("  -p append (a)     # Add content without removing\n")


def main_cli():
    """Entry point for the CLI application."""
    app()


if __name__ == "__main__":
    main_cli()
