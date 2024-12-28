from pathlib import Path

from rdflib import Graph, URIRef

from ontologist.retrievers import (
    get_classes_from_definitions,
    get_data_properties,
    get_data_properties_with_domains,
    get_object_properties,
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
