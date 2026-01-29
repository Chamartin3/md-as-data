# Verification Guide

Complete guide to verify that mddata Claude Code tools are properly installed and working.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation Verification](#installation-verification)
- [Skills Verification](#skills-verification)
- [Commands Verification](#commands-verification)
- [Agent Verification](#agent-verification)
- [End-to-End Testing](#end-to-end-testing)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### 1. Verify mddata Installation

First, ensure mddata is installed and accessible:

```bash
# Check mddata is in PATH
which mddata

# Verify version
mddata --version

# Expected output: mddata version 0.1.0 or higher
```

If mddata is not found:

```bash
# Navigate to mddata project
cd /home/omidev/Code/tools/mdasdata

# Verify installation
uv sync --dev

# Test with full path
uv run mddata --version
```

### 2. Create Test Markdown File

Create a sample markdown file for testing:

```bash
# Navigate to a test directory
cd /tmp

# Create test markdown file
cat > test-document.md << 'EOF'
---
title: "Test Document"
author: "Test User"
version: 1.0
tags: ["test", "verification"]
status: "draft"
---

# Introduction

This is a test document for verifying mddata Claude Code tools.

## Overview

The document contains:
- Frontmatter properties
- Multiple sections
- Different content types

## Features

### Code Blocks

```python
def hello():
    print("Hello, mddata!")
```

### Lists

- Item one
- Item two
- Item three

## Conclusion

This document is used for testing.
EOF

# Verify file was created
ls -la test-document.md
```

### 3. Test mddata Commands Manually

Before testing with Claude, verify mddata works:

```bash
# Test info command
mddata info summary test-document.md

# Test extract command
mddata extract json test-document.md --pretty

# Test schema generation
mddata schema generate test-document.md --output test-schema.json

# Test validation
mddata schema validate test-document.md test-schema.json

# If all commands work, mddata is properly installed!
```

## Installation Verification

### Check Symbolic Links

Verify the installation created proper symbolic links:

```bash
# For global (user-level) installation
ls -la ~/.claude/plugins/mddata-tools
ls -la ~/.claude/skills/md-query
ls -la ~/.claude/skills/md-schema
ls -la ~/.claude/commands/md-*.md
ls -la ~/.claude/agents/markdown-data-engineer

# For local (project-level) installation
ls -la /path/to/project/.claude/plugins/mddata-tools
ls -la /path/to/project/.claude/skills/
ls -la /path/to/project/.claude/commands/
ls -la /path/to/project/.claude/agents/
```

**Expected output:**
- Symbolic links (shown with `->` arrow)
- Links should point to your tools directory
- No broken links (check with `ls -L`)

**Example:**
```
lrwxrwxrwx ... mddata-tools -> /home/omidev/Code/tools/mdasdata/claude_mddata_tools/mddata-plugin
```

### Verify File Accessibility

Check that Claude can read the files:

```bash
# Test plugin structure
ls -la ~/.claude/plugins/mddata-tools/.claude-plugin/plugin.json
ls -la ~/.claude/plugins/mddata-tools/skills/
ls -la ~/.claude/plugins/mddata-tools/commands/
ls -la ~/.claude/plugins/mddata-tools/agents/

# Verify files are readable
cat ~/.claude/plugins/mddata-tools/.claude-plugin/plugin.json
```

## Skills Verification

Skills activate automatically based on user requests. Test each skill:

### Test md-query Skill

**In Claude Code, ask:**

```
"What's in the test-document.md file?"
```

**Expected behavior:**
1. Claude recognizes this as a markdown inspection request
2. The `md-query` skill activates automatically
3. Claude runs commands like:
   - `mddata info summary test-document.md`
   - `mddata info properties test-document.md`
   - `mddata info sections test-document.md`
4. Claude provides structured information about the document

**What to look for:**
- ✓ Claude mentions using mddata or markdown inspection
- ✓ Output includes frontmatter properties (title, author, etc.)
- ✓ Output shows section structure
- ✓ No errors about mddata command not found

**Alternative test:**

```
"List all the sections in test-document.md"
"What frontmatter properties does test-document.md have?"
"Show me the structure of test-document.md"
```

### Test md-schema Skill

**In Claude Code, ask:**

```
"Validate test-document.md against its schema"
```

**Expected behavior:**
1. If schema doesn't exist, Claude may offer to generate one
2. The `md-schema` skill activates
3. Claude runs schema validation commands
4. Reports validation results

**Alternative tests:**

```
"Generate a schema for test-document.md"
"Does test-document.md follow a consistent structure?"
"Check if this markdown file has all required properties"
```

**Manual skill verification:**

```bash
# Check if skill files are accessible
cat ~/.claude/skills/md-query/SKILL.md | head -20
cat ~/.claude/skills/md-schema/SKILL.md | head -20

# Look for the frontmatter with 'name' and 'description'
```

## Commands Verification

Commands are invoked manually with `/command-name` syntax.

### Test /md-info Command

**In Claude Code:**

```
/md-info test-document.md
```

**Expected output:**
- Document summary with statistics
- Frontmatter properties listed
- Section hierarchy displayed
- Content blocks summary

**What to look for:**
- ✓ Formatted output with clear sections
- ✓ Property values shown correctly
- ✓ Section tree with proper nesting
- ✓ No errors

### Test /md-extract Command

**In Claude Code:**

```
/md-extract test-document.md json
```

**Expected output:**
- Complete JSON representation of document
- Includes `frontmatter` object
- Includes `content.sections` array
- Pretty-printed format

**Alternative:**

```
/md-extract test-document.md yaml
```

### Test /md-validate Command

First create a schema:

```bash
mddata schema generate test-document.md --output test-schema.json
```

**Then in Claude Code:**

```
/md-validate test-document.md test-schema.json
```

**Expected output:**
- Validation results
- Schema information
- Pass/fail status
- Any validation errors

### Test /md-update-property Command

**In Claude Code:**

```
/md-update-property test-document.md status "published"
```

**Expected behavior:**
1. Shows current frontmatter
2. Applies the change
3. Shows updated frontmatter
4. File is modified

**Verify:**

```bash
# Check the file was updated
grep "status:" test-document.md
# Should show: status: "published"
```

### Test /md-update-section Command

**In Claude Code:**

```
/md-update-section test-document.md introduction "This is updated introduction text."
```

**Expected behavior:**
1. Shows current section structure
2. Applies update with specified policy
3. Shows updated structure

**Verify:**

```bash
# Check the content was updated
mddata info sections test-document.md
```

### Test /md-generate-schema Command

**In Claude Code:**

```
/md-generate-schema test-document.md
```

**Expected output:**
- Schema in JSON format (default)
- Includes `frontmatter` definitions
- Includes `sections` structure
- Pretty-printed

**Alternative:**

```
/md-generate-schema test-document.md --format yaml
```

### Manual Command Verification

```bash
# List installed commands
ls -la ~/.claude/commands/md-*.md

# Check command file format
cat ~/.claude/commands/md-info.md | head -20

# Should show frontmatter with 'description' and bash commands with !`
```

## Agent Verification

The agent is invoked for complex transformation tasks.

### Test Agent Availability

**In Claude Code, ask:**

```
"I need to update all markdown files in this directory with a new version number"
```

**Expected behavior:**
- Claude may suggest using the markdown-data-engineer agent
- Agent should be available for invocation
- Claude discusses transformation strategy

### Test Agent Capabilities

**Create a transformation scenario:**

```
"I have a markdown file test-document.md. I need to:
1. Update the version to 2.0
2. Add a new property 'updated' with today's date
3. Append a changelog section

Can you help with this transformation?"
```

**Expected behavior:**
1. Agent analyzes the request
2. Plans transformation steps
3. Offers to create transformation JSON or direct commands
4. Executes transformation
5. Validates results

### Manual Agent Verification

```bash
# Check agent files are accessible
ls -la ~/.claude/agents/markdown-data-engineer/

# Verify AGENT.md exists and has proper frontmatter
cat ~/.claude/agents/markdown-data-engineer/AGENT.md | head -20

# Should show:
# ---
# name: markdown-data-engineer
# description: Expert agent for complex markdown...
# tools: Bash, Bash(mddata:*), Read, Write, Edit
# ---
```

## End-to-End Testing

Complete workflow testing all components together:

### Scenario 1: Document Analysis and Validation

```bash
# 1. Create test document (if not already created)
cat > workflow-test.md << 'EOF'
---
title: "API Documentation"
version: 1.0
status: "draft"
---

# Overview

This is API documentation.

## Authentication

Describes authentication methods.

## Endpoints

### GET /users

Returns user list.
EOF
```

**In Claude Code:**

```
Step 1: "Analyze workflow-test.md and tell me about its structure"
→ md-query skill should activate

Step 2: /md-generate-schema workflow-test.md
→ Generates schema

Step 3: "Generate a schema and save it to workflow-schema.json"
→ Creates schema file

Step 4: /md-validate workflow-test.md workflow-schema.json
→ Validates document

Step 5: "Update the status to 'published' and version to 2.0"
→ Agent or commands handle modification

Step 6: /md-info workflow-test.md
→ Verify changes
```

### Scenario 2: Bulk Transformation

```
"I need to create a template for all our API documentation.
Generate a schema from workflow-test.md, then create a new document
from that schema called new-api-doc.md"
```

**Expected:**
- Agent plans multi-step workflow
- Generates schema
- Creates new document from schema
- Validates result

## Troubleshooting

### Commands Not Found

**Symptom:** `/md-info` returns "command not found"

**Solutions:**

1. **Verify installation:**
   ```bash
   ls -la ~/.claude/commands/md-info.md
   ```

2. **Restart Claude Code** after installation

3. **Check file permissions:**
   ```bash
   chmod +r ~/.claude/commands/md-*.md
   ```

4. **Reinstall:**
   ```bash
   ./uninstall.sh global
   ./install.sh plugin global
   ```

### Skills Not Activating

**Symptom:** Claude doesn't use mddata for markdown questions

**Solutions:**

1. **Check skill installation:**
   ```bash
   ls -la ~/.claude/skills/md-query/SKILL.md
   cat ~/.claude/skills/md-query/SKILL.md | grep "^name:"
   ```

2. **Verify skill frontmatter is correct:**
   - Must have `---` delimiters
   - Must have `name:` and `description:` fields
   - File must be named `SKILL.md`

3. **Be more explicit in requests:**
   - Instead of: "What's in this file?"
   - Try: "Inspect the markdown file test-document.md and show me its structure"

4. **Restart Claude Code**

### mddata Command Errors

**Symptom:** "mddata: command not found" in Claude output

**Solutions:**

1. **Verify mddata is in PATH:**
   ```bash
   which mddata
   echo $PATH
   ```

2. **Test mddata directly:**
   ```bash
   mddata --version
   ```

3. **Check if using uv:**
   ```bash
   # If mddata requires uv, update tool definitions
   # Change "mddata" to "uv run mddata" in SKILL.md and command files
   ```

4. **Create alias or symlink:**
   ```bash
   # If mddata is installed via uv in specific project
   ln -s /home/omidev/Code/tools/mdasdata/bin/mddata ~/bin/mddata
   # Or add to PATH
   export PATH="/home/omidev/Code/tools/mdasdata/bin:$PATH"
   ```

### Agent Not Available

**Symptom:** Agent doesn't appear as option for complex tasks

**Solutions:**

1. **Check agent installation:**
   ```bash
   ls -la ~/.claude/agents/markdown-data-engineer/AGENT.md
   ```

2. **Verify agent frontmatter:**
   ```bash
   cat ~/.claude/agents/markdown-data-engineer/AGENT.md | head -10
   ```

   Should show:
   ```
   ---
   name: markdown-data-engineer
   description: Expert agent...
   tools: Bash, Bash(mddata:*), Read, Write, Edit
   ---
   ```

3. **Be explicit about needing complex transformation:**
   - "I need the markdown-data-engineer agent to help with bulk transformations"
   - "This is a complex markdown transformation task"

### Permission Errors

**Symptom:** "Permission denied" when running commands

**Solutions:**

1. **Fix file permissions:**
   ```bash
   chmod -R u+r ~/.claude/
   chmod +x install.sh uninstall.sh
   ```

2. **Check directory ownership:**
   ```bash
   ls -la ~/.claude/
   # Should be owned by your user
   ```

3. **Reinstall with proper permissions:**
   ```bash
   ./uninstall.sh global
   ./install.sh plugin global
   ```

## Verification Checklist

Use this checklist to verify complete installation:

### Installation

- [ ] `install.sh` executed without errors
- [ ] Symbolic links created successfully
- [ ] Links point to correct source directories
- [ ] No broken symlinks

### mddata Prerequisites

- [ ] `mddata --version` returns version number
- [ ] `mddata info summary test-document.md` works
- [ ] Test markdown file created and accessible

### Skills

- [ ] md-query skill file exists and readable
- [ ] md-schema skill file exists and readable
- [ ] Skills activate on appropriate user requests
- [ ] Skills execute mddata commands correctly

### Commands

- [ ] All 6 command files exist in commands directory
- [ ] `/md-info test-document.md` works
- [ ] `/md-extract test-document.md json` works
- [ ] `/md-validate` works with schema file
- [ ] `/md-update-property` modifies file correctly
- [ ] `/md-update-section` updates content
- [ ] `/md-generate-schema` produces valid schema

### Agent

- [ ] Agent directory exists and readable
- [ ] Agent AGENT.md has correct frontmatter
- [ ] Agent available for complex transformation tasks
- [ ] Agent can execute mddata commands
- [ ] Agent plans multi-step workflows correctly

### End-to-End

- [ ] Can analyze document structure
- [ ] Can generate and validate schemas
- [ ] Can modify documents
- [ ] Can perform complex transformations
- [ ] All components work together seamlessly

## Success Criteria

Your installation is successful if:

✅ **Skills work automatically** - Claude uses mddata for markdown questions
✅ **Commands execute** - All `/md-*` commands return results
✅ **Agent available** - Can invoke for complex tasks
✅ **mddata accessible** - Commands run without "not found" errors
✅ **Files modify correctly** - Updates actually change the markdown files
✅ **No permission errors** - All operations complete successfully

## Getting Help

If verification fails:

1. **Check this guide's troubleshooting section**
2. **Review INSTALL.md for installation details**
3. **Examine tool logs in Claude Code**
4. **Verify mddata installation independently**
5. **Try manual installation instead of scripts**
6. **Check file permissions and ownership**

## Quick Verification Commands

Run these commands for fast verification:

```bash
#!/bin/bash
# Quick verification script

echo "=== Checking Installation ==="
echo ""

echo "1. Checking mddata..."
if command -v mddata &> /dev/null; then
    echo "✓ mddata found: $(mddata --version)"
else
    echo "✗ mddata not found in PATH"
fi

echo ""
echo "2. Checking plugin installation..."
if [ -L ~/.claude/plugins/mddata-tools ]; then
    echo "✓ Plugin installed (symlink)"
    ls -la ~/.claude/plugins/mddata-tools
elif [ -d ~/.claude/plugins/mddata-tools ]; then
    echo "✓ Plugin installed (directory)"
else
    echo "✗ Plugin not found"
fi

echo ""
echo "3. Checking skills..."
for skill in md-query md-schema; do
    if [ -e ~/.claude/skills/$skill/SKILL.md ]; then
        echo "✓ Skill installed: $skill"
    else
        echo "✗ Skill missing: $skill"
    fi
done

echo ""
echo "4. Checking commands..."
cmd_count=$(ls ~/.claude/commands/md-*.md 2>/dev/null | wc -l)
echo "✓ Found $cmd_count commands"

echo ""
echo "5. Checking agent..."
if [ -e ~/.claude/agents/markdown-data-engineer/AGENT.md ]; then
    echo "✓ Agent installed: markdown-data-engineer"
else
    echo "✗ Agent missing"
fi

echo ""
echo "=== Verification Complete ==="
```

Save this as `verify.sh` and run it:

```bash
chmod +x verify.sh
./verify.sh
```

## Testing in Claude Code

After passing all checks, open Claude Code and try:

1. **Ask:** "What markdown tools do you have available?"
2. **Ask:** "Analyze test-document.md"
3. **Run:** `/md-info test-document.md`
4. **Ask:** "Help me transform this markdown file"

If all work correctly, your installation is verified! ✅
