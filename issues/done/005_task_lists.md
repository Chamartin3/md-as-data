# Issue Report: Complex Task List Functionality Implementation

## Issue Description

Implement comprehensive task list (checkbox) functionality to extract, filter, and mutate task lists with different statuses and custom checkbox characters. The current md_as_data library treats task lists as regular unordered lists, losing the semantic meaning of task status indicators and preventing programmatic manipulation of task states.

**Required Functionality:**
- Extract task lists from markdown content with configurable checkbox characters
- Filter task list elements by status (done, pending, important, custom states)
- Mutate task lists (change status, add/remove items, reorder)
- Support variable checkbox characters (`[x]` done, `[ ]` pending, `[!]` important, `[~]` in-progress, `[?]` question/blocked)
- Minimal interface in MarkdownData object for task list access
- Delegate complex task list operations to specialized TaskList class

**Environmental Context:**
- Current architecture uses markdown-it-py CommonMark parser with extensible token handlers
- Existing list parsing provides foundation (`_handle_bullet_list`, `_handle_ordered_list`)
- Block metadata system supports custom field storage
- Type-safe model hierarchy with BlockType enum and Block class serialization
- Processor.py handles token-based parsing with configurable handlers

## Step-by-Step Reproduction

### Setup Process

1. **Create test markdown file with various task list patterns:**
```markdown
---
title: "Task List Test Document"
version: "1.0"
---

# Project Development Tasks

## Sprint Planning
- [x] Define project scope
- [ ] Create user stories
- [!] Review security requirements (HIGH PRIORITY)
- [~] Research technology stack (IN PROGRESS)
- [?] Clarify performance requirements (BLOCKED)

## Implementation Tasks
- [x] Set up repository
- [ ] Implement core features
- [!] Critical bug fixes required
- Custom status: [P] Paused for review
- Mixed list: Regular item without checkbox

## Documentation
- [x] API documentation complete
- [ ] User guide in progress
- [!] Release notes urgent
```

2. **Test current parser behavior:**
```bash
cd /home/omidev/Code/tools/makdown_manager/mdasdata
uv run python -c "
from src.md_as_data import MarkdownFile
file = MarkdownFile('task_test.md')
doc = file.mddata

# Examine current parsing behavior
sections = doc.content.get_all_sections()
for section in sections:
    print(f'Section: {section.title}')
    for block in section.blocks:
        if hasattr(block.type, 'value') and block.type.value == 'list':
            print(f'  List block: {block.content}')
            print(f'  Metadata: {block.metadata}')
            print('---')
"
```

3. **Verify current limitations:**
```python
# Expected to show task lists are parsed as regular lists
# Checkbox syntax treated as literal text content
# No task status recognition or metadata extraction
# No programmatic access to task completion states
```

**Expected Result:**
- Task lists recognized as distinct `TASK_LIST` block type
- Individual task items parsed with status metadata
- Filtering capabilities by completion status and priority
- Mutation operations to change task states
- Serialization preserves checkbox formatting

**Actual Result:**
- Task lists parsed as regular `LIST` blocks
- Checkbox syntax `[x]`, `[ ]`, `[!]` treated as literal text
- No distinction between task items and regular list items
- No programmatic access to task status information
- No filtering or mutation capabilities for task states

## Diagnostics

**Affected Files/Classes/Components:**
- `/src/md_as_data/models.py` - BlockType enum, BlockMetadata TypedDict, Block class
- `/src/md_as_data/processor.py` - MarkdownProcessor, token handlers, _handle_bullet_list method
- `/src/md_as_data/data.py` - MarkdownData class, public API methods
- `/src/md_as_data/__init__.py` - Public API exports for new TaskList class

**Analysis:**

The issue occurs because the current `_handle_bullet_list` method in `processor.py` extracts list item content without parsing checkbox patterns. The token processing flow is:

1. markdown-it-py tokenizes task lists as `BULLET_LIST_OPEN` tokens (same as regular lists)
2. `_handle_bullet_list()` processes `LIST_ITEM_OPEN` tokens extracting raw `INLINE` content
3. Checkbox syntax like `[x] Task content` stored as literal string content
4. Block created with `BlockType.LIST` instead of `BlockType.TASK_LIST`
5. No metadata extraction for task status indicators

