---
name: markdown-datatemplate-composer
description: Split large markdown datatemplates into smaller modular components and compose them together. Update template sections independently, manage template libraries, and create reusable partial templates. Use when managing complex datatemplates, creating modular template systems, or updating specific template sections without affecting others.
version: 1.0.0
keywords:
  - markdown datatemplates
  - template composition
  - template splitting
  - modular templates
  - partial templates
  - template libraries
  - section updates
  - template reusability
  - MarkdownDataUpdate
  - template management
  - component templates
  - template organization
allowed_tools:
  - Read
  - Write
  - Edit
  - Bash
  - "mddata extract"
  - "mddata write"
  - "mddata modify"
  - "mddata info"
---
# Markdown Datatemplate Composer

## Purpose

Help users split complex markdown datatemplates into smaller, manageable components and compose them together. Enables modular template design where common sections can be reused across multiple templates, specific sections can be updated independently, and template libraries can be organized efficiently. Supports both splitting existing templates and composing new templates from partial components.

## When to Use This Skill

Use this skill when you need to:

1. **Split large datatemplates** - Break down complex templates into manageable parts
2. **Create template libraries** - Build collections of reusable template components
3. **Update sections independently** - Modify specific template sections without full rewrites
4. **Compose templates** - Build new templates from existing partial templates
5. **Maintain modular systems** - Manage templates that share common sections
6. **Organize template collections** - Structure template directories efficiently

## Instructions

### 1. Analyze Template for Splitting Opportunities

Identify sections that can be extracted as independent components:

**Candidates for splitting:**
- Common sections used across multiple templates (headers, footers, changelogs)
- Large, self-contained sections (detailed requirements, testing procedures)
- Frequently updated sections (status updates, version history)
- Reusable parameter groups (author info, date fields, metadata)

**Example analysis:**

```bash
# Inspect existing template structure
mddata info sections large-template.yaml --paths --blocks

# Extract to see full structure
mddata extract yaml large-template.yaml --output large-template-extracted.yaml

# Identify:
# - Sections with 10+ blocks (candidates for extraction)
# - Repeated patterns across multiple templates
# - Sections that change frequently
```

### 2. Extract Sections into Partial Templates

Create focused partial templates for specific sections:

**Extract common header section:**

```yaml
# templates/partials/common-header.yaml
parameters:
  title:
    type: str
    required: true
    min: 5
    max: 100
  author:
    type: str
    required: false
    default: "{env.USER}"
  version:
    type: str
    required: false
    default: "1.0.0"
    pattern: "^\\d+\\.\\d+\\.\\d+$"

frontmatter:
  title: "{title}"
  author: "{author}"
  version: "{version}"
  created: "{date}"

sections:
  - id: header
    content: |
      # {title}

      **Version**: {version}
      **Author**: {author}
      **Created**: {date}
```

**Extract changelog section:**

```yaml
# templates/partials/changelog-section.yaml
parameters:
  version:
    type: str
    required: true
  changes:
    type: array
    item_type: str
    required: true
    min_items: 1

sections:
  - id: changelog
    content: |
      ## Changelog

      ### Version {version} - {date}

      {changes}
    policy: append  # Always append when composing
```

### 3. Compose Templates from Partials

Combine partial templates to create complete templates:

**Method 1: Manual composition with extraction**

```bash
# Extract all partials
mddata extract yaml templates/partials/common-header.yaml > /tmp/header.yaml
mddata extract yaml templates/partials/changelog-section.yaml > /tmp/changelog.yaml
mddata extract yaml templates/partials/details-section.yaml > /tmp/details.yaml

# Manually merge into single template file
# (Combine parameters, frontmatter, and sections)
```

**Method 2: Create composite template with references**

```yaml
# templates/bug-report.yaml
# Composite template - combines multiple partial templates

parameters:
  # From common-header.yaml
  title:
    type: str
    required: true
  author:
    type: str
    required: false
    default: "{env.USER}"

  # From bug-specific section
  severity:
    type: str
    required: true
    enum: [critical, high, medium, low]
    enum_strict: true

  # From changelog partial
  version:
    type: str
    required: true
  changes:
    type: array
    required: true

frontmatter:
  title: "{title}"
  author: "{author}"
  severity: "{severity}"
  version: "{version}"
  created: "{date}"

sections:
  # Header section (from common-header partial)
  - id: header
    content: |
      # {title}

      **Version**: {version}
      **Author**: {author}

  # Bug-specific content
  - id: bug_details
    content: |
      ## Bug Details

      **Severity**: {severity}

  # Changelog section (from changelog partial)
  - id: changelog
    content: |
      ## Changelog

      ### Version {version} - {date}

      {changes}
```

### 4. Update Specific Template Sections

Modify individual sections without affecting the rest:

**Update only the changelog section:**

