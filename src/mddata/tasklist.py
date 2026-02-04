"""Specialized interface for task list manipulation."""

import hashlib

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
            # Ensure all tasks have UIDs
            self._ensure_uids()
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
        """Get tasks marked as completed (x or X), including subtasks.

        Returns:
            List of completed tasks
        """

        def collect_completed(tasks: list[TaskItemData]) -> list[TaskItemData]:
            result = []
            for task in tasks:
                if task["symbol"].lower() == "x":
                    result.append(task)
                if "subtasks" in task:
                    result.extend(collect_completed(task["subtasks"]))
            return result

        return collect_completed(self.tasks)

    def get_pending_tasks(self) -> list[TaskItemData]:
        """Get tasks marked as pending (space), including subtasks.

        Returns:
            List of pending tasks
        """

        def collect_pending(tasks: list[TaskItemData]) -> list[TaskItemData]:
            result = []
            for task in tasks:
                if task["symbol"] == " ":
                    result.append(task)
                if "subtasks" in task:
                    result.extend(collect_pending(task["subtasks"]))
            return result

        return collect_pending(self.tasks)

    def get_all_symbols(self) -> set[str]:
        """Get unique set of all checkbox symbols used.

        Returns:
            Set of unique checkbox symbols
        """
        return {task["symbol"] for task in self.tasks}

    # Mutation Methods

    def mark_completed(self, task_ref: int | str) -> None:
        """Mark specific task as completed.

        Args:
            task_ref: Index of task to mark as completed, or task UID (hierarchical)

        Raises:
            IndexError: If task_index is out of range
            ValueError: If UID is not found
        """
        task = self._resolve_task_reference(task_ref)
        task["symbol"] = "x"
        self._sync_block_content()

    def _resolve_task_reference(self, task_ref: int | str) -> TaskItemData:
        """Resolve a task reference to a TaskItemData object.

        Args:
            task_ref: Numeric index or hierarchical UID string

        Returns:
            The referenced task

        Raises:
            IndexError: If numeric index is out of range
            ValueError: If UID is not found
        """
        if isinstance(task_ref, str):
            # Handle hierarchical UID
            task = self.get_task_by_uid(task_ref)
            if task is None:
                raise ValueError(f"Task with UID '{task_ref}' not found")
            return task
        else:
            # Handle numeric index
            if not (0 <= task_ref < len(self.tasks)):
                raise IndexError(f"Task index {task_ref} out of range")
            return self.tasks[task_ref]

    def mark_pending(self, task_ref: int | str) -> None:
        """Mark specific task as pending.

        Args:
            task_ref: Index of task to mark as pending, or task UID (hierarchical)

        Raises:
            IndexError: If task_index is out of range
            ValueError: If UID is not found
        """
        task = self._resolve_task_reference(task_ref)
        task["symbol"] = " "
        self._sync_block_content()

    def set_symbol(self, task_ref: int | str, symbol: str) -> None:
        """Set custom checkbox symbol for task.

        Args:
            task_ref: Index of task to update, or task UID (hierarchical)
            symbol: Single character symbol

        Raises:
            IndexError: If task_index is out of range
            ValueError: If symbol is not single character or UID is not found
        """
        if len(symbol) != 1:
            raise ValueError("Symbol must be single character")

        task = self._resolve_task_reference(task_ref)
        task["symbol"] = symbol
        self._sync_block_content()

    def add_task(self, content: str, symbol: str = " ") -> str:
        """Add new task to the list.

        Args:
            content: Task text content
            symbol: Checkbox symbol (default: space for pending)

        Returns:
            UID of the newly added task

        Raises:
            ValueError: If symbol is not single character
        """
        if len(symbol) != 1:
            raise ValueError("Symbol must be single character")

        # Generate unique UID
        base_uid = self._generate_uid(content)
        uid = base_uid
        counter = 1
        existing_uids = {task.get("uid") for task in self.tasks}
        while uid in existing_uids:
            uid = f"{base_uid}{counter}"
            counter += 1

        task_data: TaskItemData = {"content": content, "symbol": symbol, "uid": uid}

        self.tasks.append(task_data)
        if isinstance(self.block.content, list):
            self.block.content.append(content)
        self.block.metadata["tasks"] = self.tasks  # type: ignore

        return uid

    def remove_task(self, task_ref: int | str) -> None:
        """Remove task from the list.

        Args:
            task_ref: Index of task to remove, or task UID (hierarchical)

        Raises:
            IndexError: If task_index is out of range
            ValueError: If UID is not found
        """
        # For removal, we need to handle hierarchical references differently
        # since we need to know the parent to remove from
        if isinstance(task_ref, str) and "." in task_ref:
            # Hierarchical UID - need to remove from subtasks
            uid_parts = task_ref.split(".")
            parent_uid = ".".join(uid_parts[:-1])
            target_uid = uid_parts[-1]

            parent_task = self.get_task_by_uid(parent_uid)
            if parent_task is None:
                raise ValueError(f"Parent task with UID '{parent_uid}' not found")

            if "subtasks" not in parent_task:
                raise ValueError(f"Parent task '{parent_uid}' has no subtasks")

            # Find and remove the subtask
            subtasks = parent_task["subtasks"]
            for i, subtask in enumerate(subtasks):
                if subtask.get("uid") == target_uid:
                    subtasks.pop(i)
                    self._sync_block_content()
                    return

            raise ValueError(
                f"Subtask with UID '{target_uid}' not found under '{parent_uid}'"
            )
        else:
            # Simple case - remove from root level
            if isinstance(task_ref, str):
                index = self.get_task_index_by_uid(task_ref)
                if index is None:
                    raise ValueError(f"Task with UID '{task_ref}' not found")
            else:
                if not (0 <= task_ref < len(self.tasks)):
                    raise IndexError(f"Task index {task_ref} out of range")
                index = task_ref

            self.tasks.pop(index)
            if isinstance(self.block.content, list):
                self.block.content.pop(index)
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

    # UID Methods

    def _generate_uid(self, content: str) -> str:
        """Generate a short unique identifier for a task.

        Args:
            content: Task content

        Returns:
            Short alphanumeric UID
        """
        # Create a hash of the content and take first 4 characters
        hash_obj = hashlib.md5(content.encode())
        return hash_obj.hexdigest()[:4].upper()

    def _ensure_uids(self) -> None:
        """Ensure all tasks and subtasks have unique UIDs."""
        used_uids = set()
        for task in self.tasks:
            self._ensure_task_uid(task, used_uids)

    def _ensure_task_uid(self, task: TaskItemData, used_uids: set[str]) -> None:
        """Ensure a task and its subtasks have unique UIDs."""
        if "uid" not in task or not task.get("uid"):
            # Generate UID from content
            base_uid = self._generate_uid(task["content"])
            uid = base_uid
            counter = 1
            # Ensure uniqueness within this task list
            while uid in used_uids:
                uid = f"{base_uid}{counter}"
                counter += 1
            task["uid"] = uid
            used_uids.add(uid)
        else:
            used_uids.add(task["uid"])

        # Ensure UIDs for subtasks
        if "subtasks" in task:
            for subtask in task["subtasks"]:
                self._ensure_task_uid(subtask, used_uids)

    def get_task_by_uid(self, uid: str) -> TaskItemData | None:
        """Get task by its UID, supporting hierarchical UIDs like 'A1B2.C3D4'.

        Args:
            uid: Task UID (can be hierarchical with dots)

        Returns:
            Task data if found, None otherwise
        """
        uid_parts = uid.split(".")
        return self._find_task_by_uid_path(self.tasks, uid_parts)

    def _find_task_by_uid_path(
        self, tasks: list[TaskItemData], uid_parts: list[str]
    ) -> TaskItemData | None:
        """Recursively find task by UID path."""
        if not uid_parts:
            return None

        target_uid = uid_parts[0]
        for task in tasks:
            if task.get("uid") == target_uid:
                if len(uid_parts) == 1:
                    return task
                elif "subtasks" in task:
                    return self._find_task_by_uid_path(task["subtasks"], uid_parts[1:])
        return None

    def get_task_index_by_uid(self, uid: str) -> int | None:
        """Get task index by its UID, supporting hierarchical UIDs.

        For hierarchical UIDs, returns the index of the root task.

        Args:
            uid: Task UID (can be hierarchical)

        Returns:
            Task index if found, None otherwise
        """
        uid_parts = uid.split(".")
        if not uid_parts:
            return None

        target_uid = uid_parts[0]
        for i, task in enumerate(self.tasks):
            if task.get("uid") == target_uid:
                return i
        return None

    # Helper Methods

    def _sync_block_content(self) -> None:
        """Synchronize block content list with task metadata."""

        # For now, flatten the hierarchical structure to simple content list
        # This is a simplified approach - full hierarchical serialization would require
        # more complex markdown generation
        def flatten_tasks(tasks: list[TaskItemData]) -> list[str]:
            """Flatten hierarchical tasks to content list."""
            result = []
            for task in tasks:
                result.append(task["content"])
                if "subtasks" in task:
                    # For subtasks, we flatten them but don't preserve
                    # hierarchy in content - limitation of block model
                    result.extend(flatten_tasks(task["subtasks"]))
            return result

        self.block.content = flatten_tasks(self.tasks)
        self.block.metadata["tasks"] = self.tasks  # type: ignore

    def __len__(self) -> int:
        """Return number of tasks in list."""
        return len(self.tasks)

    def __repr__(self) -> str:
        """Return string representation of TaskList."""
        return f"TaskList(tasks={len(self.tasks)})"
