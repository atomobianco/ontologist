# ontologist

[![Release](https://img.shields.io/github/v/release/atomobianco/ontologist)](https://img.shields.io/github/v/release/atomobianco/ontologist)
[![Build status](https://img.shields.io/github/actions/workflow/status/atomobianco/ontologist/main.yml?branch=main)](https://github.com/atomobianco/ontologist/actions/workflows/main.yml?query=branch%3Amain)
[![License](https://img.shields.io/github/license/atomobianco/ontologist)](https://img.shields.io/github/license/atomobianco/ontologist)

A Python library for validating RDF data alignment with ontologies without requiring shape resources.

- **Github repository**: <https://github.com/atomobianco/ontologist/>

## Why?

When working with Large Language Models (LLMs) to extract RDF data based on ontologies, it's crucial to verify that the extracted data aligns correctly with the target ontology.
While tools like [pySHACL](https://github.com/RDFLib/pySHACL) or [PyShEx](https://github.com/hsolbrig/PyShEx) exist for RDF validation, they may require additional shape resources, or may fail on certain validation checks.

This library provides a programmatic approach to verify ontology alignment, making it particularly suitable for:

- Validating LLM-extracted RDF data
- Working with ontologies that lack shape definitions
- Getting detailed violation reports for debugging and improvement

## Installation

```bash
pip install ontologist
```

## Quick Start

```python
from rdflib import Graph
from ontologist import validate

# Load your ontology and data graphs
data = Graph().parse("your_data.ttl")
ontology = Graph().parse("your_ontology.ttl")

# Validate the data
is_valid, violations, report = validate(data, ontology)

print(report)
```

```
Validation Report
Conforms: False
Results (1):
PROPERTY type violation:
	Property 'ex:Prop1' of instance 'ex:Class1' can't have value of type 'http://www.w3.org/2001/XMLSchema#string' because it requires type 'http://www.w3.org/2001/XMLSchema#integer'.

```
