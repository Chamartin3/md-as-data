# Data Transformation

## Overview

The `mddata write` command provides tools for programmatically modifying markdown documents:
- **Set properties** - Add or update frontmatter properties
- **Remove properties** - Delete frontmatter properties
- **Modify sections** - Update section content with different policies
- **Bulk operations** - Apply multiple changes from JSON

## Command Structure

```bash
mddata write <subcommand> <file_path> [arguments] [options]
```

**Important:** All modify commands update the file in-place. Always backup important files or use version control.

## Property Operations

### Set Property

Add or update a frontmatter property:

```bash
mddata write set-property document.md <property_name> <value>
```

**Example - Simple string:**
```bash
mddata write set-property document.md title "Updated Title"
```

**Before:**
```markdown
---
title: "Old Title"
---
```

**After:**
```markdown
---
title: "Updated Title"
---
```

**Example - Number:**
```bash
mddata write set-property document.md version 2.0
```

**Example - Boolean:**
```bash
mddata write set-property document.md published true
```

**Example - Complex values (JSON):**

For arrays, objects, or special values, use `--json` flag:

```bash
mddata write set-property document.md tags '["api", "guide", "v2"]' --json
```

```bash
mddata write set-property document.md author '{"name": "John Doe", "email": "john@example.com"}' --json
```

```bash
mddata write set-property document.md config '{"timeout": 30, "retry": true}' --json
```

**Result:**
```markdown
---
title: "Updated Title"
version: 2.0
published: true
tags: ["api", "guide", "v2"]
author:
  name: "John Doe"
  email: "john@example.com"
config:
  timeout: 30
  retry: true
---
```

### Remove Property

Delete a frontmatter property:

```bash
mddata write remove-property document.md <property_name>
```

**Example:**
```bash
mddata write remove-property document.md draft
```

**Before:**
```markdown
---
title: "Document"
draft: true
version: 1.0
---
```

**After:**
```markdown
---
title: "Document"
version: 1.0
---
```

### Property Types

Values are automatically typed based on format:

| Input | Type | Example |
|-------|------|---------|
| `"text"` | String | `mddata write set-property doc.md name "John"` |
| `42` | Integer | `mddata write set-property doc.md count 42` |
| `3.14` | Float | `mddata write set-property doc.md pi 3.14` |
| `true`/`false` | Boolean | `mddata write set-property doc.md active true` |
| `'[1,2,3]' --json` | Array | `mddata write set-property doc.md nums '[1,2,3]' --json` |
| `'{"k":"v"}' --json` | Object | `mddata write set-property doc.md obj '{"k":"v"}' --json` |

## Section Operations

### Set Section Content

Update or create section content:

```bash
mddata write set-section document.md <section_id> <content>
```

**Example - Update existing section:**
```bash
mddata write set-section document.md introduction "This is the updated introduction text."
```

**Before:**
```markdown
# Introduction

Old introduction text.

# Configuration

Setup instructions.
```

**After:**
```markdown
# Introduction

This is the updated introduction text.

# Configuration

Setup instructions.
```

### Section Policies

Control how content is merged using `--policy`:

#### UPDATE Policy (Default)

Merges content while preserving subsections:

```bash
mddata write set-section document.md introduction "New intro content"
# Same as:
mddata write set-section document.md introduction "New intro content" --policy update
```

**Before:**
```markdown
# Introduction

Old content.

## Overview

Overview subsection.
```

**After:**
```markdown
# Introduction

New intro content.

## Overview

Overview subsection.
```

**Behavior:**
- Replaces section's direct content
- Preserves all subsections unchanged
- Maintains heading level and title

#### REPLACE Policy

Completely replaces section including all subsections:

```bash
mddata write set-section document.md introduction "Fresh start." --policy replace
```

**Before:**
```markdown
# Introduction

Old content.

## Overview

Overview subsection.

## Details

Details subsection.
```

**After:**
```markdown
# Introduction

Fresh start.
```

**Behavior:**
- Removes all existing content
- Removes all subsections
- Starts with fresh content
- Maintains heading level and title

#### APPEND Policy

Adds content to the end of existing content:

```bash
mddata write set-section document.md notes "Additional note." --policy append
```

**Before:**
```markdown
# Notes

First note.

Second note.
```

**After:**
```markdown
# Notes

First note.

Second note.

Additional note.
```

**Behavior:**
- Keeps all existing content
- Adds new content after existing
- Preserves subsections
- Maintains heading level and title

