from typing import Optional, Union

from rdflib import Graph, URIRef
from rdflib.namespace import OWL, RDF, RDFS, XSD
from rdflib.term import BNode, Node

from .utils import is_annotation_property


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
    superclasses: set[Union[URIRef, Node]] = set()
    to_visit = [cls]
    while to_visit:
        current = to_visit.pop()
        for superclass in ontology.objects(subject=current, predicate=RDFS.subClassOf):
            if superclass not in superclasses:
                superclasses.add(superclass)
                to_visit.append(superclass)
    return superclasses


def get_all_classes_with_superclasses(instance: URIRef, data_graph: Graph, ont_graph: Graph) -> set[URIRef]:
    classes: set[URIRef] = set()
    for cls in data_graph.objects(subject=instance, predicate=RDF.type):
        if isinstance(cls, URIRef):
            classes.add(cls)
            superclasses = get_superclasses(cls, ont_graph)
            classes.update(sc for sc in superclasses if isinstance(sc, URIRef))
    return classes


def _convert_class_strings_to_uris(classes: set[str], ont_graph: Graph) -> set[URIRef]:
    """Convert string class identifiers to URIRef objects."""
    class_uris = set()
    for cls_str in classes:
        # If it's already a full URI, use it directly
        if cls_str.startswith("http://") or cls_str.startswith("https://"):
            class_uris.add(URIRef(cls_str))
        # Check if it's a prefixed name (contains a colon)
        elif ":" in cls_str:
            prefix, local = cls_str.split(":", 1)
            for prefix_ns, namespace in ont_graph.namespaces():
                if prefix == prefix_ns:
                    class_uris.add(URIRef(namespace + local))
                    break
            else:
                # If prefix not found in namespaces, try to expand using the graph's namespace manager
                try:
                    expanded_uri = ont_graph.namespace_manager.expand_curie(cls_str)
                    class_uris.add(expanded_uri)
                except Exception:
                    # If expansion fails, use as is
                    class_uris.add(URIRef(cls_str))
        else:
            # It's a simple string, use as is
            class_uris.add(URIRef(cls_str))
    return class_uris


def _collect_class_hierarchy(
    class_uris: set[URIRef], ont_graph: Graph, include_superclasses: bool, include_subclasses: bool
) -> set[URIRef]:
    """Collect classes from the hierarchy based on inclusion flags."""
    included_classes: set[URIRef] = set(class_uris)

    for cls in class_uris:
        # Include superclasses if requested
        if include_superclasses:
            superclasses = get_superclasses(cls, ont_graph)
            for sc in superclasses:
                if isinstance(sc, URIRef):
                    included_classes.add(sc)

        # Include subclasses if requested
        if include_subclasses:
            subclasses = set(ont_graph.subjects(RDFS.subClassOf, cls))
            for sc in subclasses:
                if isinstance(sc, URIRef):
                    included_classes.add(sc)

    return included_classes


def _find_related_classes(ont_graph: Graph, classes: set[URIRef]) -> set[URIRef]:
    """Find classes related to the given classes through properties."""
    related_classes: set[URIRef] = set()

    # Get properties with their domains and ranges
    obj_props_domains = get_object_properties_with_domains(ont_graph)
    obj_props_ranges = get_object_properties_with_ranges(ont_graph)

    # For each class
    for cls in classes:
        # Find properties where this class is in the domain
        for prop, domains in obj_props_domains.items():
            if cls in domains:
                # Add classes from the range of this property
                for r in ont_graph.objects(prop, RDFS.range):
                    if isinstance(r, URIRef):
                        related_classes.add(r)

        # Find properties where this class is in the range
        for prop, ranges in obj_props_ranges.items():
            if cls in ranges:
                # Add classes from the domain of this property
                for d in ont_graph.objects(prop, RDFS.domain):
                    if isinstance(d, URIRef):
                        related_classes.add(d)

    return related_classes