```json
{
  "_comment": "updates/add-changelog-entry.json",
  "content": {
    "children": [
      {
        "id": "changelog",
        "policy": "append",
        "children": [
          {
            "title": "Version 1.2.0 - 2025-10-26",
            "level": 3,
            "blocks": [
              {
                "type": "list",
                "content": "- Fixed critical security issue\n- Added new authentication method\n- Improved performance by 40%"
              }
            ]
          }
        ]
      }
    ]
  }
}
```

**Apply the update:**

```bash
# Update existing bug report template
mddata write --data updates/add-changelog-entry.json \
  templates/bug-report.json \
  --policy append
```

**Update parameters without changing content:**

```json
{
  "_comment": "updates/enhance-validation.json",
  "parameters": {
    "severity": {
      "type": "str",
      "required": true,
      "enum": ["critical", "high", "medium", "low"],
      "enum_strict": true,
      "enum_descriptions": {
        "critical": "System down, immediate fix",
        "high": "Major feature broken",
        "medium": "Minor feature issue",
        "low": "Cosmetic or enhancement"
      }
    }
  }
}
```

### 5. Organize Template Library

Structure templates for maintainability:

**Recommended structure:**

```
templates/
├── partials/           # Reusable components
│   ├── common-header.yaml
│   ├── changelog-section.yaml
│   ├── metadata-section.yaml
│   ├── footer-section.yaml
│   └── status-section.yaml
├── complete/           # Full templates ready to use
│   ├── bug-report.yaml
│   ├── feature-request.yaml
│   ├── meeting-notes.yaml
│   └── project-spec.yaml
├── updates/            # Section-specific updates
│   ├── add-changelog.yaml
│   ├── update-status.yaml
│   └── enhance-validation.yaml
└── README.md           # Template library documentation
```

### 6. Test Composition and Updates

Verify that partial templates work correctly when composed:

```bash
# Test partial template independently
mddata write --data templates/partials/common-header.yaml \
  -p title="Test Document" \
  -p author="Test User" \
  --output /tmp/partial-test.md

# Test full composed template
mddata write --data templates/complete/bug-report.yaml \
  -p title="Login Bug" \
  -p severity=critical \
  -p 'changes=["Fixed issue"]' \
  --output /tmp/composed-test.md

# Test section update
mddata write --data templates/updates/add-changelog.yaml \
  /tmp/composed-test.md \
  --policy append \
  --dry-run
```

## Examples

### Example 1: Splitting a Large Template

**Original large template:**

```yaml
# templates/comprehensive-spec.yaml (200+ lines)
parameters:
  # 15 different parameters
  # ...

frontmatter:
  # Multiple properties
  # ...

sections:
  - id: header
    # ...
  - id: overview
    # ...
  - id: requirements
    # ...
  - id: architecture
    # ...
  - id: testing
    # ...
  - id: deployment
    # ...
  - id: changelog
    # ...
```

**Split into partials:**

```bash
# Extract header (common across all specs)
# Create templates/partials/spec-header.yaml
# Contains: title, author, version parameters + header section

# Extract requirements section (reusable)
# Create templates/partials/requirements-section.yaml
# Contains: requirements-specific parameters + requirements section

# Extract changelog (frequently updated)
# Create templates/partials/changelog-section.yaml
# Contains: version, changes parameters + changelog section
```

**Composed template:**

```json
{
  "_comment": "templates/complete/project-spec.json (much simpler!)",
  "_comment2": "References partials conceptually through shared structure",
  "parameters": {
    "title": {
      "type": "str",
      "required": true,
      "description": "Project title (from spec-header partial)"
    },
    "author": {
      "type": "str",
      "default": "{env.USER}",
      "description": "Author name (from spec-header partial)"
    },
    "project_type": {
      "type": "str",
      "enum": ["web", "mobile", "api", "library"],
      "description": "Project-specific parameter"
    }
  },
  "frontmatter": {
    "title": "{title}",
    "author": "{author}",
    "type": "{project_type}"
  },
  "content": {
    "children": [
      {
        "id": "header",
        "title": "{title}",
        "level": 1,
        "blocks": []
      },
      {
        "id": "project_details",
        "title": "Project Details",
        "level": 2,
        "blocks": [
          {
            "type": "paragraph",
            "content": "**Type**: {project_type}"
          }
        ]
      }
    ]
  }
}
```

### Example 2: Creating a Template Library

**Setup:**

```bash
# Create library structure
mkdir -p templates/{partials,complete,updates}

# Create common header partial
cat > templates/partials/doc-header.yaml << 'EOF'
parameters:
  title:
    type: str
    required: true
  author:
    type: str
    default: "{env.USER}"

sections:
  - id: header
    content: |
      # {title}

      **Author**: {author}
      **Date**: {date}
EOF

# Create status section partial
cat > templates/partials/status-section.yaml << 'EOF'
parameters:
  status:
    type: str
    enum: [draft, review, approved, published]
    enum_descriptions:
      draft: "Work in progress"
      review: "Under review"
      approved: "Approved, pending publication"
      published: "Live and published"

sections:
  - id: status
    content: |
      ## Status

      **Current Status**: {status}
      **Last Updated**: {date}
EOF
```