### Creating New Sections

#### Top-Level Section

```bash
mddata write set-section document.md new_section "This is new content."
```

**Before:**
```markdown
# Introduction

Existing content.
```

**After:**
```markdown
# Introduction

Existing content.

# New Section

This is new content.
```

**Auto-generated:**
- Section ID: `new_section`
- Title: "New Section" (from ID)
- Level: 1 (top-level)

#### Subsection (Nested)

Use dot notation to create nested sections:

```bash
mddata write set-section document.md introduction.overview "Overview content."
```

**Before:**
```markdown
# Introduction

Introduction text.
```

**After:**
```markdown
# Introduction

Introduction text.

## Overview

Overview content.
```

**Auto-generated:**
- Section ID: `overview`
- Path: `introduction.overview`
- Title: "Overview" (from ID)
- Level: 2 (parent level + 1)

#### Deep Nesting

```bash
mddata write set-section document.md intro.getting_started.prerequisites "You need Python 3.8+."
```

**Result:**
```markdown
# Intro

## Getting Started

### Prerequisites

You need Python 3.8+.
```

**Requirements:**
- Parent sections must exist
- Each level increments heading level
- Automatic title generation from ID

### Path-Based Section Access

Access sections using dot-separated paths:

```bash
# Top-level section
mddata write set-section document.md configuration "Config content."

# Second-level nested
mddata write set-section document.md configuration.database "DB settings."

# Third-level nested
mddata write set-section document.md configuration.database.connection "Connection details."
```

**Result structure:**
```
configuration              (level 1: #)
  database                 (level 2: ##)
    connection             (level 3: ###)
```

### Section ID Rules

Section IDs follow these conventions:

1. **Lowercase**: "Getting Started" → `getting_started`
2. **Underscores**: Spaces become underscores
3. **Alphanumeric**: Special characters removed
4. **Collapsed spaces**: Multiple spaces → single underscore

**Examples:**

| Desired Title | Section ID |
|---------------|------------|
| Introduction | `introduction` |
| Getting Started | `getting_started` |
| API v2.0 | `api_v2_0` |
| FAQ & Support | `faq_support` |

## Practical Examples

### Example 1: Publishing Workflow

```bash
# Update status to published
mddata write set-property article.md status "published"

# Set publication date
mddata write set-property article.md published_date "2025-10-23"

# Add publishing tags
mddata write set-property article.md tags '["published", "featured"]' --json

# Update version
mddata write set-property article.md version 1.0
```

### Example 2: Content Update

```bash
# Update introduction
mddata write set-section guide.md introduction "Welcome to version 2.0 of our guide."

# Add new section
mddata write set-section guide.md whats_new "Version 2.0 introduces several new features."

# Update changelog section
mddata write set-section guide.md changelog "## Version 2.0\n- New feature A\n- New feature B" --policy append
```

### Example 3: Document Restructuring

```bash
# Replace entire section with new structure
mddata write set-section document.md api_reference "See the new API documentation." --policy replace

# Create new subsections
mddata write set-section document.md api_reference.authentication "Authentication details here."
mddata write set-section document.md api_reference.endpoints "Endpoint documentation here."
mddata write set-section document.md api_reference.examples "Example usage here."
```

### Example 4: Metadata Management

```bash
# Update author information
mddata write set-property doc.md author '{"name": "Jane Smith", "role": "Technical Writer"}' --json

# Add review status
mddata write set-property doc.md review '{"status": "approved", "reviewer": "John Doe", "date": "2025-10-23"}' --json

# Remove outdated property
mddata write remove-property doc.md draft
```

### Example 5: Batch Updates

```bash
# Update all documents in folder
for doc in docs/*.md; do
  mddata write set-property "$doc" last_updated "2025-10-23"
  mddata write set-property "$doc" version 2.0
done
```

### Example 6: Conditional Updates

```bash
# Only update if draft
if grep -q "draft: true" document.md; then
  mddata write set-property document.md status "review"
  mddata write set-section document.md review_notes "Ready for review."
fi
```

### Example 7: Migration Script

```bash
#!/bin/bash
# migrate-docs.sh - Update all docs to new schema

for doc in docs/**/*.md; do
  echo "Processing: $doc"

  # Update schema version
  mddata write set-property "$doc" schema_version 2.0

  # Add required new property
  mddata write set-property "$doc" category "general"

  # Remove deprecated property
  mddata write remove-property "$doc" legacy_field

  # Update standard sections
  mddata write set-section "$doc" prerequisites "See installation guide."
done

echo "Migration complete!"
```

