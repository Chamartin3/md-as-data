# mddata Claude Code Tools

Comprehensive suite of Claude Code extensions for treating markdown files as structured data using the mddata command-line tool.

## Overview

This toolkit enables Claude to autonomously query, validate, transform, and generate markdown documents by treating them as structured data objects with:
- **Frontmatter properties** (YAML metadata)
- **Hierarchical sections** (heading-based structure)
- **Typed content blocks** (paragraphs, code, lists, etc.)

## What's Included

### 📦 Complete Plugin
- **`mddata-plugin/`** - Full-featured plugin bundling all tools
  - Install once, get everything
  - Skills, commands, and agent in one package
  - Perfect for teams and comprehensive workflows

### 🎯 Individual Skills (Autonomous)
- **`md-query-skill/`** - Automatic markdown inspection
- **`md-schema-skill/`** - Auto-validation and schema management
- **`md-template-skill/`** - Template-based document generation
- **`md-generator-skill/`** - Markdown generation from data/schemas

### ⚡ Slash Commands (User-Invoked)
- **`md-commands/`** - 8 quick-access commands
  - `/md-info` - Document overview
  - `/md-extract` - Export to JSON/YAML
  - `/md-validate` - Schema validation
  - `/md-update-property` - Set frontmatter
  - `/md-update-section` - Modify sections
  - `/md-infer-schema` - Generate schemas
  - `/md-apply-template` - Apply YAML templates
  - `/md-generate` - Generate from JSON/schemas

### 🤖 Expert Agent (Complex Tasks)
- **`md-doc-editor/`** - Advanced document editing
  - Nested data editing with verification
  - Document creation from schemas/data
  - Comprehensive validation workflows
  - Bulk operations with proof of changes

## Quick Start

### Automated Installation (Recommended)

Use the included installation script for easy setup:

```bash
# Navigate to tools directory
cd /home/omidev/Code/tools/mdasdata/claude_mddata_tools

# Install complete plugin globally (user-level)
./install.sh plugin global

# Or install locally in current project
./install.sh plugin local .

# Or install in specific project
./install.sh plugin local /path/to/project
```

This gives you everything: skills, commands, and agent.

**Other installation options:**
```bash
# Install individual components
./install.sh skill-query global    # Query skill only
./install.sh skill-schema global   # Schema skill only
./install.sh commands global       # All commands only
./install.sh agent global          # Agent only
./install.sh all global            # All tools individually

# Uninstall
./uninstall.sh global              # Remove from user-level
./uninstall.sh local /path         # Remove from project
```

### Manual Installation (Alternative)

Manual installation using symbolic links:

```bash
# Skills (autonomous) - all 4
cp -r md-query-skill ~/.claude/skills/
cp -r md-schema-skill ~/.claude/skills/
cp -r md-template-skill ~/.claude/skills/
cp -r md-generator-skill ~/.claude/skills/

# Commands (slash commands) - all 8
cp md-commands/*.md ~/.claude/commands/

# Agent (complex tasks)
cp -r md-doc-editor ~/.claude/agents/
```

## Prerequisites

All tools require the `mddata` command:

```bash
# Verify installation
mddata --version

# Should output: mddata version 0.1.0 or higher
```

If mddata is not installed, see the main project README for installation instructions.

## Usage Examples

### Using Skills (Automatic)

Just ask Claude naturally:

```
User: "What's in this README.md file?"
→ md-query skill activates automatically
→ Runs mddata info commands
→ Presents structured summary

User: "Make sure this doc follows our schema"
→ md-schema skill activates
→ Validates document
→ Reports results

User: "Create a blog post from the template"
→ md-template skill activates
→ Applies parameterized template
→ Generates document

User: "Generate markdown from this JSON data"
→ md-generator skill activates
→ Validates JSON structure
→ Creates markdown document
```

### Using Slash Commands (Quick Operations)

