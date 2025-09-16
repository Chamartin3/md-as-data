"""Specialized interface for task list manipulation."""

from .models import Block, BlockType, TaskItemData


class TaskList:
    """Specialized interface for task list manipulation.

    Provides high-level filtering and mutation operations for task list blocks,
    maintaining consistency between task metadata and block content.
    """

    def __init__(self, block: Block):
        """Initialize TaskList wrapper from TASK_LIST block.

        Args:
            block: Block of type TASK_LIST

        Raises:
            ValueError: If block is not TASK_LIST type
        """
        if block.type != BlockType.TASK_LIST:
            raise ValueError(f"Block must be TASK_LIST type, got {block.type}")
        self.block = block
        # Get tasks from metadata with runtime type checking
        tasks_data = block.metadata.get("tasks", [])
        if isinstance(tasks_data, list):
            self.tasks: list[TaskItemData] = tasks_data  # type: ignore
        else:
            self.tasks = []

    # Filtering Methods

    def filter_by_symbol(self, symbol: str) -> list[TaskItemData]:
        """Filter tasks by specific checkbox character.

        Args:
            symbol: Checkbox character to filter by

        Returns:
            List of tasks matching the symbol
        """
        return [task for task in self.tasks if task["symbol"] == symbol]

    def get_completed_tasks(self) -> list[TaskItemData]:
        """Get tasks marked as completed (x or X).

        Returns:
            List of completed tasks
        """
        return [task for task in self.tasks if task["symbol"].lower() == "x"]

    def get_pending_tasks(self) -> list[TaskItemData]:
        """Get tasks marked as pending (space).

        Returns:
            List of pending tasks
        """
        return [task for task in self.tasks if task["symbol"] == " "]

    def get_all_symbols(self) -> set[str]:
        """Get unique set of all checkbox symbols used.

        Returns:
            Set of unique checkbox symbols
        """
        return {task["symbol"] for task in self.tasks}

    # Mutation Methods

    def mark_completed(self, task_index: int) -> None:
        """Mark specific task as completed.

        Args:
            task_index: Index of task to mark as completed

        Raises:
            IndexError: If task_index is out of range
        """
        if not (0 <= task_index < len(self.tasks)):
            raise IndexError(f"Task index {task_index} out of range")

        self.tasks[task_index]["symbol"] = "x"
        self._sync_block_content()

    def mark_pending(self, task_index: int) -> None:
        """Mark specific task as pending.

        Args:
            task_index: Index of task to mark as pending

        Raises:
            IndexError: If task_index is out of range
        """
        if not (0 <= task_index < len(self.tasks)):
            raise IndexError(f"Task index {task_index} out of range")

        self.tasks[task_index]["symbol"] = " "
        self._sync_block_content()

    def set_symbol(self, task_index: int, symbol: str) -> None:
        """Set custom checkbox symbol for task.

        Args:
            task_index: Index of task to update
            symbol: Single character symbol

        Raises:
            IndexError: If task_index is out of range
            ValueError: If symbol is not single character
        """
        if not (0 <= task_index < len(self.tasks)):
            raise IndexError(f"Task index {task_index} out of range")

        if len(symbol) != 1:
            raise ValueError("Symbol must be single character")

        self.tasks[task_index]["symbol"] = symbol
        self._sync_block_content()

    def add_task(self, content: str, symbol: str = " ") -> None:
        """Add new task to the list.

        Args:
            content: Task text content
            symbol: Checkbox symbol (default: space for pending)

        Raises:
            ValueError: If symbol is not single character
        """
        if len(symbol) != 1:
            raise ValueError("Symbol must be single character")

        task_data: TaskItemData = {"content": content, "symbol": symbol}

        self.tasks.append(task_data)
        if isinstance(self.block.content, list):
            self.block.content.append(content)
        self.block.metadata["tasks"] = self.tasks  # type: ignore

    def remove_task(self, task_index: int) -> None:
        """Remove task from the list.

        Args:
            task_index: Index of task to remove

        Raises:
            IndexError: If task_index is out of range
        """
        if not (0 <= task_index < len(self.tasks)):
            raise IndexError(f"Task index {task_index} out of range")

        self.tasks.pop(task_index)
        if isinstance(self.block.content, list):
            self.block.content.pop(task_index)
        self.block.metadata["tasks"] = self.tasks  # type: ignore

    def reorder_tasks(self, new_order: list[int]) -> None:
        """Reorder tasks based on index array.

        Args:
            new_order: List of indices in new order

        Raises:
            ValueError: If new_order is invalid
        """
        if len(new_order) != len(self.tasks):
            raise ValueError("new_order length must match task count")

        if set(new_order) != set(range(len(self.tasks))):
            raise ValueError("new_order must contain all indices exactly once")

        self.tasks = [self.tasks[i] for i in new_order]
        if isinstance(self.block.content, list):
            self.block.content = [self.block.content[i] for i in new_order]
        self.block.metadata["tasks"] = self.tasks  # type: ignore

    # Helper Methods

    def _sync_block_content(self) -> None:
        """Synchronize block content list with task metadata."""
        self.block.content = [task["content"] for task in self.tasks]
        self.block.metadata["tasks"] = self.tasks  # type: ignore

    def __len__(self) -> int:
        """Return number of tasks in list."""
        return len(self.tasks)

    def __repr__(self) -> str:
        """Return string representation of TaskList."""
        return f"TaskList(tasks={len(self.tasks)})"
