"""Data manipulation and dynamic access for markdown documents."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, TypedDict, TypeVar, cast, get_type_hints

from .models import (
    BlocksData,
    ContentTree,
    FrontmatterProperties,
    FrontmatterPropertyValue,
    FrontmatterValue,
    MarkdownDataDict,
    ParsedMarkdownData,
    Section,
    SectionData,
    SectionPolicy,  # Alias for UpdatePolicy
    SectionsData,
    UpdatePolicy,
)
from .processor import MarkdownProcessor
from .validation import DocumentSchema, SchemaValidator, ValidationLevel


class UpdateInputDict(TypedDict, total=False):
    """Base for dict to define data for update."""

    policy: SectionPolicy


class InputDictSectionContent(UpdateInputDict):
    """Section input using markdown text."""

    content: str


class InputDictSectionData(SectionData, UpdateInputDict):
    """Structured section input (when section fields are provided
    additionally to policy"""

    pass


class InputDictSectionObject(UpdateInputDict):
    """Explicit section input (when Section object is provided)"""

    section: Section


class SectionUpdate(TypedDict, total=False):
    """Structure for section update in batch operation."""

    id: str  # Required
    content: str  # Required
    policy: str | SectionPolicy  # Optional, defaults to UPDATE


class BatchChanges(TypedDict, total=False):
    """Structure for batch changes to document."""

    frontmatter: dict[str, FrontmatterPropertyValue]
    frontmatter_policy: str | UpdatePolicy
    sections: list[SectionUpdate]


class BatchOperationResult(TypedDict):
    """Result of batch operation."""

    success: bool
    changes_count: int
    frontmatter_changes: int
    section_changes: int
    errors: list[str]
    warnings: list[str]


InputDataDictOptions = (
    InputDictSectionContent | InputDictSectionData | InputDictSectionObject
)

TDict = TypeVar("TDict", bound=InputDataDictOptions)


def validate_typed_dict(
    data: InputDataDictOptions | dict[str, Any], typed_dict_class: type[TDict]
) -> TDict | None:
    hints = get_type_hints(typed_dict_class)
    matches = all(
        key in data and isinstance(data[key], hint) for key, hint in hints.items()
    )
    return cast(TDict, data) if matches else None


InputDataOptions = FrontmatterValue | Section | InputDataDictOptions


class UpdateOperationTypes(Enum):
    """Public enum for operation types."""

    PROPERTY = "frontmatter"
    SECTION = "section"
    SECTION_TEXT = "section_text"
    SECTION_TEXT_STRUCTURED = "section_text_structured"
    SECTION_EXPLICIT = "section_explicit"
    SECTION_STRUCTURED = "section_structured"

    @classmethod
    def infer_from_value(cls, value: InputDataOptions) -> "UpdateOperationTypes":
        if isinstance(value, Section):
            return cls.SECTION
        if isinstance(value, str):
            if cls._looks_like_section_text(value):
                # Simple string, treat as frontmatter
                return cls.SECTION_TEXT
            else:
                return cls.PROPERTY
        if isinstance(value, int | float | bool | datetime):
            # Primitive types, treat as frontmatter
            return cls.PROPERTY
        if isinstance(value, list):
            # Lists are valid frontmatter values (e.g., tags, authors)
            return cls.PROPERTY
        if isinstance(value, dict):
            return cls._classify_dict_input(value)
        raise ValueError(f"Unsupported input type: {type(value)}")

    @classmethod
    def _classify_dict_input(
        cls, value: InputDataDictOptions
    ) -> "UpdateOperationTypes":
        """Classify dict as vorect type."""
        section_text = validate_typed_dict(value, InputDictSectionContent)
        if section_text is not None:
            return cls.SECTION_TEXT_STRUCTURED
        explicit_section = validate_typed_dict(value, InputDictSectionObject)
        if explicit_section is not None:
            return cls.SECTION_EXPLICIT
        structured_section = validate_typed_dict(value, InputDictSectionData)
        if structured_section is not None:
            return cls.SECTION_STRUCTURED
        return cls.PROPERTY

    @classmethod
    def _looks_like_section_text(cls, value: str) -> bool:
        """Check if string looks like section content."""
        # Multiline content
        if "\n" in value:
            return True

        # Long content (likely prose)
        if len(value) > 600:
            return True

        return False


@dataclass(frozen=True)
class UpdateOperation:
    """Represents a validated update operation for MarkdownData.
    Encapsulates all necessary information for validation and execution
    of updates to frontmatter properties or content sections.
    """

    TYPES = UpdateOperationTypes

    # Required fields
    target: str
    data: InputDataOptions
    type: UpdateOperationTypes
    policy: SectionPolicy | None = None

    # Computed fields
    # policy: SectionPolicy
    # prepared_data: Section | FrontmatterValue

    @property
    def dict_inputs(self) -> set["UpdateOperationTypes"]:
        """Operation types that accept dict inputs."""
        return {
            self.TYPES.SECTION_TEXT_STRUCTURED,
            self.TYPES.SECTION_STRUCTURED,
            self.TYPES.SECTION_EXPLICIT,
        }

    @property
    def text_inputs(self) -> set[UpdateOperationTypes]:
        """Operation types that accept text inputs."""
        return {self.TYPES.SECTION_TEXT, self.TYPES.SECTION_TEXT_STRUCTURED}

    @property
    def prepared_data(self) -> Section | FrontmatterValue:
        """Get prepared data for the operation."""
        return self._get_prepared_data(self.data, self.target)

    @property
    def section_policy(self) -> SectionPolicy:
        """Get policy for the operation."""
        if self.policy is not None:
            return self.policy
        return self._get_policy(self.data)

    def _get_policy(self, value: InputDataOptions) -> SectionPolicy:
        """Extract policy from dict input, defaulting to UPDATE."""
        if self in self.dict_inputs:
            value = cast(InputDataDictOptions, value)
            policy = value.get("policy")
            if isinstance(policy, SectionPolicy):
                return policy
            elif isinstance(policy, str):
                try:
                    return SectionPolicy(policy)
                except ValueError:
                    raise ValueError(f"Invalid policy value: {policy}")
            return SectionPolicy.UPDATE
        return SectionPolicy.UPDATE

    def _get_section_from_text(self, text: str, path: str) -> Section:
        """Parse markdown text to create Section."""
        processor = MarkdownProcessor()
        return processor.parse_content_to_section(text, path)

    def _get_prepared_data(
        self, value: InputDataOptions, path: str
    ) -> Section | FrontmatterValue:
        """Prepare data based on operation type."""
        if self.type == self.TYPES.PROPERTY:
            return cast(FrontmatterValue, value)

        if self.type == self.TYPES.SECTION:
            # If value is already a Section, return it
            if isinstance(value, Section):
                return value
            # Otherwise, treat it as text and convert to Section
            if isinstance(value, str):
                return self._get_section_from_text(value, path)
            else:
                raise ValueError(f"Cannot convert {type(value)} to Section")

        if self.type in self.text_inputs:
            if self == self.TYPES.SECTION_TEXT_STRUCTURED:
                dict_value = cast(InputDictSectionContent, value)
                text = dict_value["content"]
            else:
                text = cast(str, value)
                return self._get_section_from_text(text, path)

        if self.type == self.TYPES.SECTION_STRUCTURED:
            dict_value = cast(InputDictSectionData, value)
            dict_value = dict_value.copy()
            dict_value.pop("policy", None)
            return Section.from_dict(dict_value)

        if self.type == self.TYPES.SECTION_EXPLICIT:
            dict_value = cast(InputDictSectionObject, value)
            section_obj = dict_value.get("section")
            if not isinstance(section_obj, Section) or not dict_value:
                raise ValueError("Invalid Section object in input")
            return section_obj

        raise ValueError(f"Unsupported operation type: {self}")

    @property
    def is_content_operation(self) -> bool:
        """Check if operation targets content (section)."""
        return self.type in {
            self.TYPES.SECTION,
            self.TYPES.SECTION_TEXT,
            self.TYPES.SECTION_TEXT_STRUCTURED,
            self.TYPES.SECTION_EXPLICIT,
            self.TYPES.SECTION_STRUCTURED,
        }

    @property
    def is_property_operation(self) -> bool:
        """Check if operation targets frontmatter property."""
        return self.type == self.TYPES.PROPERTY


class MarkdownData:
    """Document with frontmatter and content structure.

    MarkdownData is the exclusive owner of the parser and handles all
    content parsing before delegating structural operations to ContentTree.
    """

    _content: ContentTree
    _frontmatter: FrontmatterProperties
    _schema: DocumentSchema | None
    _validator: SchemaValidator | None

    def __init__(
        self, parsed_data: ParsedMarkdownData, schema: DocumentSchema | None = None
    ) -> None:
        # Use object.__setattr__ to bypass our custom __setattr__ during init
        object.__setattr__(self, "_frontmatter", parsed_data["frontmatter"])
        object.__setattr__(self, "_content", parsed_data["content"])
        object.__setattr__(self, "_schema", schema)
        object.__setattr__(
            self, "_validator", SchemaValidator(schema) if schema else None
        )

    def __repr__(self) -> str:
        return (
            "<MarkdownData "
            f"properties={len(self.frontmatter.keys())} "
            f"sections={len(self.content.keys)} "
            f"frontmatter_keys={list(self.frontmatter.keys())}"
            ">"
        )

    def __dir__(self):
        """Include frontmatter keys in dir() output for better introspection."""
        return ["data"] + list(self.frontmatter.keys()) + self._content.keys

    @property
    def data(self) -> ParsedMarkdownData:
        """Get complete document data."""
        return {"frontmatter": self._frontmatter, "content": self._content}

    @property
    def frontmatter(self) -> FrontmatterProperties:
        """Get frontmatter dictionary."""
        return self._frontmatter

    @property
    def content(self) -> ContentTree:
        """Get content tree."""
        return self._content

    def get_section(self, section_id_or_path: str) -> Section | None:
        """Get section by ID or path."""
        return self._content.get_section(section_id_or_path)

    def get_all_sections(self) -> list[Section]:
        """Get all sections."""
        return self._content.get_all_sections()

    def __getattr__(self, name: str) -> FrontmatterPropertyValue | Section:
        """Dynamic access to frontmatter properties."""
        if name.startswith("_"):
            raise AttributeError("Cannot access private attribute")

        # First check if it's a frontmatter property
        if name in self.frontmatter:
            return self.frontmatter[name]

        if name in self._content.keys:
            section = self._content.__getattr__(name)
            if section is not None:
                return section

        # If not found in frontmatter, raise AttributeError for proper behavior
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    def get_sections(self) -> SectionsData:
        """Get all sections from the content tree as structured data."""
        sections_list = [
            section.to_dict() for section in self.content.get_all_sections()
        ]
        sections_by_id = {
            section.id: section.to_dict() for section in self.content.get_all_sections()
        }
        return {"sections": sections_list, "sections_by_id": sections_by_id}

    def get_blocks(self, section_id: str | None = None) -> BlocksData:
        """Get blocks from a specific section or all sections as structured data."""
        if section_id:
            section = self.content.get_section(section_id)
            if section:
                return {"blocks": [b.to_dict() for b in section.blocks]}
            return {"blocks": []}

        blocks = []
        for section in self.content.get_all_sections():
            blocks.extend([b.to_dict() for b in section.blocks])
        return {"blocks": blocks}

    # Update operations
    def infer_operation_type(
        self,
        name: str,
        value: InputDataOptions,
        policy: SectionPolicy | None = None,
    ) -> UpdateOperation:
        """Infer operation type from property name and value."""
        if not name or not isinstance(name, str):
            raise ValueError("Property name must be a non-empty string")
        if name.startswith("_"):
            raise AttributeError("Cannot modify private attribute")

        content_paths = self._content.paths
        property_list = list(self.frontmatter.keys())

        # Check if it's an existing section path/id first
        if name in content_paths:
            operation_type = UpdateOperationTypes.SECTION
        elif self.get_section(name) is not None:
            # Section exists by ID, treat as section operation
            operation_type = UpdateOperationTypes.SECTION
        elif name in property_list:
            operation_type = UpdateOperationTypes.PROPERTY
        else:
            operation_type = UpdateOperationTypes.infer_from_value(value)
        return UpdateOperation(
            target=name,
            type=operation_type,
            data=value,
            policy=policy,
        )

    # Validation methods

    def _validate_changes(self) -> None:
        """Validate document against schema if validator is configured."""
        if self._validator:
            result = self._validator.validate(self)
            if not result["valid"]:
                # Get validation level from schema
                validation_level = ValidationLevel(
                    self._schema.get("validation_level", ValidationLevel.WARNINGS)
                    if self._schema
                    else ValidationLevel.WARNINGS
                )

                if validation_level == ValidationLevel.STRICT:
                    # Raise error with all validation issues
                    error_messages = [issue["message"] for issue in result["errors"]]
                    raise ValueError(
                        f"Schema validation failed: {'; '.join(error_messages)}"
                    )
                # For WARNINGS level, validation errors are collected but not raised

    # Mutation methods

    def _set_frontmatter_property(self, operation: UpdateOperation) -> None:
        """Set frontmatter property."""
        key = operation.target
        value = cast(FrontmatterValue, operation.data)
        self._frontmatter[key] = value
        # Validate after mutation if schema is configured
        self._validate_changes()

    def _set_content(self, operation: UpdateOperation) -> None:
        """Set section content with policy support."""
        try:
            section = cast(Section, operation.prepared_data)
            section_path = operation.target
            policy = operation.section_policy
            # Delegate to ContentTree for structural operation
            self._content.set_section(section, section_path, policy)
            # Validate after mutation if schema is configured
            self._validate_changes()

        except (ValueError, TypeError) as e:
            raise ValueError(f"Failed to set section '{operation}': {e}") from e

    def __setattr__(self, name: str, value: InputDataOptions) -> None:
        """Dynamic property setting with clear input validation."""
        # Use the InputValidator for all validation and Section preparation
        operation = self.infer_operation_type(name, value)
        if operation.is_property_operation:
            self._set_frontmatter_property(operation)
        else:
            self._set_content(operation)

    # Public mutation methods
    def append_to_section(self, section_id_or_path: str, block_markdown: str) -> None:
        """Append a block of markdown to a section."""
        operation = UpdateOperation(
            target=section_id_or_path,
            type=UpdateOperationTypes.SECTION_TEXT,
            data=block_markdown,
            policy=SectionPolicy.APPEND,
        )
        self._set_content(operation)

    def replace_section(
        self, section_id_or_path: str, section_contents: InputDataOptions
    ) -> None:
        """Replace the entire content of a section."""
        # Force section operation type since this method is explicitly for sections
        operation = UpdateOperation(
            target=section_id_or_path,
            type=UpdateOperationTypes.SECTION_TEXT,
            data=section_contents,
            policy=SectionPolicy.REPLACE,
        )
        self._set_content(operation)

    def update_section(
        self, section_id_or_path: str, section_contents: InputDataOptions
    ) -> None:
        """Update (merge) content of a section."""
        # Force section operation type since this method is explicitly for sections
        operation = UpdateOperation(
            target=section_id_or_path,
            type=UpdateOperationTypes.SECTION_TEXT,
            data=section_contents,
            policy=SectionPolicy.UPDATE,
        )
        self._set_content(operation)

    def update_frontmatter(
        self,
        properties: dict[str, FrontmatterPropertyValue],
        policy: UpdatePolicy = UpdatePolicy.MERGE,
    ) -> None:
        """Update multiple frontmatter properties in batch with specified policy."""
        for key, value in properties.items():
            self._update_frontmatter_property(key, value, policy)

    def _update_frontmatter_property(
        self, key: str, new_value: FrontmatterPropertyValue, policy: UpdatePolicy
    ) -> None:
        """Update a single frontmatter property with policy support."""
        existing_value = self._frontmatter.get(key)

        if policy == UpdatePolicy.REPLACE or existing_value is None:
            # Replace or set new property
            self._frontmatter[key] = new_value
        elif policy in (UpdatePolicy.MERGE, UpdatePolicy.UPDATE):
            # Smart merge based on value types
            # (MERGE and UPDATE behave the same for frontmatter)
            if isinstance(existing_value, list) and isinstance(new_value, list):
                # Merge lists, avoiding duplicates
                merged_list = existing_value.copy()
                for item in new_value:
                    if item not in merged_list:
                        merged_list.append(item)
                self._frontmatter[key] = merged_list
            elif isinstance(existing_value, dict) and isinstance(new_value, dict):
                # Merge dictionaries
                merged_dict = existing_value.copy()
                merged_dict.update(new_value)
                self._frontmatter[key] = merged_dict
            else:
                # For non-mergeable types, replace
                self._frontmatter[key] = new_value
        elif policy == UpdatePolicy.APPEND:
            # Append to existing value (arrays only)
            if isinstance(existing_value, list) and isinstance(new_value, list):
                self._frontmatter[key] = existing_value + new_value
            elif isinstance(existing_value, list):
                self._frontmatter[key] = existing_value + [new_value]
            else:
                # If not a list, treat as replace
                self._frontmatter[key] = new_value

    def apply_batch_changes(self, changes: BatchChanges) -> BatchOperationResult:
        """Apply multiple changes from structured data.

        Args:
            changes: Dictionary containing frontmatter and section updates

        Returns:
            BatchOperationResult with success status and details
        """
        result: BatchOperationResult = {
            "success": True,
            "changes_count": 0,
            "frontmatter_changes": 0,
            "section_changes": 0,
            "errors": [],
            "warnings": [],
        }

        # Apply frontmatter updates
        if "frontmatter" in changes:
            frontmatter_data = changes["frontmatter"]
            policy = self._parse_update_policy(
                changes.get("frontmatter_policy", "merge"), result["warnings"]
            )

            try:
                self.update_frontmatter(frontmatter_data, policy)
                result["frontmatter_changes"] = len(frontmatter_data)
                result["changes_count"] += len(frontmatter_data)
            except Exception as e:
                result["errors"].append(f"Frontmatter update failed: {e}")
                result["success"] = False

        # Apply section updates
        if "sections" in changes:
            for section_update in changes["sections"]:
                section_id = "unknown"
                try:
                    section_id = section_update["id"]
                    content = section_update["content"]
                    policy = self._parse_section_policy(
                        section_update.get("policy", "update"), result["warnings"]
                    )

                    if policy == SectionPolicy.APPEND:
                        self.append_to_section(section_id, content)
                    elif policy == SectionPolicy.REPLACE:
                        self.replace_section(section_id, content)
                    else:
                        self.update_section(section_id, content)

                    result["section_changes"] += 1
                    result["changes_count"] += 1
                except Exception as e:
                    result["errors"].append(
                        f"Section update failed for '{section_id}': {e}"
                    )
                    result["success"] = False

        return result

    def _parse_update_policy(
        self, policy_value: str | UpdatePolicy, warnings: list[str]
    ) -> UpdatePolicy:
        """Parse policy value to UpdatePolicy enum.

        Args:
            policy_value: Policy as string or enum
            warnings: List to append warnings to

        Returns:
            UpdatePolicy enum value
        """
        if isinstance(policy_value, UpdatePolicy):
            return policy_value

        try:
            return UpdatePolicy[policy_value.upper()]
        except (KeyError, AttributeError):
            warnings.append(f"Invalid policy '{policy_value}', using MERGE")
            return UpdatePolicy.MERGE

    def _parse_section_policy(
        self, policy_value: str | SectionPolicy, warnings: list[str]
    ) -> SectionPolicy:
        """Parse policy value to SectionPolicy enum.

        Args:
            policy_value: Policy as string or enum
            warnings: List to append warnings to

        Returns:
            SectionPolicy enum value
        """
        if isinstance(policy_value, SectionPolicy):
            return policy_value

        try:
            return SectionPolicy[policy_value.upper()]
        except (KeyError, AttributeError):
            warnings.append(f"Invalid policy '{policy_value}', using UPDATE")
            return SectionPolicy.UPDATE

    # Serialization
    def to_dict(self) -> MarkdownDataDict:
        """Convert to JSON-serializable dictionary."""
        return {"frontmatter": self.frontmatter, "content": self.content.to_dict()}
