"""Error types for mddata operations."""

from dataclasses import dataclass


@dataclass
class ParameterValidationError(Exception):
    """Error raised when template parameters are invalid or missing."""

    missing_params: list[str]
    provided_params: list[str]
    available_params: list[str]

    def __str__(self) -> str:
        missing = ", ".join(f"'{p}'" for p in self.missing_params)
        provided = ", ".join(f"'{p}'" for p in self.provided_params)
        available = ", ".join(f"'{p}'" for p in self.available_params)

        return (
            f"Missing required parameters: {missing}\n"
            f"Provided parameters: {provided}\n"
            f"Available parameters: {available}"
        )


@dataclass
class DataStructureError(Exception):
    """Error raised when data structure is invalid."""

    issue: str
    expected: str
    received: str

    def __str__(self) -> str:
        return (
            f"Data structure error: {self.issue}. "
            f"Expected: {self.expected}, received: {self.received}"
        )