**Current Token Processing Flow:**
```
BULLET_LIST_OPEN → _handle_bullet_list() →
  LIST_ITEM_OPEN → extract INLINE content →
    "[x] Done task" stored as raw text →
      Block(type=LIST, content=["[x] Done task"])
```

**Missing Components:**
1. `BlockType.TASK_LIST` enum value for semantic distinction
2. Task metadata fields in BlockMetadata (status, completed, priority flags)
3. Checkbox pattern recognition logic in token handler
4. TaskList wrapper class for advanced operations (filtering, mutation)
5. MarkdownData integration methods (`get_task_lists`, `filter_tasks_by_status`)

## Suggestions

Implement task list support through the following architectural changes:

### 1. Extend Data Model (models.py)

```python
class BlockType(Enum):
    """Types of content blocks in markdown."""
    PARAGRAPH = "paragraph"
    LIST = "list"
    ORDERED_LIST = "ordered_list"
    TASK_LIST = "task_list"  # NEW: Task list type
    CODE_BLOCK = "code_block"
    # ... existing types

class TaskItemData(TypedDict):
    """Individual task item with status metadata."""
    content: str             # Task text content
    symbol: str             # Checkbox character (x, space, !, ~, ?, etc.)

class BlockMetadata(TypedDict, total=False):
    """Metadata attributes for blocks."""
    language: str           # For code blocks
    href: str              # For links
    src: str               # For images
    alt: str               # For images
    title: str             # For links/images
    tasks: list[TaskItemData]  # NEW: For task list blocks
```

### 2. Enhanced Parser Support (processor.py)

Modify `_handle_bullet_list` to detect and process task lists:

```python
def _handle_bullet_list(self, token: Token, state: dict) -> int:
    """Handle bullet list tokens, detecting task lists."""
    tokens = state["tokens"]
    i = state["index"]

    list_items = []
    task_items = []
    j = i + 1

    # Extract list items and check for task patterns
    while j < len(tokens) and tokens[j].type != TokenType.BULLET_LIST_CLOSE:
        if tokens[j].type == TokenType.LIST_ITEM_OPEN:
            k = j + 1
            while k < len(tokens) and tokens[k].type != TokenType.LIST_ITEM_CLOSE:
                if tokens[k].type == TokenType.INLINE:
                    item_content = tokens[k].content
                    task_data = self._parse_task_item(item_content)

                    if task_data:
                        task_items.append(task_data)
                    else:
                        list_items.append(item_content)
                    break
                k += 1
        j += 1

    # Create appropriate block type
    if task_items and not list_items:
        # Pure task list
        block = Block(state["current_section"].id, BlockType.TASK_LIST,
                     [t['content'] for t in task_items])
        block.metadata['tasks'] = task_items
        state["current_section"].add_block(block)
    elif task_items and list_items:
        # Mixed list - create both blocks or handle as configuration option
        self._handle_mixed_list(state, task_items, list_items)
    elif list_items:
        # Regular list
        block = Block(state["current_section"].id, BlockType.LIST, list_items)
        state["current_section"].add_block(block)

    return j - i + 1

def _parse_task_item(self, item_text: str) -> TaskItemData | None:
    """Parse task list item checkbox syntax."""
    import re

    # Match pattern: optional whitespace, [char], space, content
    pattern = r'^\s*\[(.?)\]\s*(.*)'
    match = re.match(pattern, item_text.strip())

    if not match:
        return None

    indicator = match.group(1)
    content = match.group(2)

    # Determine semantic status
    completed = indicator.lower() == 'x'
    priority = indicator == '!'

    return {
        'content': content,
        'status': indicator,
        'completed': completed,
        'priority': priority,
        'custom_indicator': indicator if indicator not in ['x', 'X', ' ', '!'] else ''
    }
```

### 3. TaskList Wrapper Class

Create specialized class for task list operations:

