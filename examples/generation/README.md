# Generation Examples

Generate markdown from schemas, data, or both using `mddata write`.

## Files

- `blog_post_schema.json` — JSON schema for blog posts (with defaults)
- `project_spec_schema.yaml` — YAML schema for project specs
- `blog_post_data.json` — complete blog post data
- `simple_note_data.json` — meeting notes data (no schema)
- `invalid_data.json` — data that intentionally fails `blog_post_schema`

## Run

```bash
# Template from schema (uses defaults)
mddata write --schema blog_post_schema.json --output blog_template.md
mddata write --schema project_spec_schema.yaml --output project_template.md

# Document from data
mddata write --data blog_post_data.json --output blog_post.md
mddata write --data simple_note_data.json --output meeting_notes.md

# Data + schema validation
mddata write --data blog_post_data.json --schema blog_post_schema.json --output validated.md

# stdin pipeline
cat blog_post_data.json | mddata write --data - --output from_stdin.md

# Force overwrite
mddata write --schema blog_post_schema.json --output blog_template.md --force
```

## See also

- [docs/CLI_REFERENCE.md](../../docs/CLI_REFERENCE.md)
- [../schemas/](../schemas/)
