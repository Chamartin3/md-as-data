# IPython Configuration for md_as_data Development

This document explains the simplified IPython configuration setup for the md_as_data project, enabling seamless interactive development with automatic imports and configuration loading.

## Quick Start

### Create Development Profile

Create a custom IPython profile for development:

```bash
uv run ipython profile create dev
```

### Launch Development Shell

Start IPython with the development configuration:

```bash
IPYTHONDIR=.ipython_profile_default uv run ipython --profile=dev
```

This automatically:
- Loads all md_as_data classes and types
- Enables auto-reload for live code changes
- Provides helper functions for common tasks
- Sets up the development environment

## Configuration Architecture

### Overview

The IPython configuration uses a simple profile-based setup that integrates with uv's virtual environment management. The configuration consists of:

1. **IPython Profile** - Local profile directory with startup scripts and configuration
2. **Profile Configuration** - Auto-reload and development settings
3. **Startup Scripts** - Auto-import and helper function definitions

### File Structure

```
mdasdata/
├── .ipython_profile_default/                  # Local IPython profile directory
│   └── profile_default/
│       ├── ipython_config.py                  # IPython configuration with auto-reload
│       └── startup/
│           └── 00_md_as_data.py               # Auto-import and setup script (if needed)
└── docs/ipython.md                            # This documentation
```

## Implementation Details

### 1. IPython Profile Configuration

The profile configuration in `.ipython_profile_default/profile_default/ipython_config.py` provides:

Key features:
- **Auto-reload**: Automatically reloads modules when source files change (`%autoreload 2`)
- **Path Setup**: Adds `src/` directory to Python path for direct imports
- **Development Feedback**: Provides clear startup messages and status indicators
- **Import Safety**: Graceful handling of import errors during development

### 2. Simple Setup Process

Creating a development profile is straightforward:

```bash
# Create a new profile named 'dev'
uv run ipython profile create dev
```

This creates the profile structure in `.ipython_profile_default/profile_dev/` with:
- Empty startup directory for custom scripts
- Default configuration that can be customized
- Isolated environment for development work

## Development Features

### Auto-Reload Configuration

The profile automatically enables:

```python
%load_ext autoreload
%autoreload 2
```

This means:
- **Live Development**: Changes to source files are automatically detected and reloaded
- **No Restart Needed**: Modify code and immediately test changes in the same session
- **Seamless Workflow**: Focus on development without interruption

### Import Setup

The configuration automatically:
- Adds `src/` directory to Python path
- Enables direct imports: `from md_as_data import MarkdownFile`
- Provides clear feedback about successful configuration loading

### Available Classes

After starting IPython, you can directly use:

```python
# Core functionality
from md_as_data import MarkdownFile, MarkdownData, Section, Block

# Load and work with documents
doc = MarkdownFile('examples/sample.md')
data = doc.mddata
sections = data.sections
```

## Configuration Details

### Visual Notifications

The configuration provides clear visual feedback:

```
======================================================================
🚀 MD_AS_DATA IPYTHON CONFIGURATION LOADING...
======================================================================
✅ Core md_as_data classes imported successfully
🛠️  Helper functions available:
   • load_example('simple'|'complex'|'minimal') - Load example files
   • quick_parse(filename) - Quick parse any markdown file
   • show_sections(md_file) - Display document structure
   • show_frontmatter(md_file) - Display frontmatter properties

📌 Available Classes:
   • MarkdownFile, MarkdownData, Section, Block
   • BlockType, HeadingLevel, ContentTree
   • All TypedDict types for type-safe data access
🔄 Auto-reload enabled
📁 Added src/ to Python path
📚 Ready to import md_as_data modules!
======================================================================
✅ MD_AS_DATA CONFIGURATION SUCCESSFULLY LOADED!
======================================================================
```

### Error Handling

If configuration fails to load, you'll see clear error messages:

```
❌ ERROR: Could not import md_as_data modules
   Reason: [specific error message]

⚠️  CONFIGURATION NOT LOADED - Check that:
   1. You're running from the project root directory
   2. The package is installed with 'uv sync --dev'
   3. The src/ directory exists and contains md_as_data module
```

## Usage Examples

### Basic Development Session

```python
# IPython starts with everything imported
In [1]: # Load a markdown file
   ...: md = MarkdownFile('README.md')

In [2]: # Access frontmatter dynamically
   ...: print(md.mddata.title)  # If title exists in frontmatter

In [3]: # Show document structure
   ...: show_sections(md)

In [4]: # Access sections by path
   ...: intro = md.mddata.content.get_section('introduction')
```

### Working with Helper Functions

```python
# Load example files (if they exist)
example = load_example('simple')

# Quick parse any file
data = quick_parse('document.md')

# Display structure
show_sections(example)
show_frontmatter(example)
```

### Testing Code Changes

Thanks to auto-reload, you can modify source code and see changes immediately:

```python
# 1. Edit a function in src/md_as_data/models.py
# 2. The change is automatically available in IPython
# 3. No need to restart or manually reload
```

## Alternative Launch Methods

While `uv run ipython` is the recommended approach, alternative methods are available:

```bash
# Direct profile specification
uv run ipython --profile-dir=.ipython_profile_default

# Via development script (if available)
uv run python scripts/ipython_dev.py
```

## Troubleshooting

### Common Issues

1. **Configuration not loading**
   - Ensure you're in the project root directory
   - Run `uv sync --dev` to install dependencies
   - Check that `.ipython_profile_default/` directory exists

2. **Import errors**
   - Verify the package is installed in development mode
   - Check that `src/md_as_data/` directory exists
   - Ensure `pyproject.toml` is configured correctly

3. **IPython not found**
   - Run `uv sync --dev` to install IPython
   - Check that IPython is in the dev dependencies

### Debugging

To debug configuration issues:

```bash
# Check IPython installation
uv run ipython --version

# Check where IPython looks for profiles
uv run ipython locate

# Check Python path in virtual environment
uv run python -c "import sys; print('\n'.join(sys.path))"
```

## Design Philosophy

### Project-Local Configuration

The configuration is designed to be completely project-local:
- No global IPython configuration modifications
- No system-wide dependencies
- Self-contained within the project directory
- Safe for multiple projects on the same system

### Integration with uv

The setup leverages uv's capabilities:
- Virtual environment management
- Script entry points in `pyproject.toml`
- Development dependency management
- Clean integration with project structure

### Developer Experience

The configuration prioritizes developer productivity:
- Single command to start configured IPython
- Clear visual feedback about what's loaded
- Comprehensive auto-imports
- Helpful utility functions
- Auto-reload for immediate feedback

## Maintenance

### Updating Configuration

To modify the IPython configuration:

1. **Add new imports**: Edit `.ipython_profile_default/startup/00_md_as_data.py`
2. **Add new helpers**: Add functions to the startup script
3. **Change IPython settings**: Edit `.ipython_profile_default/ipython_config.py`
4. **Modify launcher**: Edit `src/ipython_launcher.py`

### Version Compatibility

The configuration is designed to work with:
- IPython 9.5.0+ (specified in dev dependencies)
- Python 3.11+ (project requirement)
- uv latest (for script execution and virtual environment management)

## Conclusion

This IPython configuration provides a seamless development experience for the md_as_data project. By using `uv run ipython`, developers get a fully configured interactive environment with all necessary imports, helper functions, and development features ready to use.

The project-local approach ensures no interference with other projects or global IPython settings, while the integration with uv provides a clean and modern Python development workflow.