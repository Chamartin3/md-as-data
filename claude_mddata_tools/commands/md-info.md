---
description: Display comprehensive information about a markdown file
argument-hint: <markdown-file> [--verbose]
allowed-tools: Bash(mddata:*)
---

# Markdown File Information

Display comprehensive information about the markdown file: **$1**

Execute the following commands to gather complete document information:

1. **Quick Summary** - Run:
   ```bash
   mddata info summary "$1" --verbose
   ```

2. **Frontmatter Properties** - Run:
   ```bash
   mddata info properties "$1" --verbose
   ```

3. **Section Hierarchy** - Run:
   ```bash
   mddata info sections "$1" --paths --blocks
   ```

4. **Content Blocks Summary** - Run:
   ```bash
   mddata info blocks "$1" --limit 20
   ```

Present the results in a well-organized format with clear section headings.

---

**Usage Examples:**
- Basic: `/md-info document.md`
- With details: `/md-info README.md --verbose`

**What you get:**
- Complete document overview
- All frontmatter properties with values
- Full section hierarchy with paths
- Block type distribution
- Quick insight into document structure
