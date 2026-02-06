"""Extract subcommands for outputting markdown file data in various formats."""

from pathlib import Path
from typing import Annotated

import typer

from .utils import (
    MarkdownPrinter,
    OptionalOutputFileArg,
    OutputFormatArg,
    OutputFormatChoice,
    PrettyFlag,
    cli_context,
)

app = typer.Typer(
    name="extract",
    help="Extract markdown file data in various formats",
    no_args_is_help=True,
)

FilePathArg = Annotated[Path, typer.Argument(help="Path to the markdown file")]
PathOption = Annotated[
    str | None,
    typer.Option(
        "--path",
        help=(
            "Dot-separated path to extract "
            "(e.g., 'title', 'introduction', 'metadata.tags')"
        ),
    ),
]


@app.command("json")
def extract_json(
    file_path: FilePathArg,
    path: PathOption = None,
    pretty: PrettyFlag = False,
    output: OptionalOutputFileArg = None,
) -> None:
    """Extract file data as JSON.

    If --path is specified, extracts only the value at that path.
    Otherwise, extracts the entire document.
    """
    md_file = cli_context.load_file_for_command(file_path)
    printer = MarkdownPrinter(cli_context.console)

    # Extract specific path or entire document
    if path:
        try:
            data, warnings = md_file.mddata.get_value_at_path(path)
            # Display warnings if any
            for warning in warnings:
                printer.print_warning(warning)
        except (KeyError, ValueError) as e:
            printer.print_error(str(e))
            raise typer.Exit(1)
    else:
        data = md_file.mddata.to_dict()

    if output:
        import json

        with open(output, "w") as f:
            json.dump(data, f, indent=2 if pretty else None, default=str)
        printer.print_success(f"Extracted JSON to {output}")
    else:
        printer.print_json_output(data, pretty)


@app.command("yaml")
def extract_yaml(
    file_path: FilePathArg,
    path: PathOption = None,
    output: OptionalOutputFileArg = None,
) -> None:
    """Extract file data as YAML.

    If --path is specified, extracts only the value at that path.
    Otherwise, extracts the entire document.
    """
    try:
        import yaml
    except ImportError:
        cli_context.print_error(
            "PyYAML not installed. Install with: pip install PyYAML"
        )
        raise typer.Exit(1)

    md_file = cli_context.load_file_for_command(file_path)
    printer = MarkdownPrinter(cli_context.console)

    # Extract specific path or entire document
    if path:
        try:
            data, warnings = md_file.mddata.get_value_at_path(path)
            # Display warnings if any
            for warning in warnings:
                printer.print_warning(warning)
        except (KeyError, ValueError) as e:
            printer.print_error(str(e))
            raise typer.Exit(1)
    else:
        data = md_file.mddata.to_dict()

    yaml_content = yaml.dump(data, default_flow_style=False, allow_unicode=True)

    if output:
        with open(output, "w") as f:
            f.write(yaml_content)
        printer.print_success(f"Extracted YAML to {output}")
    else:
        print(yaml_content)


@app.command("path")
def extract_path(
    file_path: FilePathArg,
    path: Annotated[str, typer.Argument(help="Dot-separated path to extract")],
    output: OptionalOutputFileArg = None,
) -> None:
    """Extract value at a specific path.

    For frontmatter properties, returns the raw value as text.
    For sections, returns the section content as markdown.

    Examples:
        mddata extract path doc.md title
        mddata extract path doc.md introduction
        mddata extract path doc.md features.authentication
        mddata extract path doc.md metadata.tags
    """
    md_file = cli_context.load_file_for_command(file_path)
    printer = MarkdownPrinter(cli_context.console)

    try:
        value, warnings = md_file.mddata.get_value_at_path(path)
        # Display warnings if any
        for warning in warnings:
            printer.print_warning(warning)
    except (KeyError, ValueError) as e:
        printer.print_error(str(e))
        raise typer.Exit(1)

    # Convert value to string representation
    if isinstance(value, str):
        content = value
    elif isinstance(value, (list, dict)):
        import json

        content = json.dumps(value, indent=2, default=str)
    else:
        content = str(value)

    if output:
        with open(output, "w") as f:
            f.write(content)
        printer.print_success(f"Extracted path '{path}' to {output}")
    else:
        print(content)


@app.command("frontmatter")
def extract_frontmatter(
    file_path: FilePathArg,
    format_type: OutputFormatArg = OutputFormatChoice.JSON,
    output: OptionalOutputFileArg = None,
) -> None:
    """Extract only frontmatter properties."""
    md_file = cli_context.load_file_for_command(file_path)

    frontmatter = md_file.mddata.frontmatter
    printer = MarkdownPrinter(cli_context.console)

    if not frontmatter:
        printer.print_warning("No frontmatter properties found")
        return

    # Use enum comparison instead of string comparison
    if format_type == OutputFormatChoice.YAML:
        try:
            import yaml

            content = yaml.dump(
                frontmatter, default_flow_style=False, allow_unicode=True
            )
        except ImportError:
            printer.print_error(
                "PyYAML not installed. Install with: pip install PyYAML"
            )
            raise typer.Exit(1)
    else:
        import json

        content = json.dumps(frontmatter, indent=2, default=str)

    if output:
        with open(output, "w") as f:
            f.write(content)
        printer.print_success(f"Extracted frontmatter to {output}")
    else:
        print(content)