```python
class TaskList:
    """Specialized interface for task list manipulation."""

    def __init__(self, block: Block):
        if block.type != BlockType.TASK_LIST:
            raise ValueError("Block must be TASK_LIST type")
        self.block = block
        self.tasks = block.metadata.get('tasks', [])

    def filter_by_status(self, status: str) -> list[TaskItemData]:
        """Filter tasks by specific status character."""
        return [task for task in self.tasks if task['status'] == status]

    def filter_completed(self, completed: bool = True) -> list[TaskItemData]:
        """Filter tasks by completion status."""
        return [task for task in self.tasks if task['completed'] == completed]

    def filter_priority(self, priority: bool = True) -> list[TaskItemData]:
        """Filter tasks by priority flag."""
        return [task for task in self.tasks if task['priority'] == priority]

    def get_custom_status_tasks(self) -> list[TaskItemData]:
        """Get tasks with custom status indicators."""
        return [task for task in self.tasks if task['custom_indicator']]

    def mark_completed(self, task_index: int) -> None:
        """Mark specific task as completed."""
        if 0 <= task_index < len(self.tasks):
            self.tasks[task_index]['status'] = 'x'
            self.tasks[task_index]['completed'] = True
            # Update block content
            self.block.content[task_index] = self.tasks[task_index]['content']

    def mark_pending(self, task_index: int) -> None:
        """Mark specific task as pending."""
        if 0 <= task_index < len(self.tasks):
            self.tasks[task_index]['status'] = ' '
            self.tasks[task_index]['completed'] = False
            self.block.content[task_index] = self.tasks[task_index]['content']

    def set_custom_status(self, task_index: int, status: str) -> None:
        """Set custom status character for task."""
        if 0 <= task_index < len(self.tasks):
            self.tasks[task_index]['status'] = status
            self.tasks[task_index]['completed'] = status.lower() == 'x'
            self.tasks[task_index]['priority'] = status == '!'
            self.tasks[task_index]['custom_indicator'] = status if status not in ['x', 'X', ' ', '!'] else ''

    def add_task(self, content: str, status: str = ' ') -> None:
        """Add new task to the list."""
        task_data = {
            'content': content,
            'status': status,
            'completed': status.lower() == 'x',
            'priority': status == '!',
            'custom_indicator': status if status not in ['x', 'X', ' ', '!'] else ''
        }

        self.tasks.append(task_data)
        self.block.content.append(content)
        self.block.metadata['tasks'] = self.tasks

    def remove_task(self, task_index: int) -> None:
        """Remove task from the list."""
        if 0 <= task_index < len(self.tasks):
            self.tasks.pop(task_index)
            self.block.content.pop(task_index)
            self.block.metadata['tasks'] = self.tasks

    def reorder_tasks(self, new_order: list[int]) -> None:
        """Reorder tasks based on index array."""
        if len(new_order) != len(self.tasks) or set(new_order) != set(range(len(self.tasks))):
            raise ValueError("Invalid reorder specification")

        self.tasks = [self.tasks[i] for i in new_order]
        self.block.content = [self.block.content[i] for i in new_order]
        self.block.metadata['tasks'] = self.tasks
```

### 4. MarkdownData Integration

Add minimal interface methods to MarkdownData:

```python
def get_task_lists(self, section_id: str | None = None) -> list[TaskList]:
    """Get task list objects for advanced operations."""
    blocks_data = self.get_blocks(section_id)
    task_lists = []

    for block_data in blocks_data['blocks']:
        if block_data['type'] == 'task_list':
            # Reconstruct Block object from BlockData
            block = Block.from_dict(block_data)
            task_lists.append(TaskList(block))

    return task_lists

def filter_tasks_by_status(self, status: str, section_id: str | None = None) -> list[dict]:
    """Get all tasks with specific status across sections."""
    all_tasks = []
    for task_list in self.get_task_lists(section_id):
        matching_tasks = task_list.filter_by_status(status)
        all_tasks.extend(matching_tasks)
    return all_tasks

def get_completed_tasks(self, section_id: str | None = None) -> list[dict]:
    """Get all completed tasks."""
    all_tasks = []
    for task_list in self.get_task_lists(section_id):
        completed_tasks = task_list.filter_completed(True)
        all_tasks.extend(completed_tasks)
    return all_tasks

def get_pending_tasks(self, section_id: str | None = None) -> list[dict]:
    """Get all pending tasks."""
    all_tasks = []
    for task_list in self.get_task_lists(section_id):
        pending_tasks = task_list.filter_completed(False)
        all_tasks.extend(pending_tasks)
    return all_tasks
```

