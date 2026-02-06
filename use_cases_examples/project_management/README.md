# Project Management Use Case (MDForm-based)

This example demonstrates using mddata with markdown forms for project planning and tracking.

## Overview

This use case shows how to:
- Define parameterized forms for project documents
- Use parameter validation and enums
- Create documents with nested lists and milestones
- Fill forms with different parameter sources
- Handle computed parameters (dates, environment variables)

## Files in this example

- `project_form.yaml` - Markdown form template with parameters
- `sample_params.json` - Example parameters for filling the form
- `sample_project.md` - Example generated project document
- `team_params.json` - Different parameter set for team projects

## Form Structure

The project form includes:

### Parameters
- `project_name` (required string, min 3 chars)
- `project_type` (enum: internal, client, research)
- `priority` (enum: low, medium, high, critical)
- `start_date` (computed from current date if not provided)
- `end_date` (required string, ISO date format)
- `project_manager` (string, defaults to environment USER)
- `team_size` (integer, min 1, max 50)
- `budget` (number, optional)
- `milestones` (array of milestone objects)
- `risks` (array of strings)

### Document Sections
- **Project Overview**
- **Team & Resources**
  - **Team Members**
  - **Budget Allocation**
- **Milestones & Timeline**
- **Risks & Mitigation**
- **Status Updates**

## Step-by-step Usage

### 1. View Form Structure

```bash
# View the form template
cat project_form.yaml

# Check form validation rules
mddata info properties project_form.yaml
```

### 2. Fill Form with Parameters

```bash
# Fill form using parameter file
mddata write --form project_form.yaml --params sample_params.json --output new_project.md

# Fill form using CLI parameters
mddata write --form project_form.yaml \
  -p project_name="Mobile App Redesign" \
  -p project_type="client" \
  -p priority="high" \
  -p end_date="2024-06-30" \
  -p team_size=8 \
  --output mobile_project.md

# Fill form with computed parameters (uses current date and $USER)
mddata write --form project_form.yaml \
  -p project_name="Quick Fix" \
  -p project_type="internal" \
  -p priority="medium" \
  -p end_date="2024-02-15" \
  -p team_size=3 \
  --output quick_fix.md
```

### 3. Update Existing Project Documents

```bash
# Update project status
mddata write set-property new_project.md status "in-progress"

# Add new team member
mddata write set-section new_project.md "team-members" \
  "- John Smith (Designer)\n- Jane Doe (Developer)\n- Mike Wilson (QA)" \
  --policy replace

# Add status update
mddata write set-section new_project.md "status-updates" \
  "## Week 1 (Jan 15-19)\n- Completed initial planning\n- Set up development environment\n- Created project timeline" \
  --policy append
```

### 4. Validate Form Data

```bash
# Test with invalid parameters (should fail)
mddata write --form project_form.yaml \
  -p project_name="ab" \
  -p project_type="invalid" \
  -p team_size=100 \
  --output invalid_project.md
```

### 5. Extract Project Data

```bash
# Extract to JSON for reporting
mddata extract json new_project.md --pretty --output project_data.json

# Extract only frontmatter for dashboard
mddata extract frontmatter new_project.md --format json
```

### 6. Query Project Information

```bash
# View project structure
mddata info sections new_project.md

# Check project metadata
mddata info properties new_project.md

# Find specific content blocks
mddata info blocks new_project.md
```

## Key Features Demonstrated

1. **Parameter Validation**: Rich validation rules for form fields
2. **Computed Parameters**: Automatic date and environment variable injection
3. **Nested Lists**: Structured milestones and team member lists
4. **Enumerations**: Controlled vocabularies for project types and priorities
5. **Array Parameters**: Lists of milestones, risks, and team members
6. **Default Values**: Sensible defaults for optional parameters
7. **Multi-source Parameters**: CLI, files, and computed sources
8. **Form Reusability**: Same form for different project types