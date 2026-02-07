# Project Management — Forms

Parameterized form for project planning docs.

## Files

- `project_form.yaml` — form template
- `sample_params.json`, `team_params.json` — example params
- `sample_project.md` — example output

## Form parameters

- `project_name` (str, min 3, required)
- `project_type` (enum: internal, client, research)
- `priority` (enum: low, medium, high, critical)
- `start_date` (computed if omitted)
- `end_date` (ISO date, required)
- `project_manager` (defaults to `$USER`)
- `team_size` (int, 1–50)
- `budget` (number, optional)
- `milestones` (array of objects)
- `risks` (array of strings)

## Run

```bash
# From params file
mddata write --form project_form.yaml --params sample_params.json --output new_project.md

# From CLI params
mddata write --form project_form.yaml \
  -p project_name="Mobile App Redesign" \
  -p project_type=client -p priority=high \
  -p end_date=2024-06-30 -p team_size=8 \
  --output mobile_project.md

# Update an existing doc
mddata write set-property new_project.md status in-progress
mddata write set-section new_project.md status-updates \
  "## Week 1\n- Planning complete" --policy append

# Extract
mddata extract json new_project.md --pretty --output project_data.json
mddata extract frontmatter new_project.md --format json
```
