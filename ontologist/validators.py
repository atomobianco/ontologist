from rdflib import RDF, RDFS, Graph, Literal, URIRef

from ontologist.models import (
    PropertyDomainViolation,
    PropertyRangeViolation,
    TypeMismatchViolation,
    UndefinedClassViolation,
    UndefinedPropertyViolation,
    Violation,
)
from ontologist.retrievers import (
    get_classes_from_definitions,
    get_classes_from_instances,
    get_data_properties,
    get_object_properties,
    get_object_properties_with_domains,
    get_object_properties_with_ranges,
    get_superclasses,
)
from ontologist.utils import get_short_name, is_annotation_property


def validate_undefined_class(data_graph: Graph, ont_graph: Graph) -> set[Violation]:
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


def validate_undefined_property(data_graph: Graph, ont_graph: Graph) -> set[Violation]:
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


def validate_object_property_domain(data_graph: Graph, ont_graph: Graph) -> set[Violation]:
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


def validate_object_property_range(data_graph: Graph, ont_graph: Graph) -> set[Violation]:
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


def validate_type_compatibility(data_graph: Graph, ont_graph: Graph) -> set[Violation]:
    violations: set[Violation] = set()

    data_property_ranges = {}
    for prop in get_data_properties(ont_graph):
        ranges = set(ont_graph.objects(prop, RDFS.range))
        if ranges:
            data_property_ranges[prop] = ranges

    for s, p, o in data_graph:
        if isinstance(p, URIRef) and p in data_property_ranges:
            expected_type = data_property_ranges[p]
            if isinstance(o, Literal) and o.datatype not in expected_type:
                violations.add(
                    TypeMismatchViolation(
                        instance_id=get_short_name(s, data_graph),
                        invalid_type=str(o.datatype),
                        expected_type=", ".join(str(t) for t in expected_type),
                    )
                )

    return violations
