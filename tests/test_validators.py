from pathlib import Path

import pyshacl
import pytest
from rdflib import Graph

from ontologist import validate
from ontologist.rules import ViolationType

RESOURCE_DIR = Path(__file__).parent / "resources"


def test_validate_successful():
    d = Graph().parse(RESOURCE_DIR / "01-data.ttl", format="turtle")
    o = Graph().parse(RESOURCE_DIR / "01-ontology.ttl", format="turtle")
    conforms, violations, _ = validate(d, o)
    assert conforms, "Expected conformity"
    assert not violations, "Expected no violations"


def test_validate_property_type():
    d = Graph().parse(RESOURCE_DIR / "02-data.ttl", format="turtle")
    o = Graph().parse(RESOURCE_DIR / "02-ontology.ttl", format="turtle")
    conforms, violations, _ = validate(d, o)
    assert not conforms, "Expected non conformity"
    assert len(violations) == 1, "Expected 1 violation"
    assert {violation.violation_type for violation in violations} == {
        ViolationType.PROPERTY_TYPE_VIOLATION
    }, "Expected only type mismatch violations"


def test_validate_undefined_class():
    d = Graph().parse(RESOURCE_DIR / "03-data.ttl", format="turtle")
    o = Graph().parse(RESOURCE_DIR / "03-ontology.ttl", format="turtle")
    conforms, violations, _ = validate(d, o)
    assert not conforms, "Expected non conformity"
    assert len(violations) == 1, "Expected 1 violation"
    assert {violation.violation_type for violation in violations} == {
        ViolationType.UNDEFINED_CLASS
    }, "Expected only undefined class violations"


def test_validate_undefined_property():
    d = Graph().parse(RESOURCE_DIR / "04-data.ttl", format="turtle")
    o = Graph().parse(RESOURCE_DIR / "04-ontology.ttl", format="turtle")
    conforms, violations, _ = validate(d, o)
    assert not conforms, "Expected non conformity"
    assert len(violations) == 2, "Expected 2 violations"
    assert {violation.violation_type for violation in violations} == {
        ViolationType.UNDEFINED_PROPERTY
    }, "Expected only undefined property violations"
    undefined_props = {v.related_property for v in violations}
    assert undefined_props == {
        "exOnt:nArms",
        "exOnt:hasFriend",
    }, "Expected exOnt:nArms and exOnt:hasFriend to be undefined"


def _validate_with_pyshacl(data_graph: Graph, ont_graph: Graph, shape_graph: Graph) -> bool:
    results = pyshacl.validate(
        data_graph=data_graph,
        ont_graph=ont_graph,
        shacl_graph=shape_graph,
        inference="both",
        debug=True,
    )
    conforms, report_graph, report_text = results
    return conforms


@pytest.mark.parametrize(
    "data_graph_file, ont_graph_file, shape_graph_file, conforms_ours, conforms_pyshacl",
    [
        (
            "01-data.ttl",
            "01-ontology.ttl",
            "01-shape.ttl",
            True,
            True,
        ),
        (
            "02-data.ttl",
            "02-ontology.ttl",
            "02-shape.ttl",
            False,
            False,
        ),
        (
            "03-data.ttl",
            "03-ontology.ttl",
            "03-shape.ttl",
            False,
            True,
        ),
        (
            "04-data.ttl",
            "04-ontology.ttl",
            "04-shape.ttl",
            False,
            True,
        ),
    ],
)
def test_validate_against_pyshacl(data_graph_file, ont_graph_file, shape_graph_file, conforms_ours, conforms_pyshacl):
    d = Graph().parse(RESOURCE_DIR / data_graph_file, format="turtle")
    o = Graph().parse(RESOURCE_DIR / ont_graph_file, format="turtle")
    s = Graph().parse(RESOURCE_DIR / shape_graph_file, format="turtle")

    conforms, _, _ = validate(d, o)

    assert conforms == conforms_ours
    assert _validate_with_pyshacl(d, o, s) == conforms_pyshacl
