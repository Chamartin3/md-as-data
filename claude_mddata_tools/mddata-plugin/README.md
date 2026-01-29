# mddata-tools Plugin

Comprehensive Claude Code plugin for working with markdown files as structured data using the mddata tool.

## Overview

This plugin enables Claude to autonomously query, validate, transform, and generate markdown documents by treating them as structured data objects. It provides skills for automatic assistance, slash commands for quick operations, and expert agents for complex transformations.

## Features

### 🔍 **Autonomous Skills**

- **md-query**: Automatically inspect markdown files when users ask about document structure, properties, or content
- **md-schema**: Auto-validate documents against schemas and maintain consistency across documentation

### ⚡ **Slash Commands**

Quick access to common mddata operations:

- `/md-info <file>` - Display comprehensive document information
- `/md-extract <file> [json|yaml]` - Extract to structured format
- `/md-validate <file> <schema>` - Validate against schema
- `/md-update-property <file> <key> <value>` - Set frontmatter property
- `/md-update-section <file> <path> <content>` - Modify section content
- `/md-infer-schema <path>` - Generate schema from documents

### 🤖 **Expert Agent**

- **markdown-data-engineer**: Specialized agent for complex document transformations, bulk operations, and sophisticated workflows

## Installation

### Prerequisites

Ensure `mddata` is installed in your project:

```bash
# If using the mddata project directly
uv sync --dev

# Or if mddata is installed as a package
pip install mddata
```

### Install Plugin

#### Option 1: Project-Level (Recommended for teams)

Copy the plugin to your project's Claude configuration:

```bash
cp -r mddata-plugin /path/to/your/project/.claude/plugins/
```

#### Option 2: User-Level (Personal use)

Copy to your user Claude configuration:

```bash
cp -r mddata-plugin ~/.claude/plugins/
```

#### Option 3: Via Git Clone

```bash
# Project-level
cd /path/to/your/project/.claude/plugins/
git clone https://github.com/mddata/claude-mddata-tools mddata-tools

# User-level
cd ~/.claude/plugins/
git clone https://github.com/mddata/claude-mddata-tools mddata-tools
```

## Usage

### Autonomous Skills

Skills activate automatically based on user requests:

```
User: "What's in this README.md file?"
→ md-query skill activates, runs mddata info commands

User: "Make sure this document follows our schema"
→ md-schema skill activates, validates document
```

### Slash Commands

Use commands for quick operations:

```bash
# Get document overview
/md-info documentation.md

# Extract to JSON
/md-extract api-guide.md json

# Validate document
/md-validate README.md docs-schema.json

# Update property
/md-update-property README.md version 2.0

# Update section
/md-update-section README.md introduction "New intro text"

# Generate schema
/md-infer-schema ./docs/
```

### Expert Agent

Invoke for complex tasks:

```
User: "I need to migrate all our documentation to a new format and validate against our schema"

Claude invokes the markdown-data-engineer agent which:
1. Analyzes current document structure
2. Plans migration strategy
3. Generates transformation scripts
4. Applies changes systematically
5. Validates results
6. Reports outcomes
```

## Components

### Skills

**md-query-skill/**
- SKILL.md - Query and inspection operations
- Autonomous markdown file analysis
- Read-only operations

**md-schema-skill/**
- SKILL.md - Schema generation and validation
- reference.md - Detailed schema documentation
- Automatic schema compliance checking

### Commands

**commands/**
- md-info.md - Document information display
- md-extract.md - Export to JSON/YAML
- md-validate.md - Schema validation
- md-update-property.md - Frontmatter modifications
- md-update-section.md - Section content updates
- md-infer-schema.md - Schema generation

### Agents

**md-transformer-agent/**
- AGENT.md - Expert transformation agent
- transformation-guide.md - Basic patterns
- advanced-guide.md - Complex workflows
- Handles bulk operations and migrations

## Common Workflows

### Documentation Validation Pipeline

```bash
# 1. Generate schema from template
/md-infer-schema template.md

# 2. Validate all documents
for doc in docs/**/*.md; do
  /md-validate "$doc" schema.json
