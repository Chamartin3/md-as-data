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


@app.command("json")
def extract_json(
    file_path: FilePathArg,
    pretty: PrettyFlag = False,
    output: OptionalOutputFileArg = None,
) -> None:
    """Extract file data as JSON."""
    md_file = cli_context.load_file_for_command(file_path)

    data = md_file.mddata.to_dict()
    printer = MarkdownPrinter(cli_context.console)

    if output:
        import json

        with open(output, "w") as f:
            json.dump(data, f, indent=2 if pretty else None)
        printer.print_success(f"Extracted JSON to {output}")
    else:
        printer.print_json_output(data, pretty)


@app.command("yaml")
def extract_yaml(
    file_path: FilePathArg,
    output: OptionalOutputFileArg = None,
) -> None:
    """Extract file data as YAML."""
    try:
        import yaml
    except ImportError:
        cli_context.print_error(
            "PyYAML not installed. Install with: pip install PyYAML"
        )
        raise typer.Exit(1)

    md_file = cli_context.load_file_for_command(file_path)

    data = md_file.mddata.to_dict()
    printer = MarkdownPrinter(cli_context.console)

    yaml_content = yaml.dump(data, default_flow_style=False, allow_unicode=True)

    if output:
        with open(output, "w") as f:
            f.write(yaml_content)
        printer.print_success(f"Extracted YAML to {output}")
    else:
        print(yaml_content)


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

        content = json.dumps(frontmatter, indent=2)

    if output:
        with open(output, "w") as f:
            f.write(content)
        printer.print_success(f"Extracted frontmatter to {output}")
    else:
        print(content)
