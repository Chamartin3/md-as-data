"""Dedicated printing callbacks for CLI output operations."""

from collections import Counter
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.syntax import Syntax

from md_as_data import MarkdownDataDict, MarkdownFile
from md_as_data.models import BlockData, Section


class MarkdownPrinter:
    """Handles all markdown file printing operations."""

    def __init__(self, console: Console):
        self.console = console

    def print_file_summary(
        self, file_path: Path, md_file: MarkdownFile, verbose: bool = False
    ) -> None:
        """Print file summary with basic statistics."""
        self.console.print(f"\n[bold]File:[/bold] {file_path}")

        # Frontmatter info
        frontmatter = md_file.mddata.frontmatter
        self.console.print(f"[bold]Frontmatter properties:[/bold] {len(frontmatter)}")

        if frontmatter and verbose:
            for key in list(frontmatter.keys())[:5]:
                value = str(frontmatter[key])[:50]
                self.console.print(f"  • {key}: {value}")
            if len(frontmatter) > 5:
                self.console.print(f"  ... and {len(frontmatter) - 5} more")

        # Content info
        sections_data = md_file.mddata.get_sections()
        blocks_data = md_file.mddata.get_blocks()

        self.console.print(f"[bold]Sections:[/bold] {len(sections_data['sections'])}")
        self.console.print(f"[bold]Total blocks:[/bold] {len(blocks_data['blocks'])}")

        # Block type breakdown
        block_types = Counter(b["type"] for b in blocks_data["blocks"])
        if block_types:
            self.console.print("[bold]Block types:[/bold]")
            for btype, count in block_types.most_common():
                self.console.print(f"  • {btype}: {count}")

    def print_frontmatter_properties(
        self, file_path: Path, frontmatter: dict[str, Any], verbose: bool = False
    ) -> None:
        """Print all frontmatter properties."""
        self.console.print(f"\n[bold]Frontmatter Properties in {file_path}:[/bold]")

        if frontmatter:
            for key, value in frontmatter.items():
                if verbose:
                    value_str = str(value)
                else:
                    value_str = (
                        str(value)[:100] + "..."
                        if len(str(value)) > 100
                        else str(value)
                    )
                self.console.print(f"  [cyan]{key}[/cyan]: {value_str}")
        else:
            self.console.print("  [dim]No frontmatter properties found[/dim]")

    def print_document_sections(
        self,
        file_path: Path,
        sections: list[Section],
        show_blocks: bool = False,
        show_paths: bool = True,
    ) -> None:
        """Print all document sections with hierarchy."""
        self.console.print(f"\n[bold]Sections in {file_path}:[/bold]")

        if sections:
            for section in sections:
                if section.level > 0:  # Skip root
                    indent = "  " * (section.level - 1)

                    if show_paths:
                        # Extract the last part of the path (the ID) for highlighting
                        path_parts = section.path.split(".")
                        if len(path_parts) > 1:
                            path_prefix = ".".join(path_parts[:-1]) + "."
                            highlighted_id = path_parts[-1]
                            path_display = (
                                f"{path_prefix}[bold cyan]{highlighted_id}[/bold cyan]"
                            )
                        else:
                            path_display = f"[bold cyan]{section.path}[/bold cyan]"

                        # Compact format: Title(path)
                        self.console.print(
                            f"{indent}[green]#{section.level}[/green] "
                            f"{section.title} ({path_display})"
                        )
                    else:
                        self.console.print(
                            f"{indent}[green]#{section.level}[/green] {section.title}"
                        )

                    if show_blocks and section.blocks:
                        self.console.print(
                            f"{indent}   [dim]Blocks: {len(section.blocks)}[/dim]"
                        )
        else:
            self.console.print("  [dim]No sections found[/dim]")

    def print_document_blocks(
        self,
        file_path: Path,
        blocks: list[BlockData],
        block_type: str | None = None,
        limit: int | None = None,
        total_count: int | None = None,
    ) -> None:
        """Print document blocks with optional filtering."""
        if block_type:
            self.console.print(
                f"\n[bold]Blocks of type '{block_type}' in {file_path}:[/bold]"
            )
        else:
            self.console.print(f"\n[bold]All blocks in {file_path}:[/bold]")

        if not blocks:
            self.console.print("  [dim]No blocks found[/dim]")
            return

        # Show limit info if applicable
        if limit and total_count and total_count > limit:
            self.console.print(
                f"[dim]Showing first {limit} of {total_count} blocks[/dim]\n"
            )

        for i, block in enumerate(blocks, 1):
            self.console.print(f"[bold]{i}.[/bold] [blue]{block['type']}[/blue]")

            if "content" in block and block["content"]:
                content = (
                    block["content"][:100] + "..."
                    if len(block["content"]) > 100
                    else block["content"]
                )
                self.console.print(f"   {content}")

            if "section_path" in block:
                self.console.print(f"   [dim]Section: {block['section_path']}[/dim]")

            self.console.print()

    def print_json_output(self, data: MarkdownDataDict, pretty: bool = False) -> None:
        """Print data as JSON output."""
        import json

        json_str = json.dumps(data, indent=2)

        if pretty:
            syntax = Syntax(json_str, "json", theme="monokai")
            self.console.print(syntax)
        else:
            print(json_str)

    def print_success(self, message: str) -> None:
        """Print a success message."""
        self.console.print(f"✓ {message}", style="bold green")

    def print_warning(self, message: str) -> None:
        """Print a warning message."""
        self.console.print(f"[yellow]Warning: {message}[/yellow]")

    def print_error(self, message: str) -> None:
        """Print an error message."""
        self.console.print(f"[red]Error: {message}[/red]")
