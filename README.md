# ontologist

[![Release](https://img.shields.io/github/v/release/atomobianco/ontologist)](https://img.shields.io/github/v/release/atomobianco/ontologist)
[![Build status](https://img.shields.io/github/actions/workflow/status/atomobianco/ontologist/main.yml?branch=main)](https://github.com/atomobianco/ontologist/actions/workflows/main.yml?query=branch%3Amain)
[![License](https://img.shields.io/github/license/atomobianco/ontologist)](https://img.shields.io/github/license/atomobianco/ontologist)

A Python library for validating RDF data alignment with ontologies without requiring SHACL definitions.

- **Github repository**: <https://github.com/atomobianco/ontologist/>

## Why onto-match?

When working with Large Language Models (LLMs) to extract RDF data based on ontologies, it's crucial to verify that the extracted data aligns correctly with the target ontology.
While tools like [pySHACL](https://github.com/RDFLib/pySHACL) exist for RDF validation, they may require explicit SHACL shape definitions, or may fail on certain validation checks.

This library provides a programmatic approach to verify ontology alignment, making it particularly suitable for:

- Validating LLM-extracted RDF data
- Working with ontologies that lack SHACL definitions
- Getting detailed violation reports for debugging and improvement

## Features

- Validate RDF data against ontology definitions without SHACL
- Detect undefined classes and properties
- Verify property domain and range constraints
- Provide detailed violation reports

## Installation

```bash
pip install onto-match
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
```
