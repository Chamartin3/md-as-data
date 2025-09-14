#!/bin/bash
# Schema Generation & Validation Demo Script

echo "════════════════════════════════════════════════════════════════"
echo "  Schema Generation & Validation - Interactive Demo"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Demo 1: Generate permissive schema
echo "━━━ Demo 1: Generate Permissive Schema (Minimal) ━━━"
echo "Command: uv run mdasdata examples/simple.md schema generate --output /tmp/demo_permissive.json"
uv run mdasdata examples/simple.md schema generate --output /tmp/demo_permissive.json
echo ""
echo "Schema section example (no validation):"
jq '.sections.introduction' /tmp/demo_permissive.json
echo ""

# Demo 2: Generate strict schema
echo "━━━ Demo 2: Generate Strict Schema (Exact Constraints) ━━━"
echo "Command: uv run mdasdata examples/simple.md schema generate --inference-mode strict --output /tmp/demo_strict.json"
uv run mdasdata examples/simple.md schema generate --inference-mode strict --output /tmp/demo_strict.json
echo ""
echo "Schema section example (with validation):"
jq '.sections.introduction' /tmp/demo_strict.json
echo ""

# Demo 3: Compare sizes
echo "━━━ Demo 3: Size Comparison ━━━"
echo "Permissive schema: $(wc -c < /tmp/demo_permissive.json) bytes"
echo "Strict schema:     $(wc -c < /tmp/demo_strict.json) bytes"
echo "Reduction: $((100 - ($(wc -c < /tmp/demo_permissive.json) * 100 / $(wc -c < /tmp/demo_strict.json))))% smaller"
echo ""

# Demo 4: View schema info
echo "━━━ Demo 4: View Schema Information ━━━"
echo "Command: uv run mdasdata examples/simple.md schema info /tmp/demo_permissive.json"
uv run mdasdata examples/simple.md schema info /tmp/demo_permissive.json
echo ""

# Demo 5: Validate document
echo "━━━ Demo 5: Validate Document ━━━"
echo "Command: uv run mdasdata examples/simple.md schema validate /tmp/demo_permissive.json"
uv run mdasdata examples/simple.md schema validate /tmp/demo_permissive.json
echo ""

# Demo 6: Use pre-generated schemas
echo "━━━ Demo 6: Use Pre-Generated Schemas ━━━"
echo "Available schemas in examples/schemas/:"
ls -1 examples/schemas/*.json
echo ""
echo "Validate using pre-generated schema:"
uv run mdasdata examples/complex.md schema validate examples/schemas/complex_permissive.json
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "  Demo Complete!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Key Takeaways:"
echo "  • Permissive mode: Minimal schemas, flexible validation"
echo "  • Strict mode: Exact constraints, enforced structure"
echo "  • Schemas in examples/schemas/ ready for testing"
echo ""
