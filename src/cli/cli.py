"""CLI implementation with Typer."""

import json
from collections import Counter
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.syntax import Syntax

from md_as_data import MarkdownDataDict, MarkdownFile, SectionsData

app = typer.Typer(name="mdasdata", help="Parse markdown files as structured data")
console = Console()


@app.command()
def parse(
    file: Path = typer.Argument(
        ...,
        help="Path to markdown file",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    pretty: bool = typer.Option(
        False,
        "--pretty",
        "-p",
        help="Pretty print JSON output with syntax highlighting",
    ),
    output: Path | None = typer.Option(
        None, "--output", "-o", help="Output file path (default: stdout)"
    ),
    frontmatter_only: bool = typer.Option(
        False, "--frontmatter", help="Extract only frontmatter"
    ),
    sections_only: bool = typer.Option(
        False, "--sections", help="Extract only section titles and structure"
    ),
):
    """Parse a markdown file and output as structured JSON."""
    try:
        # Load and parse file
        md_file = MarkdownFile(str(file))

        # Determine what to output
        if frontmatter_only:
            data: dict[str, Any] | SectionsData | MarkdownDataDict = (
                md_file.mddata.frontmatter
            )
        elif sections_only:
            data = md_file.mddata.get_sections()  # Returns SectionsData
        else:
            data = md_file.mddata.to_dict()

        # Format JSON
        json_str = json.dumps(data, indent=2)

        # Output
        if output:
            output.write_text(json_str)
            console.print(f"✓ Written to {output}", style="green")
        elif pretty:
            syntax = Syntax(json_str, "json", theme="monokai")
            console.print(syntax)
        else:
            print(json_str)

    except FileNotFoundError:
        console.print(f"Error: File '{file}' not found", style="red")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"Error: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def info(
    file: Path = typer.Argument(
        ...,
        help="Path to markdown file",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
):
    """Display summary information about a markdown file."""
    try:
        md_file = MarkdownFile(str(file))

        console.print(f"\n[bold]File:[/bold] {file}")

        # Frontmatter info
        frontmatter = md_file.mddata.frontmatter
        console.print(f"[bold]Frontmatter properties:[/bold] {len(frontmatter)}")
        if frontmatter:
            for key in list(frontmatter.keys())[:5]:
                value = str(frontmatter[key])[:50]
                console.print(f"  • {key}: {value}")
            if len(frontmatter) > 5:
                console.print(f"  ... and {len(frontmatter) - 5} more")

        # Content info
        sections_data = md_file.mddata.get_sections()  # SectionsData
        blocks_data = md_file.mddata.get_blocks()  # BlocksData

        console.print(f"[bold]Sections:[/bold] {len(sections_data['sections'])}")
        console.print(f"[bold]Total blocks:[/bold] {len(blocks_data['blocks'])}")

        # Block type breakdown
        block_types = Counter(b["type"] for b in blocks_data["blocks"])
        if block_types:
            console.print("[bold]Block types:[/bold]")
            for btype, count in block_types.most_common():
                console.print(f"  • {btype}: {count}")

    except Exception as e:
        console.print(f"Error: {e}", style="red")
        raise typer.Exit(1)


def main():
    """CLI entry point."""
    app()


if __name__ == "__main__":
    main()
