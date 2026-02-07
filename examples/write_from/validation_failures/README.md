# Validation Failure Examples

Inputs designed to fail — useful for verifying error messages.

| Data file | Form | Expected error |
|-----------|------|----------------|
| `missing-required.json` | `../forms/project-doc.yaml` | Missing required parameter `project_name` |
| `invalid-enum.json` | `../forms/project-doc.yaml` | Value not in enum |
| `string-too-short.json` | `../combined/api-doc-form.yaml` | String below `min` length |
| `pattern-mismatch.json` | `../combined/api-doc-form.yaml` | Value doesn't match pattern |

## Run

```bash
mddata write --form ../forms/project-doc.yaml \
  --data missing-required.json -o /tmp/out.md

# Run all failures
for f in *.json; do
  echo "=== $f ==="
  mddata write --form ../forms/project-doc.yaml --data "$f" -o /tmp/out.md 2>&1 | head -3
done
```

Each should produce a clear error and create no output file.
