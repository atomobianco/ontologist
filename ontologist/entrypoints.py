from rdflib import RDF, Graph, URIRef

from .models import (
    PropertyDomainViolation,
    PropertyRangeViolation,
    UndefinedClassViolation,
    UndefinedPropertyViolation,
    Violation,
)
from .retrievers import (
    get_classes_from_definitions,
    get_classes_from_instances,
    get_data_properties,
    get_object_properties,
    get_object_properties_with_domains,
    get_object_properties_with_ranges,
    get_superclasses,
)
from .utils import get_short_name, is_annotation_property


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
        *_validate_undefined_class(data_graph, ont_graph),
        *_validate_undefined_property(data_graph, ont_graph),
        *_validate_object_property_domain(data_graph, ont_graph),
        *_validate_object_property_range(data_graph, ont_graph),
    }

    conforms = len(violations) == 0

    if conforms:
        report = "Validation Report\nConforms: True\nResults (0):"
    else:
        violations_list = "\n".join(f"{v.description}" for v in violations)
        report = f"Validation Report\nConforms: False\nResults ({len(violations)}):\n{violations_list}"

    return conforms, violations, report


def _validate_undefined_class(data_graph: Graph, ont_graph: Graph) -> set[Violation]:
    ontology_classes = get_classes_from_definitions(ont_graph)
    graph_classes = get_classes_from_instances(data_graph)

    undefined_classes = graph_classes - ontology_classes
    violations: set[Violation] = set()

    if undefined_classes:
        for s, _, o in data_graph:
            if o in undefined_classes:
                instance_id = get_short_name(s, data_graph)
                undefined_class = get_short_name(o, data_graph)
                violations.add(UndefinedClassViolation(instance_id=instance_id, undefined_class=undefined_class))

    return violations


def _validate_undefined_property(data_graph: Graph, ont_graph: Graph) -> set[Violation]:
    """
    Spot properties in the test graph that are not defined on the classes in the reference ontology.
    Annotation properties are excluded from validation.
    """
    defined_object_properties = get_object_properties(ont_graph)
    defined_data_properties = get_data_properties(ont_graph)
    violations: set[Violation] = set()

    for s, p, _ in data_graph:
        if p == RDF.type or is_annotation_property(p):
            continue

        if isinstance(p, URIRef) and p not in defined_object_properties and p not in defined_data_properties:
            violations.add(
                UndefinedPropertyViolation(
                    instance_id=get_short_name(s, data_graph),
                    undefined_property=get_short_name(p, data_graph),
                )
            )

    return violations


def _validate_object_property_domain(data_graph: Graph, ont_graph: Graph) -> set[Violation]:
    relations_mapped_to_allowed_domains = get_object_properties_with_domains(ont_graph)
    violations: set[Violation] = set()

    for s, p, o in data_graph:
        s_name = get_short_name(s, data_graph)
        p_name = get_short_name(p, data_graph)
        if isinstance(o, URIRef) and isinstance(s, URIRef) and isinstance(p, URIRef) and p != URIRef(RDF.type):
            s_classes = set(data_graph.objects(subject=s, predicate=RDF.type))
            for cls in list(s_classes):
                s_classes.update(get_superclasses(cls, ont_graph))

            o_classes = set(data_graph.objects(subject=o, predicate=RDF.type))
            for cls in list(o_classes):
                o_classes.update(get_superclasses(cls, ont_graph))

            if p in relations_mapped_to_allowed_domains:
                allowed_domain_classes = relations_mapped_to_allowed_domains[p]
                if not allowed_domain_classes.intersection(s_classes):
                    violations.add(
                        PropertyDomainViolation(
                            instance_id=s_name,
                            property_name=p_name,
                            invalid_type=", ".join([get_short_name(cls, data_graph) for cls in s_classes]),
                            expected_type=", ".join([
                                get_short_name(cls, data_graph) for cls in allowed_domain_classes
                            ]),
                        )
                    )

    return violations


def _validate_object_property_range(data_graph: Graph, ont_graph: Graph) -> set[Violation]:
    relations_mapped_to_allowed_ranges = get_object_properties_with_ranges(ont_graph)
    violations: set[Violation] = set()

    for s, p, o in data_graph:
        p_name = get_short_name(p, data_graph)
        o_name = get_short_name(o, data_graph)
        if isinstance(o, URIRef) and isinstance(s, URIRef) and isinstance(p, URIRef) and p != URIRef(RDF.type):
            s_classes = set(data_graph.objects(subject=s, predicate=RDF.type))
            for cls in list(s_classes):
                s_classes.update(get_superclasses(cls, ont_graph))

            o_classes = set(data_graph.objects(subject=o, predicate=RDF.type))
            for cls in list(o_classes):
                o_classes.update(get_superclasses(cls, ont_graph))

            if p in relations_mapped_to_allowed_ranges:
                allowed_range_classes = relations_mapped_to_allowed_ranges[p]
                if not allowed_range_classes.intersection(o_classes):
                    violations.add(
                        PropertyRangeViolation(
                            instance_id=o_name,
                            property_name=p_name,
                            invalid_type=", ".join([get_short_name(cls, data_graph) for cls in o_classes]),
                            expected_type=", ".join([get_short_name(cls, data_graph) for cls in allowed_range_classes]),
                        )
                    )

    return violations
