from pathlib import Path

import pytest
from rdflib import RDF, RDFS, Graph, URIRef

from ontologist.retrievers import (
    _convert_class_strings_to_uris,
    get_classes_from_definitions,
    get_data_properties,
    get_data_properties_with_domains,
    get_object_properties,
    get_subset,
)

RESOURCE_DIR = Path(__file__).parent / "resources"


def test_get_classes_from_definitions():
    o = Graph().parse(RESOURCE_DIR / "01-ontology.ttl", format="turtle")
    result = get_classes_from_definitions(o)
    assert result == {
        URIRef("http://example.com/exOnt#Animal"),
        URIRef("http://example.com/exOnt#Human"),
        URIRef("http://example.com/exOnt#Pet"),
        URIRef("http://example.com/exOnt#Teacher"),
        URIRef("http://example.com/exOnt#PreschoolTeacher"),
        URIRef("http://example.com/exOnt#Lizard"),
        URIRef("http://example.com/exOnt#Goanna"),
    }


def test_get_object_properties():
    o = Graph().parse(RESOURCE_DIR / "01-ontology.ttl", format="turtle")
    result = get_object_properties(o)
    assert result == {URIRef("http://example.com/exOnt#hasPet")}


def test_get_data_properties():
    o = Graph().parse(RESOURCE_DIR / "01-ontology.ttl", format="turtle")
    result = get_data_properties(o)
    assert result == {URIRef("http://example.com/exOnt#nLegs")}


def test_get_data_properties_with_domains():
    o = Graph().parse(RESOURCE_DIR / "01-ontology.ttl", format="turtle")
    result = get_data_properties_with_domains(o)
    assert result == {
        URIRef("http://example.com/exOnt#nLegs"): {
            URIRef("http://example.com/exOnt#Animal"),
            URIRef("http://www.w3.org/2002/07/owl#Thing"),
        },
    }


@pytest.mark.parametrize(
    "ont_graph_file, "
    "classes, "
    "depth, "
    "include_superclasses, "
    "include_subclasses, "
    "include_properties, "
    "subset_classes, "
    "subset_properties",
    [
        (
            "01-ontology.ttl",  # ont_graph_file
            ["exOnt:Animal"],  # classes
            0,  # depth
            False,  # include_superclasses
            False,  # include_subclasses
            True,  # include_properties
            ["exOnt:Animal"],  # subset_classes
            ["exOnt:nLegs"],  # subset_properties
        ),  # 0
        (
            "01-ontology.ttl",  # ont_graph_file
            ["exOnt:Teacher"],  # classes
            0,  # depth
            False,  # include_superclasses
            False,  # include_subclasses
            False,  # include_properties
            ["exOnt:Teacher"],  # subset_classes
            [],  # subset_properties
        ),  # 1
        (
            "01-ontology.ttl",  # ont_graph_file
            ["exOnt:Teacher"],  # classes
            0,  # depth
            False,  # include_superclasses
            False,  # include_subclasses
            True,  # include_properties
            ["exOnt:Teacher"],  # subset_classes
            [],  # subset_properties
        ),  # 2
        (
            "01-ontology.ttl",  # ont_graph_file
            ["exOnt:Teacher"],  # classes
            0,  # depth
            False,  # include_superclasses
            True,  # include_subclasses
            False,  # include_properties
            ["exOnt:Teacher", "exOnt:PreschoolTeacher"],  # subset_classes
            [],  # subset_properties
        ),  # 3
        (
            "01-ontology.ttl",  # ont_graph_file
            ["exOnt:Teacher"],  # classes
            0,  # depth
            True,  # include_superclasses
            False,  # include_subclasses
            True,  # include_properties
            ["exOnt:Teacher", "exOnt:Human", "exOnt:Animal"],  # subset_classes
            ["exOnt:nLegs"],  # subset_properties
        ),  # 4
        (
            "01-ontology.ttl",  # ont_graph_file
            ["exOnt:Teacher"],  # classes
            0,  # depth
            True,  # include_superclasses
            True,  # include_subclasses
            True,  # include_properties
            ["exOnt:Teacher", "exOnt:PreschoolTeacher", "exOnt:Human", "exOnt:Animal"],  # subset_classes
            ["exOnt:nLegs"],  # subset_properties
        ),  # 5
        (
            "01-ontology.ttl",  # ont_graph_file
            ["exOnt:Teacher"],  # classes
            1,  # depth
            True,  # include_superclasses
            True,  # include_subclasses
            True,  # include_properties
            [
                "exOnt:Teacher",
                "exOnt:PreschoolTeacher",
                "exOnt:Human",
                "exOnt:Animal",
                "exOnt:Pet",
                "exOnt:Lizard",
            ],  # subset_classes
            ["exOnt:nLegs", "exOnt:hasPet"],  # subset_properties
        ),  # 6
    ],
)
def test_get_subset(
    ont_graph_file,
    classes,
    depth,
    include_superclasses,
    include_subclasses,
    include_properties,
    subset_classes,
    subset_properties,
):
    o = Graph().parse(RESOURCE_DIR / ont_graph_file, format="turtle")
    s = get_subset(
        o,
        set(classes),
        depth,
        include_superclasses=include_superclasses,
        include_subclasses=include_subclasses,
        include_properties=include_properties,
    )
    s_ser = s.serialize(format="turtle")

    # Check that all expected classes are in the subset, excluding external resources
    for class_name in subset_classes:
        # Only check classes from our example ontology
        if class_name.startswith("exOnt:"):
            assert class_name in s_ser, f"Expected {class_name} to be in the subset"

    # Check that all expected properties are in the subset
    for prop_name in subset_properties:
        assert prop_name in s_ser, f"Expected {prop_name} to be in the subset"

    # Check that only the expected classes are in the subset
    for cls in o.subjects(RDF.type, RDFS.Class):
        cls_short_name = o.namespace_manager.qname(cls)
        if cls_short_name not in subset_classes:
            assert cls_short_name not in s_ser, f"Unexpected class {cls_short_name} found in the subset"

    # Check that only the expected properties are in the subset
    for prop in o.subjects(RDF.type, RDF.Property):
        prop_short_name = o.namespace_manager.qname(prop)
        if prop_short_name not in subset_properties:
            assert prop_short_name not in s_ser, f"Unexpected property {prop_short_name} found in the subset"


def test_convert_class_strings_to_uris():
    # Create a test graph with namespaces
    g = Graph()
    g.bind("exOnt", "http://example.com/exOnt#")

    # Test with prefixed name
    result = _convert_class_strings_to_uris({"exOnt:Teacher"}, g)
    assert URIRef("http://example.com/exOnt#Teacher") in result

    # Test with full URI
    result = _convert_class_strings_to_uris({"http://example.com/exOnt#Teacher"}, g)
    assert URIRef("http://example.com/exOnt#Teacher") in result

    # Test with both formats
    result = _convert_class_strings_to_uris({"exOnt:Teacher", "http://example.com/exOnt#Human"}, g)
    assert URIRef("http://example.com/exOnt#Teacher") in result
    assert URIRef("http://example.com/exOnt#Human") in result


def test_get_subset_with_full_uris():
    # Load test ontology
    ont_graph = Graph()
    ont_graph.parse(RESOURCE_DIR / "01-ontology.ttl", format="turtle")

    # Test with full URIs
    subset = get_subset(
        ont_graph,
        {"http://example.com/exOnt#Animal"},
        include_superclasses=False,
        include_subclasses=False,
    )

    # Verify the subset contains the Animal class
    assert (URIRef("http://example.com/exOnt#Animal"), None, None) in subset
