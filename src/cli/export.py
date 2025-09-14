"""Export subcommands for outputting markdown file data in various formats."""

from typing import Annotated

import typer

from .utils import (
    MarkdownPrinter,
    OptionalOutputFileArg,
    PrettyFlag,
    cli_context,
)

app = typer.Typer(
    name="export",
    help="Export markdown file data in various formats",
    no_args_is_help=True,
)


@app.command("json")
def export_json(
    pretty: PrettyFlag = False,
    output: OptionalOutputFileArg = None,
) -> None:
    """Export file data as JSON."""
    md_file = cli_context.ensure_file_loaded()

    data = md_file.mddata.to_dict()
    printer = MarkdownPrinter(cli_context.console)

    if output:
        import json

        with open(output, "w") as f:
            json.dump(data, f, indent=2 if pretty else None)
        printer.print_success(f"Exported JSON to {output}")
    else:
        printer.print_json_output(data, pretty)


@app.command("yaml")
def export_yaml(
    output: OptionalOutputFileArg = None,
) -> None:
    """Export file data as YAML."""
    try:
        import yaml
    except ImportError:
        cli_context.print_error(
            "PyYAML not installed. Install with: pip install PyYAML"
        )
        raise typer.Exit(1)

    md_file = cli_context.ensure_file_loaded()

    data = md_file.mddata.to_dict()
    printer = MarkdownPrinter(cli_context.console)

    yaml_content = yaml.dump(data, default_flow_style=False, allow_unicode=True)

    if output:
        with open(output, "w") as f:
            f.write(yaml_content)
        printer.print_success(f"Exported YAML to {output}")
    else:
        print(yaml_content)


@app.command("frontmatter")
def export_frontmatter(
    format_type: Annotated[
        str, typer.Option("--format", "-f", help="Output format: json, yaml")
    ] = "json",
    output: OptionalOutputFileArg = None,
) -> None:
    """Export only frontmatter properties."""
    md_file = cli_context.ensure_file_loaded()

    frontmatter = md_file.mddata.frontmatter
    printer = MarkdownPrinter(cli_context.console)

    if not frontmatter:
        printer.print_warning("No frontmatter properties found")
        return

    if format_type.lower() == "yaml":
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
        printer.print_success(f"Exported frontmatter to {output}")
    else:
        print(content)