def _add_class_definitions(subset_graph: Graph, ont_graph: Graph, included_classes: set[URIRef]) -> None:
    """Add class definitions to the subset graph."""
    for cls in included_classes:
        # Add the class itself
        for p, o in ont_graph.predicate_objects(cls):
            # Skip subClassOf statements that reference classes not in our included set
            if p == RDFS.subClassOf and o not in included_classes:
                continue
            subset_graph.add((cls, p, o))

        # Add statements where the class is the object
        for s, p in ont_graph.subject_predicates(cls):
            # Skip subClassOf statements for classes not in our included set
            if p == RDFS.subClassOf and s not in included_classes:
                continue
            # Only add statements where the subject is also in included_classes
            if s in included_classes:
                subset_graph.add((s, p, cls))


def _get_direct_object_property_domains(ont_graph: Graph) -> dict[URIRef, set[URIRef]]:
    """Get direct domains for object properties without superclass expansion."""
    direct_domains = {}
    for prop in get_object_properties(ont_graph):
        domains = set(ont_graph.objects(subject=prop, predicate=RDFS.domain))
        direct_domains[prop] = {d for d in domains if isinstance(d, URIRef)}
    return direct_domains


def _get_direct_data_property_domains(ont_graph: Graph) -> dict[URIRef, set[URIRef]]:
    """Get direct domains for data properties without superclass expansion."""
    direct_domains = {}
    for prop in get_data_properties(ont_graph):
        domains = set(ont_graph.objects(subject=prop, predicate=RDFS.domain))
        direct_domains[prop] = {d for d in domains if isinstance(d, URIRef)}
    return direct_domains


def _add_properties_for_classes(
    subset_graph: Graph,
    ont_graph: Graph,
    focal_classes: set[URIRef],
    included_classes: set[URIRef],
    include_superclasses: bool,
) -> None:
    """Add properties for the given classes."""
    # Handle object properties
    _add_object_properties_for_classes(subset_graph, ont_graph, focal_classes, included_classes, include_superclasses)

    # Handle data properties
    _add_data_properties_for_classes(subset_graph, ont_graph, focal_classes, included_classes, include_superclasses)


def _add_object_properties_for_classes(
    subset_graph: Graph,
    ont_graph: Graph,
    focal_classes: set[URIRef],
    included_classes: set[URIRef],
    include_superclasses: bool,
) -> None:
    """Add object properties for the given classes."""
    if include_superclasses:
        _add_object_properties_with_superclasses(subset_graph, ont_graph, included_classes)
    else:
        _add_object_properties_without_superclasses(subset_graph, ont_graph, focal_classes, included_classes)


def _add_object_properties_with_superclasses(
    subset_graph: Graph,
    ont_graph: Graph,
    included_classes: set[URIRef],
) -> None:
    """Add object properties when superclasses are included."""
    obj_props_domains = get_object_properties_with_domains(ont_graph)

    for prop, domains in obj_props_domains.items():
        if any(domain in included_classes for domain in domains):
            # Check if the range is also in our included classes
            ranges = set(ont_graph.objects(prop, RDFS.range))
            if all(r in included_classes for r in ranges if isinstance(r, URIRef)):
                # Add the property definition
                for p, o in ont_graph.predicate_objects(prop):
                    subset_graph.add((prop, p, o))


def _add_object_properties_without_superclasses(
    subset_graph: Graph,
    ont_graph: Graph,
    focal_classes: set[URIRef],
    included_classes: set[URIRef],
) -> None:
    """Add object properties when superclasses are not included."""
    direct_obj_props_domains = _get_direct_object_property_domains(ont_graph)

    for prop, domains in direct_obj_props_domains.items():
        domain_matches = [domain for domain in domains if domain in focal_classes]
        if domain_matches:
            # Check if the range is in our included classes
            ranges = set(ont_graph.objects(prop, RDFS.range))
            if all(r in included_classes for r in ranges if isinstance(r, URIRef)):
                # Add the property definition
                type_value = ont_graph.value(prop, RDF.type)
                if type_value is not None:
                    subset_graph.add((prop, RDF.type, type_value))

                # Add domain and range statements
                for p, o in ont_graph.predicate_objects(prop):
                    if (
                        p == RDFS.domain
                        and o in domain_matches
                        or p == RDFS.range
                        and o in included_classes
                        or p != RDFS.domain
                        and p != RDFS.range
                    ):
                        subset_graph.add((prop, p, o))


