from enum import Enum


class ViolationType(Enum):
    """
    An Enum to define a finite set of ontology rules that can be violated.
    """

    UNDEFINED_CLASS = "Undefined class violation"
    # When a class is used but not defined in the ontology.

    UNDEFINED_PROPERTY = "Undefined property violation"
    # When a property is used but not defined in the ontology.

    PROPERTY_DOMAIN_VIOLATION = "Property domain violation"
    # When a property is used outside its defined domain.

    PROPERTY_RANGE_VIOLATION = "Property range violation"
    # When a property has a value outside its allowed range.

    ## TODO: Handle more violations
    CLASS_HIERARCHY = "Class hierarchy violation"
    # When a class is placed incorrectly within the hierarchy, breaking the logical structure.

    CARDINALITY_CONSTRAINT = "Cardinality constraint violation"
    # When the number of instances for a class or property exceeds or falls short of the specified cardinality.

    TYPE_MISMATCH = "Type mismatch violation"
    # When a data type or class type does not match the expected type.

    CIRCULAR_DEPENDENCY = "Circular dependency violation"
    # When a class or property is involved in a circular reference, causing an infinite loop.

    UNSATISFIABLE_CLASS = "Unsatisfiable class violation"
    # When a class cannot have any valid instances because of conflicting constraints.

    MISSING_SUBCLASS = "Missing subclass violation"
    # When a subclass expected by the ontology is not defined.

    INVERSE_PROPERTY_VIOLATION = "Inverse property violation"
    # When the relationship between two entities violates the inverse property rule.

    SYMMETRIC_PROPERTY_VIOLATION = "Symmetric property violation"
    # When a symmetric property is not properly mirrored in both directions.

    TRANSITIVE_PROPERTY_VIOLATION = "Transitive property violation"
    # When a transitive property does not hold across a chain of relationships.

    FUNCTIONAL_PROPERTY_VIOLATION = "Functional property violation"
    # When a functional property is violated by having more than one value for a single instance.

    INCONSISTENT_LABELING = "Inconsistent labeling violation"
    # When entities or properties are labeled in an inconsistent manner within the ontology.

    DEPRECATED_PROPERTY_USAGE = "Deprecated property usage violation"
    # When a property marked as deprecated is still in use.

    INVALID_DISJOINT_CLASS = "Invalid disjoint class violation"
    # When two classes are marked as disjoint but have overlapping instances.