done
```

### Content Migration

```
User: "Update all API docs to version 2.0 and add deprecation notices"

→ markdown-data-engineer agent creates transformation plan
→ Generates bulk update JSON
→ Applies systematically with mddata modify from-json
→ Validates results
```

### Schema-Driven Development

```bash
# 1. Extract existing doc structure
/md-extract reference-doc.md json > structure.json

# 2. Generate schema
/md-infer-schema reference-doc.md > schema.json

# 3. Create new docs from schema
mddata render --schema schema.json --output new-doc.md

# 4. Validate
/md-validate new-doc.md schema.json
```

## Benefits

### For Development Teams

- **Consistency**: Enforce document structure across projects
- **Automation**: Programmatic document generation and updates
- **Validation**: CI/CD integration with schema validation
- **Migration**: Bulk transformations with confidence

### For Documentation Writers

- **Structure**: Clear document organization with sections
- **Templates**: Generate documents from schemas
- **Validation**: Ensure completeness and correctness
- **Queries**: Quick access to document information

### For Content Managers

- **Bulk Operations**: Update multiple documents efficiently
- **Metadata Management**: Programmatic frontmatter updates
- **Export**: Extract data for APIs and integrations
- **Standards**: Maintain documentation standards

## Examples

### Inspect Document

```bash
/md-info README.md
```

Output includes:
- Document summary
- Frontmatter properties
- Section hierarchy
- Block distribution

### Extract for Processing

```bash
/md-extract api-docs.md json
```

Use extracted JSON with jq, Python, or other tools for processing.

### Validate Documentation

```bash
# Generate schema from good example
/md-infer-schema examples/good-doc.md > doc-schema.json

# Validate all docs
for doc in docs/**/*.md; do
  /md-validate "$doc" doc-schema.json
done
```

### Bulk Property Update

```
User: "Set status to 'published' and add today's date to all docs"

→ Agent creates transformation JSON
→ Applies to all files
→ Validates results
```

## Configuration

### mddata Command

The plugin requires `mddata` to be available. It uses `mddata` by default.

If mddata is installed differently in your environment, you may need to adjust commands in:
- Skill SKILL.md files
- Command .md files
- Agent AGENT.md

### Allowed Tools

Skills and commands have restricted tool access for security:

- **md-query-skill**: `Bash(mddata:*)`, `Read` (read-only)
- **md-schema-skill**: `Bash(mddata:*)`, `Read`, `Write`
- **md-transformer-agent**: `Bash`, `Read`, `Write`, `Edit` (full access)
- **Commands**: `Bash(mddata:*)` only

## Troubleshooting

### mddata command not found

Ensure mddata is installed and accessible:

```bash
# Check installation
which mddata
mddata --version

# Or use uv run
mddata --version
```

### Permission errors

Check file permissions:

```bash
chmod +r document.md  # For reading
chmod +w document.md  # For writing
```

### Schema validation fails

Check schema format and document structure:

```bash
# Inspect document
/md-info document.md

# View schema
/md-infer-schema document.md

# Validate with verbose output
/md-validate document.md schema.json
```

## Development

### Adding Custom Commands

Create new .md files in `commands/`:

```markdown
---
description: Your command description
argument-hint: <args>
allowed-tools: Bash(mddata:*)
---

# Command content here
!`mddata <operation> $1`
```

### Extending Skills

Add new SKILL.md files in `skills/<skill-name>/`:

```markdown
---
name: skill-name
description: When to use this skill
allowed-tools: Bash(mddata:*), Read
---

# Skill instructions
```

### Customizing Agent

Modify `agents/md-transformer-agent/AGENT.md` to add specialized transformation patterns or workflows.

## Support

- **Documentation**: See manual/ directory in mddata repository
- **Issues**: Report via GitHub issues
- **Examples**: Check examples/ in mddata repository

## License

MIT License - See LICENSE file

## Credits

Built for the mddata project - treating markdown files as structured data.
