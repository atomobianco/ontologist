from rdflib import Graph

from .models import (
    Violation,
)
from .validators import (
    validate_object_property_domain,
    validate_object_property_range,
    validate_type_compatibility,
    validate_undefined_class,
    validate_undefined_property,
)


def validate(data_graph: Graph, ont_graph: Graph) -> tuple[bool, set[Violation], str]:
    """
    Validate a data graph against an ontology graph.

    It checks for coherence between the two graphs and returns validation results.

    Args:
        data_graph: An rdflib Graph object representing the data graph to be validated.
        ont_graph: An rdflib Graph object representing the ontology graph.

    Returns:
        - bool: True if there are no violations, False otherwise
        - set[Violation]: Set of violation objects found during validation
        - str: Human-readable validation report
    """
    violations: set[Violation] = {
        *validate_undefined_class(data_graph, ont_graph),
        *validate_undefined_property(data_graph, ont_graph),
        *validate_object_property_domain(data_graph, ont_graph),
        *validate_object_property_range(data_graph, ont_graph),
        *validate_type_compatibility(data_graph, ont_graph),
    }

    conforms = len(violations) == 0

    if conforms:
        report = "Validation Report\nConforms: True\nResults (0):"
    else:
        violations_list = "\n".join(f"{v.description}" for v in violations)
        report = f"Validation Report\nConforms: False\nResults ({len(violations)}):\n{violations_list}"

    return conforms, violations, report