```bash
# Get comprehensive document info
/md-info documentation.md

# Extract to JSON for processing
/md-extract api-guide.md json

# Validate against schema
/md-validate doc.md schema.json

# Update frontmatter property
/md-update-property doc.md version 2.0

# Modify section content
/md-update-section doc.md intro "New introduction" --policy replace

# Generate schema from docs
/md-infer-schema ./docs/

# Apply template to document
/md-apply-template post.md blog_template.yaml -p title="My Post"

# Generate markdown from JSON data
/md-generate --data content.json --output document.md
```

### Using Agent (Complex Tasks)

Invoke for sophisticated workflows:

```
User: "I need to migrate all our API docs to version 2.0 format and validate them"

→ markdown-doc-editor agent activates
→ Analyzes current structure
→ Plans multi-step migration
→ Generates transformations
→ Applies changes with verification
→ Validates all results
→ Reports outcomes with proof
```

## Tool Selection Guide

| When You Need | Use This | Type |
|---------------|----------|------|
| Quick document inspection | md-query skill | Autonomous |
| Document info display | `/md-info` | Command |
| Schema validation | md-schema skill | Autonomous |
| Run validation check | `/md-validate` | Command |
| Extract to JSON/YAML | `/md-extract` | Command |
| Update single property | `/md-update-property` | Command |
| Modify section | `/md-update-section` | Command |
| Generate schema | `/md-infer-schema` | Command |
| Apply template | md-template skill | Autonomous |
| Apply template manually | `/md-apply-template` | Command |
| Generate from data | md-generator skill | Autonomous |
| Generate manually | `/md-generate` | Command |
| Document editing with verification | markdown-doc-editor | Agent |
| Create docs from schemas/data | markdown-doc-editor | Agent |
| Nested data manipulation | markdown-doc-editor | Agent |
| Bulk operations with proof | markdown-doc-editor | Agent |

## Architecture

### Self-Contained Design

Each tool is completely self-contained:
- ✅ All documentation included
- ✅ No external dependencies (except mddata)
- ✅ Reference materials bundled
- ✅ Works independently or as part of plugin

### Tool Organization

```
claude_mddata_tools/
├── mddata-plugin/              # Complete plugin (symlinks)
│   ├── .claude-plugin/
│   │   └── plugin.json         # Plugin metadata
│   ├── skills/                 # Symlinks to all 4 skills
│   │   ├── md-query-skill/     → symlink
│   │   ├── md-schema-skill/    → symlink
│   │   ├── md-template-skill/  → symlink
│   │   └── md-generator-skill/ → symlink
│   ├── commands/               # Symlinks to all 8 commands
│   ├── agents/                 # Symlink to transformer agent
│   ├── README.md               # Plugin documentation
│   └── LICENSE
├── md-query-skill/             # Standalone: inspection
│   └── SKILL.md
├── md-schema-skill/            # Standalone: validation
│   ├── SKILL.md
│   └── reference.md
├── md-template-skill/          # Standalone: templates
│   └── SKILL.md
├── md-generator-skill/         # Standalone: generation
│   └── SKILL.md
├── md-commands/                # Standalone: all 8 commands
│   ├── md-info.md
│   ├── md-extract.md
│   ├── md-validate.md
│   ├── md-update-property.md
│   ├── md-update-section.md
│   ├── md-infer-schema.md
│   ├── md-apply-template.md
│   └── md-generate.md
├── md-doc-editor/              # Standalone: expert editor
│   ├── AGENT.md
│   ├── README.md
│   ├── transformation-guide.md
│   └── advanced-guide.md
├── SUMMARY.md                  # Complete reference
└── README.md                   # This file
```

## Features

### Read Operations
- ✅ Document summaries with statistics
- ✅ Frontmatter property listing
- ✅ Section hierarchy display
- ✅ Content block analysis
- ✅ Task list inspection
- ✅ Data extraction (JSON/YAML)

### Write Operations
- ✅ Frontmatter property updates
- ✅ Section content modifications
- ✅ Bulk transformations from JSON
- ✅ Template-based generation
- ✅ New document creation

### Validation & Schemas
- ✅ Schema generation (single/multi-file)
- ✅ Document validation
- ✅ Compliance checking
- ✅ Format conversion (JSON ↔ YAML)
- ✅ Inference modes (permissive/strict)

