from rdflib import URIRef

from ontologist.utils import ANNOTATION_PROPERTIES, is_annotation_property


def test_is_annotation_property():
    for prop in ANNOTATION_PROPERTIES:
        assert is_annotation_property(prop), f"Property {prop} should be recognized as an annotation property"

    non_annotation_properties = {
        URIRef("http://example.org/customProperty"),
        URIRef("http://example.org/anotherProperty"),
        URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
        URIRef("http://www.w3.org/2000/01/rdf-schema#subClassOf"),
        URIRef("http://www.w3.org/2002/07/owl#equivalentClass"),
    }

    for prop in non_annotation_properties:
        assert not is_annotation_property(prop), f"Property {prop} should NOT be recognized as an annotation property"
