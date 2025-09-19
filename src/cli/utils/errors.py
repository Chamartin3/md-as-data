"""CLI error handling utilities."""

from collections.abc import Callable
from functools import wraps
from typing import TypeVar

import typer

from .context import cli_context
from .printers import MarkdownPrinter

F = TypeVar("F", bound=Callable)


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
