"""CLI utilities package."""

from .context import CLIContext, cli_context
from .errors import CLIError, handle_cli_errors
from .parsers import InputParser, ParseResult
from .printers import MarkdownPrinter
from .types import (
    BlockTypeArg,
    HeadingLevelArg,
    MarkdownFileArg,
    OptionalOutputFileArg,
    OutputFormatArg,
    OutputFormatChoice,
    PrettyFlag,
    SectionPolicyArg,
    VerboseFlag,
    block_type_converter,
    heading_level_converter,
    section_policy_converter,
)

__all__ = [
    "CLIContext",
    "cli_context",
    "CLIError",
    "handle_cli_errors",
    "InputParser",
    "ParseResult",
    "MarkdownPrinter",
    "section_policy_converter",
    "block_type_converter",
    "heading_level_converter",
    "MarkdownFileArg",
    "OptionalOutputFileArg",
    "VerboseFlag",
    "PrettyFlag",
    "SectionPolicyArg",
    "BlockTypeArg",
    "HeadingLevelArg",
    "OutputFormatArg",
    "OutputFormatChoice",
]