### 5. Serialization Support

Update Block.to_text() for task list serialization:

```python
def to_text(self) -> str:
    """Return a block as markdown text representation."""
    if self.type == BlockType.TASK_LIST:
        if isinstance(self.content, list) and 'tasks' in self.metadata:
            items = []
            for content, task_meta in zip(self.content, self.metadata['tasks']):
                status = task_meta.get('status', ' ')
                items.append(f"- [{status}] {content}")
            return "\n".join(items)

    # ... existing to_text logic for other block types
```

### 6. CLI Integration

Extend CLI with task list specific commands:

```python
# In cli/info.py
@info_app.command("tasks")
def tasks_info(
    ctx: typer.Context,
    section: Optional[str] = typer.Option(None, help="Filter by section"),
    status: Optional[str] = typer.Option(None, help="Filter by status character"),
    completed: Optional[bool] = typer.Option(None, help="Filter by completion"),
    priority: Optional[bool] = typer.Option(None, help="Filter by priority")
):
    """Show task list information."""
    doc: MarkdownData = ctx.obj["doc"]

    task_lists = doc.get_task_lists(section)

    for task_list in task_lists:
        tasks = task_list.tasks

        if status:
            tasks = [t for t in tasks if t['status'] == status]
        if completed is not None:
            tasks = [t for t in tasks if t['completed'] == completed]
        if priority is not None:
            tasks = [t for t in tasks if t['priority'] == priority]

        # Display filtered tasks using Rich formatting
```

### 7. Configuration Options

Support configurable checkbox character mappings:

```python
class TaskListConfig(TypedDict):
    """Configuration for task list processing."""
    completion_indicators: list[str]  # Characters meaning "completed"
    priority_indicators: list[str]    # Characters meaning "priority"
    custom_status_map: dict[str, str] # Custom status character meanings
```

## Current Tests

**Relevant Test Suites:**
- `/tests/unit/md_as_data/test_models.py` - Block creation, serialization, and type validation
- `/tests/unit/md_as_data/test_processor.py` - Parser token handling and list processing
- `/tests/test_md_as_data.py` - Integration tests for document processing

**Analysis:**
Current tests are not catching this issue because:

1. **Limited List Coverage**: Existing tests focus on basic unordered/ordered lists without task list patterns
2. **No Task List Fixtures**: Test markdown samples don't include checkbox syntax examples
3. **Missing Token Handler Tests**: No specific tests for `_handle_bullet_list` with task patterns
4. **Integration Gap**: No end-to-end tests verifying task list recognition and manipulation
5. **Serialization Gap**: No round-trip tests ensuring task list formatting preservation

**Required Test Additions:**

1. **Unit Tests - models.py**:
   - TaskItemData TypedDict validation
   - BlockType.TASK_LIST enum handling
   - Block metadata with tasks field
   - Task list serialization (to_text method)

2. **Unit Tests - processor.py**:
   - `_parse_task_item` method with various checkbox patterns
   - `_handle_bullet_list` task list detection logic
   - Mixed list handling (regular + task items)
   - Edge cases: malformed checkbox syntax, nested lists

3. **Unit Tests - New TaskList Class**:
   - Filtering methods (by status, completion, priority)
   - Mutation operations (mark completed, add/remove tasks)
   - Reordering functionality
   - Custom status character handling

4. **Integration Tests**:
   - End-to-end parsing of documents with task lists
   - MarkdownData task list access methods
   - Round-trip serialization preserving checkbox formatting
   - CLI command integration for task operations

5. **Edge Case Tests**:
   - Empty task lists
   - Task lists with only custom status characters
   - Mixed lists with both regular and task items
   - Nested task lists (if supported)
   - Invalid checkbox syntax handling

**Test Implementation Priority:**
1. Core parsing logic (`_parse_task_item`, token handling)
2. TaskList class functionality (filtering, mutations)
3. MarkdownData integration methods
4. Serialization round-trip preservation
5. CLI integration and error handling
