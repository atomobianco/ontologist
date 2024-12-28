from typing import Union

from rdflib import Graph, URIRef
from rdflib.namespace import OWL, RDF, RDFS, XSD
from rdflib.term import BNode, Node


def get_classes_from_definitions(ontology: Graph) -> set[URIRef]:
    class_nodes: set[Node] = set()

    # Explicit class definitions
    class_nodes.update(ontology.subjects(RDF.type, RDFS.Class))
    class_nodes.update(ontology.subjects(RDF.type, OWL.Class))

    # OWL class axioms
    class_axioms = [OWL.equivalentClass, OWL.disjointWith, OWL.complementOf, OWL.unionOf, OWL.intersectionOf, OWL.oneOf]
    for axiom in class_axioms:
        class_nodes.update(ontology.subjects(axiom, None))
        class_nodes.update(ontology.objects(None, axiom))

    # Remove literal values and non-URIRefs
    class_uri_refs: set[URIRef] = {cls for cls in class_nodes if isinstance(cls, URIRef)}

    return class_uri_refs


def get_classes_from_instances(graph: Graph) -> set[URIRef]:
    class_nodes: set[Node] = set()

    # Classes inferred from instances
    class_nodes.update(graph.objects(None, RDF.type))

    # Remove literal values and non-URIRefs
    class_uri_refs: set[URIRef] = {cls for cls in class_nodes if isinstance(cls, URIRef)}

    return class_uri_refs


def get_object_properties(graph: Graph) -> set[URIRef]:
    # Get properties explicitly defined as ObjectProperties
    object_properties = set(graph.subjects(predicate=RDF.type, object=OWL.ObjectProperty))

    # Get regular properties that have a class as their range (not a literal)
    regular_properties = set(graph.subjects(predicate=RDF.type, object=RDF.Property))
    for prop in regular_properties:
        ranges = set(graph.objects(prop, RDFS.range))
        # Only include properties whose range is a class (not a literal type)
        if any(
            range_val
            for range_val in ranges
            if isinstance(range_val, URIRef) and not str(range_val).startswith(str(XSD))
        ):
            object_properties.add(prop)

    return {prop for prop in object_properties if isinstance(prop, URIRef)}


def get_object_properties_with_domains(ontology: Graph) -> dict[URIRef, set[URIRef]]:
    object_properties_with_domains: dict[URIRef, set[URIRef]] = {}
    object_properties = get_object_properties(ontology)
    for op in object_properties:
        domains = set(ontology.objects(subject=op, predicate=RDFS.domain))
        for d in list(domains):
            if isinstance(d, BNode):
                sub_graph = ontology.cbd(d)
                linked_domains = sub_graph.objects(predicate=RDF.first)
                domains.remove(d)
                domains.update(linked_domains)
            else:
                domains.update(get_superclasses(d, ontology))
        object_properties_with_domains[op] = {d for d in domains if isinstance(d, URIRef)}
    return object_properties_with_domains


def get_object_properties_with_ranges(ontology: Graph) -> dict[URIRef, set[URIRef]]:
    object_properties_with_ranges: dict[URIRef, set[URIRef]] = {}
    object_properties = get_object_properties(ontology)
    for op in object_properties:
        ranges = set(ontology.objects(subject=op, predicate=RDFS.range))
        for d in list(ranges):
            if isinstance(d, BNode):
                sub_graph = ontology.cbd(d)
                linked_domains = sub_graph.objects(predicate=RDF.first)
                ranges.remove(d)
                ranges.update(linked_domains)
            else:
                ranges.update(get_superclasses(d, ontology))
        object_properties_with_ranges[op] = {r for r in ranges if isinstance(r, URIRef)}
    return object_properties_with_ranges


def get_data_properties(graph: Graph) -> set[URIRef]:
    # Get properties explicitly defined as DataProperties
    data_properties = set(graph.subjects(predicate=RDF.type, object=OWL.DatatypeProperty))

    # Get regular properties that have a literal/XSD type as their range
    regular_properties = set(graph.subjects(predicate=RDF.type, object=RDF.Property))
    for prop in regular_properties:
        ranges = set(graph.objects(prop, RDFS.range))
        # Only include properties whose range is a literal type
        if any(isinstance(range_val, URIRef) and str(range_val).startswith(str(XSD)) for range_val in ranges):
            data_properties.add(prop)

    return {prop for prop in data_properties if isinstance(prop, URIRef)}


def get_data_properties_with_domains(graph: Graph) -> dict[URIRef, set[URIRef]]:
    data_properties_with_domains: dict[URIRef, set[URIRef]] = {}
    data_properties = get_data_properties(graph)
    for dp in data_properties:
        domains = set(graph.objects(subject=dp, predicate=RDFS.domain))
        for d in list(domains):
            if isinstance(d, BNode):
                sub_graph = graph.cbd(d)
                linked_domains = sub_graph.objects(predicate=RDF.first)
                domains.remove(d)
                domains.update(linked_domains)
            else:
                domains.update(get_superclasses(d, graph))
        data_properties_with_domains[dp] = {d for d in domains if isinstance(d, URIRef)}
    return data_properties_with_domains


def get_superclasses(cls: Union[URIRef, Node], ontology: Graph) -> set[Union[URIRef, Node]]:
    superclasses = set()
    to_visit = [cls]
    while to_visit:
        current = to_visit.pop()
        for superclass in ontology.objects(subject=current, predicate=RDFS.subClassOf):
            if superclass not in superclasses:
                superclasses.add(superclass)
                to_visit.append(superclass)
    return superclasses
