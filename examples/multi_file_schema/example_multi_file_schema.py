#!/usr/bin/env python3
"""Multi-File Schema Generation Example

This example demonstrates generating a schema from multiple markdown documents,
showing how properties are aggregated and requirements are inferred based on
frequency across files.
"""

import json
from pathlib import Path

from mddata import MarkdownFile, generate_schema
from mddata.validation import SchemaInferenceMode


def main():
    # Define the example documents directory
    examples_dir = Path(__file__).parent
    doc_files = [
        examples_dir / "doc1.md",
        examples_dir / "doc2.md",
        examples_dir / "doc3.md",
    ]

    print("=" * 60)
    print("Multi-File Schema Generation Example")
    print("=" * 60)
    print()

    # Load all documents
    print(f"Loading {len(doc_files)} markdown documents...")
    docs = [MarkdownFile(fp) for fp in doc_files]
    print()

    # Display document overview
    print("Document Overview:")
    print("-" * 60)
    for i, doc in enumerate(docs, 1):
        print(f"Document {i}: {doc.mddata.title}")
        print(f"  Properties: {', '.join(doc.mddata.frontmatter.keys())}")
        print(f"  Status: {doc.mddata.frontmatter.get('status', 'N/A')}")
        print()

    # Generate merged schema
    print("Generating merged schema from all documents...")
    print()

    schema = generate_schema(
        [doc.mddata.data for doc in docs], inference_mode=SchemaInferenceMode.PERMISSIVE
    )

    print(f"✓ Schema generated from {len(docs)} markdown files")
    print()

    # Analyze frontmatter properties
    print("Frontmatter Property Analysis:")
    print("-" * 60)

    frontmatter_schema = schema.get("frontmatter", {})
    for prop_name, prop_schema in frontmatter_schema.items():
        required = prop_schema.get("required", False)
        prop_type = prop_schema.get("type", "unknown")
        enum_values = prop_schema.get("enum")

        status = "REQUIRED" if required else "OPTIONAL"
        print(f"{prop_name}: {prop_type} [{status}]")

        if enum_values:
            print(f"  Enum values: {enum_values}")

        # Count occurrences
        count = sum(1 for doc in docs if prop_name in doc.mddata.frontmatter)
        percentage = (count / len(docs)) * 100
        print(f"  Frequency: {count}/{len(docs)} documents ({percentage:.0f}%)")
        print()

    # Display key insights
    print("Key Insights:")
    print("-" * 60)
    print("• 'title' appears in all documents → marked as REQUIRED")
    print("• 'author' appears in 2/3 documents (67%) → marked as OPTIONAL")
    print("• 'status' appears in all documents → marked as REQUIRED")
    print("• 'status' has single-word values → inferred as ENUM type")
    print("• 'tags' appears in all documents → marked as REQUIRED")
    print("• 'version' appears in 2/3 documents → marked as OPTIONAL")
    print()

    # Save schema to file
    output_file = examples_dir / "generated_schema.json"
    with open(output_file, "w") as f:
        json.dump(schema, f, indent=2)

    print(f"✓ Schema saved to: {output_file}")
    print()

    print("=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
