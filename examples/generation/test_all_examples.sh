#!/bin/bash
# Test script for all generation examples

set -e  # Exit on error

echo "=========================================="
echo "Testing Markdown Generation Examples"
echo "=========================================="
echo ""

# Clean up previous test outputs
echo "Cleaning up previous test outputs..."
rm -f examples/generation/generated_*.md
echo ""

# Test 1: Generate template from JSON schema
echo "[Test 1] Generate template from JSON schema..."
uv run mddata generate \
  --schema examples/generation/blog_post_schema.json \
  --output examples/generation/generated_blog_template.md
echo "✓ Created: generated_blog_template.md"
echo ""

# Test 2: Generate template from YAML schema
echo "[Test 2] Generate template from YAML schema..."
uv run mddata generate \
  --schema examples/generation/project_spec_schema.yaml \
  --output examples/generation/generated_project_template.md
echo "✓ Created: generated_project_template.md"
echo ""

# Test 3: Generate from data only (blog post)
echo "[Test 3] Generate from data only (blog post)..."
uv run mddata generate \
  --data examples/generation/blog_post_data.json \
  --output examples/generation/generated_blog_post.md
echo "✓ Created: generated_blog_post.md"
echo ""

# Test 4: Generate from data only (meeting notes)
echo "[Test 4] Generate from data only (meeting notes)..."
uv run mddata generate \
  --data examples/generation/simple_note_data.json \
  --output examples/generation/generated_meeting_notes.md
echo "✓ Created: generated_meeting_notes.md"
echo ""

# Test 5: Generate with schema validation (valid data)
echo "[Test 5] Generate with schema validation (valid data)..."
uv run mddata generate \
  --data examples/generation/blog_post_data.json \
  --schema examples/generation/blog_post_schema.json \
  --output examples/generation/generated_validated_blog.md
echo "✓ Created: generated_validated_blog.md"
echo ""

# Test 6: Generate with schema validation (invalid data)
echo "[Test 6] Generate with schema validation (invalid data)..."
echo "Note: This may show validation warnings/errors"
uv run mddata generate \
  --data examples/generation/invalid_data.json \
  --schema examples/generation/blog_post_schema.json \
  --output examples/generation/generated_invalid.md || true
echo "✓ Created: generated_invalid.md (check for validation messages)"
echo ""

# Test 7: Print to stdout (no output file)
echo "[Test 7] Generate to stdout (no output file)..."
echo "First 20 lines of output:"
uv run mddata generate \
  --data examples/generation/simple_note_data.json | head -20
echo "..."
echo ""

# Test 8: Force overwrite existing file
echo "[Test 8] Force overwrite existing file..."
uv run mddata generate \
  --schema examples/generation/blog_post_schema.json \
  --output examples/generation/generated_blog_template.md \
  --force
echo "✓ Overwrote: generated_blog_template.md"
echo ""

# Summary
echo "=========================================="
echo "All tests completed successfully!"
echo "=========================================="
echo ""
echo "Generated files:"
ls -lh examples/generation/generated_*.md
echo ""
echo "To view a generated file:"
echo "  cat examples/generation/generated_blog_post.md"
echo ""
echo "To clean up generated files:"
echo "  rm examples/generation/generated_*.md"