def _add_data_properties_for_classes(
    subset_graph: Graph,
    ont_graph: Graph,
    focal_classes: set[URIRef],
    included_classes: set[URIRef],
    include_superclasses: bool,
) -> None:
    """Add data properties for the given classes."""
    if include_superclasses:
        data_props_domains = get_data_properties_with_domains(ont_graph)

        for prop, domains in data_props_domains.items():
            if any(domain in included_classes for domain in domains):
                # Add the property definition
                for p, o in ont_graph.predicate_objects(prop):
                    subset_graph.add((prop, p, o))
    else:
        direct_data_props_domains = _get_direct_data_property_domains(ont_graph)

        for prop, domains in direct_data_props_domains.items():
            domain_matches = [domain for domain in domains if domain in focal_classes]
            if domain_matches:
                # Add the property definition
                type_value = ont_graph.value(prop, RDF.type)
                if type_value is not None:
                    subset_graph.add((prop, RDF.type, type_value))

                # Add domain and range statements
                for p, o in ont_graph.predicate_objects(prop):
                    if p == RDFS.domain and o in domain_matches or p != RDFS.domain:
                        subset_graph.add((prop, p, o))


def _add_annotation_properties(subset_graph: Graph, ont_graph: Graph, included_classes: set[URIRef]) -> None:
    """Add annotation properties for included classes."""
    for s, p, o in ont_graph:
        if s in included_classes and is_annotation_property(p):
            subset_graph.add((s, p, o))


def _process_classes_recursively(
    subset_graph: Graph,
    ont_graph: Graph,
    focal_classes: set[URIRef],
    depth: int,
    include_superclasses: bool,
    include_subclasses: bool,
    include_properties: bool,
    include_annotations: bool,
    processed_classes: Optional[set[URIRef]] = None,
) -> None:
    """Process classes recursively up to the specified depth."""
    if processed_classes is None:
        processed_classes = set()

    # Skip already processed classes
    new_focal_classes = focal_classes - processed_classes
    if not new_focal_classes:
        return

    # Mark these classes as processed
    processed_classes.update(new_focal_classes)

    # Collect classes from the hierarchy for current focal classes
    included_classes = _collect_class_hierarchy(new_focal_classes, ont_graph, include_superclasses, include_subclasses)

    # Add class definitions to the subset graph
    _add_class_definitions(subset_graph, ont_graph, included_classes)

    # Include properties if requested
    if include_properties:
        _add_properties_for_classes(subset_graph, ont_graph, new_focal_classes, included_classes, include_superclasses)

    # Include annotation properties if requested
    if include_annotations:
        _add_annotation_properties(subset_graph, ont_graph, included_classes)

    # If we have more depth to explore, find related classes and process them
    if depth > 0:
        next_level_classes = _find_related_classes(ont_graph, included_classes)
        _process_classes_recursively(
            subset_graph,
            ont_graph,
            next_level_classes,
            depth - 1,
            include_superclasses,
            include_subclasses,
            include_properties,
            include_annotations,
            processed_classes,
        )


def get_subset(
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

    Uses a recursive approach to process classes at each depth level.
    """
    # Create a new graph for the subset
    subset_graph = Graph()

    # Copy namespace bindings from the original graph
    for prefix, namespace in ont_graph.namespaces():
        subset_graph.bind(prefix, namespace)

    # Convert string class URIs to URIRef objects
    class_uris = _convert_class_strings_to_uris(classes, ont_graph)

    # Process the focal classes recursively
    _process_classes_recursively(
        subset_graph,
        ont_graph,
        class_uris,
        depth,
        include_superclasses,
        include_subclasses,
        include_properties,
        include_annotations,
    )

    return subset_graph
