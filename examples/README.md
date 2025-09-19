# mdasdata Examples

This directory contains practical examples demonstrating key features of the mdasdata library.

## Quick Start

See **[EXAMPLES.md](EXAMPLES.md)** for comprehensive documentation including:
- Step-by-step running instructions
- Expected outputs for each example
- Troubleshooting tips
- `uv run` commands for all features

## Available Examples

### ✅ Multi-File Schema Generation (`multi_file_schema/`)
Generate merged schemas from multiple markdown documents with intelligent property aggregation.

**Quick Run**:
```bash
uv run python examples/multi_file_schema/example_multi_file_schema.py
```

### 🚧 Task Lists (`task_lists/`)
Planned feature for extracting and manipulating markdown task lists (Issue #005).

**Quick Run**:
```bash
uv run python examples/task_lists/example_task_lists.py
```

### ✅ Template System (`templates/`)
Parameterized templates for reusable document modifications with type-safe validation (Tasks 017-021, 025).

**Features**:
- Simple, array, and complex parameter types
- Computed parameters ({date}, {now}, {env.*})
- Constraint validation (min, max, enum, pattern)
- Full Python API (CLI integration pending)

**Quick Run**:
```bash
uv run python examples/templates/demo_template_usage.py
```

**Available Templates**:
- `log-entry.yaml` - Simple template with computed params
- `meeting-notes.yaml` - Array parameters demonstration
- `bug-report.yaml` - Complex constraints and validation

See [templates/README.md](templates/README.md) for detailed documentation.

## Documentation

For complete details, see [EXAMPLES.md](EXAMPLES.md).
