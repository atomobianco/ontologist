from typing import Union

from rdflib import Graph, URIRef
from rdflib.namespace import DC, DCTERMS, RDFS, SKOS
from rdflib.term import Node

ANNOTATION_PROPERTIES: set[URIRef] = {
    URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#label"),
    RDFS.label,
    RDFS.comment,
    RDFS.seeAlso,
    DC.title,
    DC.description,
    DC.creator,
    DC.date,
    DCTERMS.created,
    DCTERMS.modified,
    DCTERMS.description,
    SKOS.prefLabel,
    SKOS.altLabel,
    SKOS.note,
    SKOS.definition,
}


def get_short_name(node: Node, graph: Graph) -> str:
    return node.n3(graph.namespace_manager)


def is_annotation_property(prop: Union[URIRef, Node]) -> bool:
    return prop in ANNOTATION_PROPERTIES
