#!/usr/bin/env python3
"""Task Lists Example

This example demonstrates the planned task list functionality for extracting,
filtering, and manipulating task lists with different status indicators.

NOTE: This is a demonstration of the PLANNED functionality described in
issue #005. The actual implementation is not yet complete.
"""

from pathlib import Path


def main():
    """Demonstrate planned task list functionality."""

    print("=" * 60)
    print("Task Lists Example (PLANNED FUNCTIONALITY)")
    print("=" * 60)
    print()
    print("NOTE: This example demonstrates the planned task list API")
    print("described in issue #005. Implementation is pending.")
    print()

    examples_dir = Path(__file__).parent
    task_file = examples_dir / "project_tasks.md"

    print(f"Example Task File: {task_file.name}")
    print()

    # Display what the API will look like once implemented
    print("Planned API Usage:")
    print("-" * 60)
    print()

    print("# Load document with task lists")
    print("from mddata import MarkdownFile")
    print(f"doc = MarkdownFile('{task_file}')")
    print("mddata = doc.mddata")
    print()

    print("# Get all task lists from document")
    print("task_lists = mddata.get_task_lists()")
    print("# Returns: List of TaskList objects")
    print()

    print("# Filter tasks by completion status")
    print("completed_tasks = mddata.get_completed_tasks()")
    print("pending_tasks = mddata.get_pending_tasks()")
    print()

    print("# Filter tasks by specific status indicator")
    print("priority_tasks = mddata.filter_tasks_by_status('!')")
    print("in_progress_tasks = mddata.filter_tasks_by_status('~')")
    print("blocked_tasks = mddata.filter_tasks_by_status('?')")
    print()

    print("# Work with individual task lists")
    print("for task_list in task_lists:")
    print("    # Filter within specific list")
    print("    completed = task_list.filter_completed(True)")
    print("    priority = task_list.filter_priority(True)")
    print("    custom = task_list.get_custom_status_tasks()")
    print()
    print("    # Mutate task status")
    print("    task_list.mark_completed(0)  # Mark first task as done")
    print("    task_list.mark_pending(1)    # Mark second task as pending")
    print("    task_list.set_custom_status(2, '~')  # Set custom status")
    print()
    print("    # Add/remove tasks")
    print("    task_list.add_task('New task item', status=' ')")
    print("    task_list.remove_task(0)")
    print()
    print("    # Reorder tasks")
    print("    task_list.reorder_tasks([1, 0, 2])  # Swap first two tasks")
    print()

    print("-" * 60)
    print()

    # Show example task list structure
    print("Example Task List Content:")
    print("-" * 60)
    print()

    with open(task_file) as f:
        content = f.read()

    # Extract and display Sprint Planning section
    lines = content.split("\n")
    in_sprint = False
    for line in lines:
        if "## Sprint Planning" in line:
            in_sprint = True
        elif in_sprint and line.startswith("## "):
            break

        if in_sprint:
            print(line)

    print()
    print("-" * 60)
    print()

    # Show expected parsing results
    print("Expected Parsing Results:")
    print("-" * 60)
    print()
    print("Task List Block Type: TASK_LIST")
    print()
    print("Individual Tasks:")
    print("  1. [x] Define project scope")
    print("     → Status: 'x', Completed: True, Priority: False")
    print()
    print("  2. [ ] Create user stories")
    print("     → Status: ' ', Completed: False, Priority: False")
    print()
    print("  3. [!] Review security requirements")
    print("     → Status: '!', Completed: False, Priority: True")
    print()
    print("  4. [~] Research technology stack")
    print("     → Status: '~', Completed: False, Custom: '~'")
    print()
    print("  5. [?] Clarify performance requirements")
    print("     → Status: '?', Completed: False, Custom: '?'")
    print()

    print("=" * 60)
    print("For implementation details, see:")
    print("  issues/done/005_task_lists.md")
    print("=" * 60)


if __name__ == "__main__":
    main()
