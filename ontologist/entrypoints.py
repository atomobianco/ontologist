from rdflib import Graph

from .models import (
    Violation,
)
from .retrievers import get_subset
from .validators import (
    validate_object_property_domain,
    validate_object_property_range,
    validate_property_type,
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
        *validate_property_type(data_graph, ont_graph),
    }

    conforms = len(violations) == 0

    if conforms:
        report = "Validation Report\nConforms: True\nResults (0):"
    else:
        violations_list = "\n".join(f"{v.description}" for v in violations)
        report = f"Validation Report\nConforms: False\nResults ({len(violations)}):\n{violations_list}"

    return conforms, violations, report


def subset(
    ont_graph: Graph,
    classes: set[str],
    depth: int = 0,
    include_superclasses: bool = True,
    include_subclasses: bool = True,
    include_properties: bool = True,
    include_annotations: bool = True,
) -> Graph:
    """
    Extract a subset of an ontology centered around specified focal classes.

    Args:
        ont_graph: The source RDF graph containing the full ontology
        classes: Set of class URIs to use as starting points for extraction
        depth: How many relationship steps to traverse from focal classes (default: 0)
        include_properties: Whether to include properties that connect included classes (default: True)
        include_annotations: Whether to include annotation properties (default: True)
        include_superclasses: Whether to include parent classes (default: True)
        include_subclasses: Whether to include child classes (default: True)

    Returns:
        A new RDF graph containing the extracted ontology subset
    """
    subset_graph = get_subset(
        ont_graph, classes, depth, include_superclasses, include_subclasses, include_properties, include_annotations
    )
    return subset_graph
