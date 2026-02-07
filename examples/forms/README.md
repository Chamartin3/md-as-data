# Form Examples

Parameterized markdown templates with typed validation. Full reference: [docs/MARKDOWN_FORMS.md](../../docs/MARKDOWN_FORMS.md).

## Files

**Raw markdown format** (content includes headings):
- `log-entry.yaml` — simple params + computed `{date}`
- `meeting-notes.yaml` — array parameters
- `bug-report.yaml` — enum, min/max, env defaults

**Structured format** (recommended — title/level separate from content):
- `meeting-structured.yaml`
- `log-entry-structured.yaml`

## Run

```bash
# Fill via CLI params
mddata write --form log-entry.yaml \
  -p title="Fixed auth bug" -p category=bugfix -p content="Updated JWT" \
  --output changelog.md

# Fill via stdin JSON
echo '{"title":"Fixed auth bug","category":"bugfix","content":"Updated JWT"}' | \
  mddata write --form log-entry.yaml --data - --output changelog.md

# Array params (JSON-encoded)
mddata write --form meeting-notes.yaml \
  -p title="Sprint Planning" \
  -p 'attendees=["Alice","Bob"]' \
  -p 'action_items=["Update docs"]' \
  --output meeting.md

# Constrained params (enum, min/max)
mddata write --form bug-report.yaml \
  -p title="Login 500" -p severity=critical -p priority=1 \
  -p description="The /api/auth/login endpoint fails" \
  --output bug-001.md
```

## Form structure

```yaml
parameters:
  name:
    type: str | int | float | bool | array
    required: true
    default: "..."
    min: 1
    max: 100
    pattern: "^[A-Z]"
    enum: [a, b, c]
    item_type: str   # for arrays

frontmatter:
  field: "{name}"

sections:
  - id: section_id
    title: "Optional - {name}"
    level: 2
    content: |
      Content with {placeholders}
    policy: append | replace | update
```

## Computed params

`{date}`, `{time}`, `{now}`, `{env.USER}` — always available.
