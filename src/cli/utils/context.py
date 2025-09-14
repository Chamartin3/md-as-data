"""CLI context and shared utilities for mdasdata CLI application."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from md_as_data import MarkdownFile


class CLIContext:
    """Shared context for CLI operations."""

    def __init__(self):
        self.console = Console()
        self.file_path: Path | None = None
        self.md_file: MarkdownFile | None = None
        self.verbose: bool = False

    def load_file(self, file_path: Path) -> None:
        """Load a markdown file and store in context."""
        if not file_path.exists():
            self.console.print(f"[red]Error: File '{file_path}' does not exist[/red]")
            raise typer.Exit(1)

        if not file_path.is_file():
            self.console.print(f"[red]Error: '{file_path}' is not a file[/red]")
            raise typer.Exit(1)

        try:
            self.file_path = file_path
            self.md_file = MarkdownFile(str(file_path))
            if self.verbose:
                self.console.print(f"[dim]Loaded file: {file_path}[/dim]")
        except Exception as e:
            self.console.print(f"[red]Error loading file '{file_path}': {e}[/red]")
            raise typer.Exit(1)

    def ensure_file_loaded(self) -> MarkdownFile:
        """Ensure a file is loaded and return it."""
        if self.md_file is None:
            self.console.print("[red]Error: No file loaded[/red]")
            raise typer.Exit(1)
        return self.md_file

    def print_success(self, message: str) -> None:
        """Print a success message."""
        self.console.print(f"✓ {message}", style="bold green")

    def print_warning(self, message: str) -> None:
        """Print a warning message."""
        self.console.print(f"[yellow]Warning: {message}[/yellow]")

    def print_error(self, message: str) -> None:
        """Print an error message."""
        self.console.print(f"[red]Error: {message}[/red]")


# Global context instance
cli_context = CLIContext()