**Compose templates using partials:**

```json
{
  "_comment": "templates/complete/design-doc.json",
  "_comment2": "Uses doc-header + status-section partials",
  "parameters": {
    "title": {
      "type": "str",
      "required": true
    },
    "author": {
      "type": "str",
      "default": "{env.USER}"
    },
    "status": {
      "type": "str",
      "enum": ["draft", "review", "approved", "published"]
    }
  },
  "frontmatter": {
    "title": "{title}",
    "author": "{author}",
    "status": "{status}"
  },
  "content": {
    "children": [
      {
        "id": "header",
        "title": "{title}",
        "level": 1,
        "blocks": [
          {
            "type": "paragraph",
            "content": "**Author**: {author}\n**Date**: {date}"
          }
        ]
      },
      {
        "id": "status",
        "title": "Status",
        "level": 2,
        "blocks": [
          {
            "type": "paragraph",
            "content": "**Current Status**: {status}"
          }
        ]
      },
      {
        "id": "design",
        "title": "Design",
        "level": 2,
        "children": [
          {
            "id": "overview",
            "title": "Overview",
            "level": 3,
            "blocks": []
          },
          {
            "id": "architecture",
            "title": "Architecture",
            "level": 3,
            "blocks": []
          }
        ]
      }
    ]
  }
}
```

### Example 3: Independent Section Updates

**Scenario:** Update changelog across multiple templates

**Create update partial:**

```json
{
  "_comment": "templates/updates/add-release-notes.json",
  "content": {
    "children": [
      {
        "id": "changelog",
        "policy": "append",
        "children": [
          {
            "title": "Version 2.0.0 - 2025-10-26",
            "level": 3,
            "blocks": [
              {
                "type": "paragraph",
                "content": "**Major Release**"
              },
              {
                "type": "list",
                "content": "- New authentication system\n- Improved performance\n- Breaking changes: see migration guide"
              }
            ]
          }
        ]
      }
    ]
  }
}
```

**Apply to multiple templates:**

```bash
# Update all bug report templates
for file in documents/bugs/bug-*.md; do
  mddata write --data templates/updates/add-release-notes.yaml \
    "$file" \
    --policy append
done

# Update all feature specifications
for file in documents/features/feature-*.md; do
  mddata write --data templates/updates/add-release-notes.yaml \
    "$file" \
    --policy append
done
```

## Additional Notes

### Best Practices for Template Composition

1. **Keep partials focused** - Each partial should have a single, clear purpose
2. **Use consistent naming** - Name partials by function (header, footer, changelog)
3. **Document dependencies** - Note which partials are used by which templates
4. **Version partials independently** - Track versions for breaking changes
5. **Test partials in isolation** - Verify each partial works before composing
6. **Minimize parameter overlap** - Avoid parameter name conflicts between partials
7. **Use policy flags wisely** - Understand merge, replace, update, append behaviors
8. **Organize by reusability** - Group highly reusable partials separately

### Common Composition Patterns

**Pattern 1: Header + Content + Footer**

```
[common-header.yaml] + [specific-content.yaml] + [common-footer.yaml]
= Complete document template
```

**Pattern 2: Base + Extensions**

```
[base-template.yaml] + [extension-1.yaml] + [extension-2.yaml]
= Extended template with additional sections
```

**Pattern 3: Core + Variants**

```
[core-params.yaml] + [variant-web.yaml] = Web template
[core-params.yaml] + [variant-mobile.yaml] = Mobile template
```

### Section Update Policies

- **merge** (default): Combine new content with existing, preserve subsections
- **replace**: Completely replace section content
- **append**: Add new content after existing content
- **update**: Update content while preserving structure

### Template Library Documentation

Create README.md in templates directory:

```markdown
# Template Library

## Partials

- `doc-header.yaml` - Standard document header with title, author, date
- `status-section.yaml` - Status tracking section with enum validation
- `changelog-section.yaml` - Versioned changelog section

## Complete Templates

- `bug-report.yaml` - Bug tracking template (uses: doc-header, status-section)
- `feature-request.yaml` - Feature request template (uses: doc-header, changelog-section)

## Updates

- `add-release-notes.yaml` - Append release notes to changelog section
- `update-status.yaml` - Update document status

## Usage Examples

### Create bug report
```bash
mddata write --data templates/complete/bug-report.yaml \
  -p title="Bug title" \
  -p severity=high \
  --output bugs/bug-001.md
```

### Update status
```bash
mddata write --data templates/updates/update-status.yaml \
  bugs/bug-001.md \
  -p status=review
```
```

### References

- **markdown-datatemplate-validator skill** - Validate template structure and parameters
- **markdown-writer skill** - Template usage and workflows
- **mddata-inspect skill** - Template inspection techniques
- **TEMPLATES.md** - Complete template documentation
