from dataclasses import dataclass, field
from typing import Optional, Union

from ontologist.rules import ViolationType


@dataclass
class Violation:
    """
    Base class for all validation violations.

    Represents a violation found during ontology validation.

    Args:
        instance_id: Identifier of the instance where the violation occurred
        violation_type: Type of the violation from ViolationType enum
        description: Human-readable description of the violation
        related_entities: List of entities related to this violation
        related_property: Optional property involved in the violation
        violating_value: Optional value that caused the violation
    """

    instance_id: str
    violation_type: ViolationType
    description: str
    related_entities: list[str] = field(default_factory=list)
    related_property: Optional[str] = None
    violating_value: Optional[Union[str, int, float]] = None

    def __hash__(self) -> int:
        return hash((
            self.instance_id,
            self.violation_type,
        ))

    def __post_init__(self) -> None:
        self.description = f"{self.violation_type.value}:\n\t{self.description}"


@dataclass
class UndefinedClassViolation(Violation):
    def __init__(self, instance_id: str, undefined_class: str):
        super().__init__(
            instance_id=instance_id,
            violation_type=ViolationType.UNDEFINED_CLASS,
            description=f"Instance '{instance_id}' refers to class '{undefined_class}' which is not defined in the ontology.",
            related_property=undefined_class,
        )

    def __hash__(self) -> int:
        return super().__hash__()


@dataclass
class UndefinedPropertyViolation(Violation):
    def __init__(self, instance_id: str, undefined_property: str):
        super().__init__(
            instance_id=instance_id,
            violation_type=ViolationType.UNDEFINED_PROPERTY,
            description=f"Instance '{instance_id}' uses property '{undefined_property}' which is not defined in the ontology.",
            related_property=undefined_property,
        )

    def __hash__(self) -> int:
        return super().__hash__()


@dataclass
class PropertyDomainViolation(Violation):
    def __init__(self, instance_id: str, property_name: str, invalid_type: str, expected_type: str):
        type_s = f"type '{invalid_type}'" if invalid_type else "undefined type"
        super().__init__(
            instance_id=instance_id,
            violation_type=ViolationType.PROPERTY_DOMAIN_VIOLATION,
            description=f"Property '{property_name}' can't have '{instance_id}' of {type_s} as domain, because this property requires domain types '{expected_type}'.",
            related_property=property_name,
            violating_value=invalid_type,
            related_entities=[expected_type],
        )

    def __hash__(self) -> int:
        return super().__hash__()


@dataclass
class PropertyRangeViolation(Violation):
    def __init__(self, instance_id: str, property_name: str, invalid_type: str, expected_type: str):
        type_s = f"type '{invalid_type}'" if invalid_type else "undefined type"
        super().__init__(
            instance_id=instance_id,
            violation_type=ViolationType.PROPERTY_RANGE_VIOLATION,
            description=f"Property '{property_name}' can't have '{instance_id}' of {type_s} as range, because this property requires range types '{expected_type}'.",
            related_property=property_name,
            violating_value=invalid_type,
            related_entities=[expected_type],
        )

    def __hash__(self) -> int:
        return super().__hash__()
