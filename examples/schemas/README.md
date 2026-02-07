# Example Schemas

Schemas generated from documents in `examples/`, in two inference modes.

## Files

**Permissive** (types + required fields only):
- `minimal_permissive.json`
- `simple_permissive.json`
- `complex_permissive.json`

**Strict** (adds defaults, length/pattern constraints, exact block counts):
- `minimal_strict.json`
- `simple_strict.json`
- `complex_strict.json`

## Run

```bash
# Generate (default mode is permissive)
mddata schema infer ../simple.md --output my_schema.json
mddata schema infer ../complex.md --inference-mode strict --output strict_schema.json

# Validate
mddata schema validate ../simple.md simple_permissive.json
mddata schema validate ../complex.md complex_strict.json --verbose

# Inspect a schema
mddata schema info simple_permissive.json
```

Use **permissive** for flexible documents, **strict** when structure must match exactly.