## Common Transformations

### 1. Version Bump

```bash
# Increment version
mddata write set-property doc.md version 2.1

# Update changelog
mddata write set-section doc.md changelog "## v2.1\n- Bug fixes\n- Performance improvements" --policy append
```

### 2. Status Changes

```bash
# Move through workflow states
mddata write set-property doc.md status "draft"
mddata write set-property doc.md status "review"
mddata write set-property doc.md status "approved"
mddata write set-property doc.md status "published"
```

### 3. Tag Management

```bash
# Add tags
mddata write set-property doc.md tags '["python", "tutorial"]' --json

# Update tags
mddata write set-property doc.md tags '["python", "tutorial", "advanced"]' --json

# Remove tags
mddata write remove-property doc.md tags
```

### 4. Content Refresh

```bash
# Update timestamp
mddata write set-property doc.md last_modified "$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Add update note
mddata write set-section doc.md update_history "Updated on $(date +%Y-%m-%d)" --policy append
```

### 5. Structure Expansion

```bash
# Add new sections to existing document
mddata write set-section doc.md troubleshooting "Common issues and solutions."
mddata write set-section doc.md troubleshooting.common_errors "Error messages explained."
mddata write set-section doc.md troubleshooting.debugging "Debugging techniques."
```

## Policy Comparison

| Use Case | Policy | Behavior |
|----------|--------|----------|
| Update content, keep subsections | `update` | Replace blocks, keep subsections |
| Fresh start, remove everything | `replace` | Delete all content and subsections |
| Add to existing content | `append` | Add content after existing |
| Default behavior | (none) | Same as `update` |

**Example scenario:**

```markdown
# Documentation

This is the main documentation.

## Installation

How to install.

## Usage

How to use.
```

**Commands and results:**

```bash
# UPDATE: Keep subsections
mddata write set-section doc.md documentation "New main text." --policy update
```
Result: Main text changes, Installation and Usage preserved

```bash
# REPLACE: Remove everything
mddata write set-section doc.md documentation "Start over." --policy replace
```
Result: Only "Start over." remains, subsections gone

```bash
# APPEND: Add to end
mddata write set-section doc.md documentation "More info." --policy append
```
Result: Original text + "More info.", subsections preserved

## Error Handling

### Property Errors

**Invalid JSON:**
```bash
mddata write set-property doc.md config '{invalid}' --json
```
```
Error: Invalid JSON format: Expecting property name enclosed in double quotes
```

### Section Errors

**Parent doesn't exist:**
```bash
mddata write set-section doc.md nonexistent.child "Content"
```
```
Error: Parent section 'nonexistent' not found
Cannot create subsection 'child'
```

**Ambiguous section:**
```bash
mddata write set-section doc.md intro "New content"
```
```
Error: Ambiguous section reference 'intro'
Matches:
  - introduction (path: introduction)
  - intro_guide (path: intro_guide)

Use full path to specify:
  - mddata write set-section doc.md introduction "content"
  - mddata write set-section doc.md intro_guide "content"
```

## Best Practices

### 1. Use Version Control

Always commit before bulk modifications:
```bash
git commit -am "Before modifications"
mddata write set-property doc.md status "published"
git diff doc.md  # Review changes
```

### 2. Test on Copies

Test transformations on copies first:
```bash
cp document.md document.backup.md
mddata write set-section document.md section "Test content"
# Verify results
rm document.backup.md
```

### 3. Script Complex Operations

For multiple changes, use scripts:
```bash
#!/bin/bash
# update-doc.sh
DOC="$1"

mddata write set-property "$DOC" updated "$(date +%Y-%m-%d)"
mddata write set-property "$DOC" version 2.0
mddata write set-section "$DOC" changes "Updated to v2.0" --policy append
```

### 4. Validate After Changes

Check document structure after modifications:
```bash
mddata write set-property doc.md status "published"
mddata info summary doc.md
mddata schema validate doc.md schema.json
```

### 5. Use Policies Appropriately

- `update`: Default for content changes
- `replace`: Only when rebuilding entire sections
- `append`: For logs, changelogs, history sections

## Next Steps

- [Complex transformations](07-complex-transformations.md) - Bulk operations from JSON
- [Schema validation](04-schema-management.md) - Validate changes
- [Extract and regenerate](03-extracting-metadata.md) - Round-trip workflows
