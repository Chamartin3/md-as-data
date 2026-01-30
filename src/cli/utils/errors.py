"""CLI error handling utilities."""

import traceback
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from typing import Any, TypeVar

import typer

from .context import cli_context
from .printers import MarkdownPrinter

F = TypeVar("F", bound=Callable)


@dataclass
class ErrorContext:
    """Enhanced error context for debugging.

    Provides detailed information about where an error occurred and what
    was being attempted, making it easier to diagnose issues.
    """

    source_file: str
    line_number: int
    function_name: str
    operation: str | None = None
    variable_name: str | None = None
    variable_value: Any = None
    hint: str | None = None

    def format(self, include_traceback: bool = False) -> str:
        """Format as user-friendly error message.

        Args:
            include_traceback: Whether to include full traceback

        Returns:
            Formatted error message string
        """
        lines = [
            "\n[bold red]Error Location:[/bold red]",
            f"  Source: {self.source_file}:{self.line_number}",
            f"  Function: {self.function_name}()",
        ]

        if self.operation:
            lines.append(f"  Operation: {self.operation}")

        if self.variable_name:
            lines.append(f"  Variable: {self.variable_name}")

            # Show variable value if it's a simple type
            if self.variable_value is not None:
                if isinstance(self.variable_value, (str, int, float, bool)):
                    lines.append(f"  Value: {self.variable_value}")
                else:
                    lines.append(f"  Type: {type(self.variable_value).__name__}")

        if self.hint:
            lines.append(f"\n[yellow]Hint:[/yellow] {self.hint}")

        if include_traceback:
            lines.append("\n[bold]Traceback:[/bold]")
            lines.append(traceback.format_exc())

        return "\n".join(lines)


class CLIError(Exception):
    """Custom exception for CLI errors with formatted output.

    This exception allows structured error messages that can include:
    - Main error message (printed with print_error)
    - Additional details (printed with console.print)
    - Optional style for details
    """

    def __init__(
        self,
        message: str,
        details: str | list[str] | None = None,
        style: str = "red",
    ):
        """Initialize CLI error.

        Args:
            message: Main error message (shown with error prefix)
            details: Additional details to print below error
                    Can be a string or list of strings
            style: Rich style for details (default: "red")
        """
        super().__init__(message)
        self.message = message
        self.details = (
            details if isinstance(details, list) else [details] if details else []
        )
        self.style = style


def handle_cli_errors(func: F) -> F:
    """Decorator to handle CLI errors uniformly.

    Catches CLIError exceptions and formats them using the printer,
    then exits with code 1.

    Example:
        @handle_cli_errors
        def my_command():
            raise CLIError("Something failed", details="More info here")
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get or create printer
        printer = MarkdownPrinter(cli_context.console)

        try:
            return func(*args, **kwargs)
        except CLIError as e:
            # Print main error message
            printer.print_error(e.message)

            # Print details if provided
            for detail in e.details:
                printer.console.print(f"  {detail}", style=e.style)

            # Exit with error code
            raise typer.Exit(1)

    return wrapper  # type: ignore