### Advanced Operations
- ✅ Extract-Transform-Load (ETL) workflows
- ✅ Batch processing across files
- ✅ Migration automation
- ✅ CI/CD pipeline integration
- ✅ Custom transformation logic

## Common Workflows

### Documentation Validation Pipeline

```bash
# 1. Generate schema from template
/md-infer-schema template.md > schema.json

# 2. Validate all documents
for doc in docs/**/*.md; do
  /md-validate "$doc" schema.json
done
```

### Content Migration

```
User: "Update all docs to new format with schema validation"

→ Agent analyzes structure
→ Plans migration steps
→ Applies transformations
→ Validates results
→ Reports success/failures
```

### Schema-Driven Development

```bash
# 1. Generate schema from existing docs
/md-infer-schema ./docs/ > docs-schema.json

# 2. Create new document from schema
mddata render --schema docs-schema.json --output new-doc.md

# 3. Validate
/md-validate new-doc.md docs-schema.json
```

## Security & Permissions

### Tool Access Control

**Skills** (Limited):
- `md-query`: Read-only (`Bash(mddata:*)`, `Read`)
- `md-schema`: Limited write (`Bash(mddata:*)`, `Read`, `Write`)

**Commands** (Restricted):
- All commands: mddata operations only (`Bash(mddata:*)`)

**Agent** (Full access):
- `markdown-doc-editor`: All tools (`Bash`, `Read`, `Write`, `Edit`)

### Safety Features

- ✅ Skills cannot modify files arbitrarily
- ✅ Commands restricted to mddata operations
- ✅ Agent communicates all actions
- ✅ Dry-run support for bulk operations
- ✅ Validation before destructive changes

## Documentation

Each tool includes comprehensive documentation:

### Skills
- **SKILL.md** - Complete usage guide with examples
- **reference.md** - Detailed reference material (where applicable)

### Commands
- **command.md** - Usage, examples, and inline help

### Agent
- **AGENT.md** - Expert transformation guide
- **transformation-guide.md** - Basic patterns
- **advanced-guide.md** - Complex workflows

### Summary
- **SUMMARY.md** - Complete toolkit reference (start here!)

## Support

- **Full Reference**: See [SUMMARY.md](./SUMMARY.md)
- **mddata Manual**: `manual/` directory in mddata repository
- **CLI Reference**: `docs/CLI_REFERENCE.md` in mddata repository
- **Project Docs**: Main mddata `README.md` and `CLAUDE.md`

## Version

- **Release**: 1.0.0
- **Date**: 2025-10-24
- **mddata Compatibility**: >= 0.1.0
- **Claude Code**: All versions

## License

MIT License - See individual tool LICENSE files

## Contributing

To add new tools:

1. **Skills**: Create `new-skill/SKILL.md` with frontmatter
2. **Commands**: Add `new-command.md` to `md-commands/`
3. **Agents**: Create `new-agent/AGENT.md` with frontmatter
4. Update `mddata-plugin/` to include new tools
5. Update `SUMMARY.md` with new tool documentation

## Credits

Built for the mddata project by the mddata team.

**mddata**: Treating markdown files as structured data since 2025.

---

## Quick Reference

### Installation
```bash
# Automated (recommended)
./install.sh plugin global

# Manual
mkdir -p ~/.claude/plugins
ln -sf "$(pwd)/mddata-plugin" ~/.claude/plugins/mddata-tools
```

### Skills (4 total)
- `md-query` → Inspect documents
- `md-schema` → Validate schemas
- `md-template` → Apply templates
- `md-generator` → Generate from data

### Commands (8 total)
```bash
/md-info <file>
/md-extract <file> [json|yaml]
/md-validate <file> <schema>
/md-update-property <file> <key> <value>
/md-update-section <file> <path> <content> [--policy]
/md-infer-schema <path>
/md-apply-template <file> <template> -p key="value"
/md-generate [--data file] [--schema file] --output file
```

### Agent
- `markdown-doc-editor` → Document editing with verification

### Check Installation
```bash
mddata --version
```

---

**📝 Happy documenting with structured markdown!**
