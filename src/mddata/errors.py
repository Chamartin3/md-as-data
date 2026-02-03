"""Error types for mddata operations."""

from dataclasses import dataclass


@dataclass
class ParameterValidationError(Exception):
    """Error raised when template parameters are invalid or missing."""

    missing_params: list[str]
    provided_params: list[str]
    available_params: list[str]
    param_definitions: dict | None = None

    def __str__(self) -> str:
        """Format error message with parameter descriptions."""
        lines = []

        # Check if this is a constraint violation error (wrapped ValueError)
        if not self.missing_params and self.provided_params and self.__cause__:
            # Show the constraint violation error
            constraint_error = str(self.__cause__)
            lines.append(f"Parameter validation failed: {constraint_error}")

            # Show the parameter definition for context
            if self.param_definitions and self.provided_params:
                param_name = self.provided_params[0]
                param_def = self.param_definitions.get(param_name, {})
                if param_def:
                    lines.append(f"\nParameter definition for '{param_name}':")
                    desc = param_def.get("description", "No description available")
                    param_type = param_def.get("type", "unknown")
                    required = param_def.get("required", False)
                    req_str = " (required)" if required else " (optional)"
                    lines.append(f"  Type: {param_type}{req_str}")
                    lines.append(f"  Description: {desc}")

                    # Show constraints
                    constraints = []
                    if "min" in param_def:
                        constraints.append(f"min: {param_def['min']}")
                    if "max" in param_def:
                        constraints.append(f"max: {param_def['max']}")
                    if "pattern" in param_def:
                        constraints.append(f"pattern: {param_def['pattern']}")
                    if "enum" in param_def:
                        constraints.append(f"enum: {param_def['enum']}")
                    if constraints:
                        lines.append(f"  Constraints: {', '.join(constraints)}")

            return "\n".join(lines)

        # Show missing parameters
        if self.missing_params:
            missing = ", ".join(f"'{p}'" for p in self.missing_params)
            lines.append(f"Missing required parameters: {missing}")

            # Show descriptions for missing parameters
            if self.param_definitions:
                lines.append("\nRequired parameters:")
                for param in self.missing_params:
                    param_def = self.param_definitions.get(param, {})
                    desc = param_def.get("description", "No description available")
                    param_type = param_def.get("type", "unknown")
                    required = param_def.get("required", False)
                    req_str = " (required)" if required else " (optional)"
                    lines.append(f"  - {param} ({param_type}){req_str}: {desc}")

            # Add note about operations layer pre-validation
            lines.append("\nNote: Use load_and_validate_data() for pre-validation")

        # Show provided parameters (filter out invalid ones)
        valid_provided = [p for p in self.provided_params if p in self.available_params]
        invalid_provided = [
            p for p in self.provided_params if p not in self.available_params
        ]

        if valid_provided:
            provided = ", ".join(f"'{p}'" for p in valid_provided)
            lines.append(f"\nProvided parameters: {provided}")

        if invalid_provided:
            invalid = ", ".join(f"'{p}'" for p in invalid_provided)
            lines.append(f"\nInvalid parameters (ignored): {invalid}")

        # Show all available parameters with descriptions
        # (show when there are missing params OR invalid params)
        if self.param_definitions and (self.missing_params or invalid_provided):
            lines.append("\nAll available parameters:")
            for param, param_def in self.param_definitions.items():
                desc = param_def.get("description", "No description available")
                param_type = param_def.get("type", "unknown")
                required = param_def.get("required", False)
                req_str = " (required)" if required else " (optional)"
                lines.append(f"  - {param} ({param_type}){req_str}: {desc}")

        return "\n".join(lines)


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
