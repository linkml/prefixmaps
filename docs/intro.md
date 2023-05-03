# Introduction

A python library for retrieving semantic prefix maps

A semantic prefix map will map a a prefix (e.g. `skos`) to a namespace (e.g `http://www.w3.org/2004/02/skos/core#`)

This library is designed to satisfy the following requirements

- coverage of prefixes from multiple different domains
- no single authoritative source of either prefixes or prefix-namespace mappings (clash-resilient)
- preferred semantic namespace is prioritized over web URLs
- authority preferred prefix is prioritized where possible
- each individual prefixmap is case-insensitive bijective
- prefixmap composition and custom ordering of prefixmaps
- lightweight / low footprint
- fast (TODO)
- network-independence / versioned prefix maps
- optional ability to retrieve latest from external authority on network

## Installation

```
pip install prefixmaps
```

## Usage

to use in combination with [curies](https://github.com/cthoyt/curies) library:

```python
from prefixmaps.io.parser import load_multi_context
from curies import Converter

context = load_multi_context(["obo", "bioregistry.upper", "linked_data", "prefixcc"])
extended_prefix_map = context.as_extended_prefix_map()
converter = Converter.from_extended_prefix_map(extended_prefix_map)

>>> converter.expand("CHEBI:1")
'http://purl.obolibrary.org/obo/CHEBI_1'
>>> converter.expand("GEO:1")
'http://purl.obolibrary.org/obo/GEO_1'
>>> converter.expand("owl:Class")
'http://www.w3.org/2002/07/owl#Class'
>>> converter.expand("FlyBase:FBgn123")
'http://identifiers.org/fb/FBgn123'
```

### Alternate orderings / clash resilience

- prefix.cc uses the prefix `geo` for geosparql `http://www.opengis.net/ont/geosparql#`
- OBO uses prefix `GEO` for the [Geographical Entity Ontology](https://obofoundry.org/ontology/geo), expanding to `http://purl.obolibrary.org/obo/GEO_`
- the Bioregistry uses the prefix [`geo`](https://bioregistry.io/registry/geo) for NCBI GEO, and "re-mints" a [`geogeo`](https://bioregistry.io/registry/geogeo) prefix for the OBO ontology

If we prioritize prefix.cc the OBO prefix is ignored:

```python
>>> ctxt = load_multi_context(["prefixcc", "obo"])
>>> extended_prefix_map = context.as_extended_prefix_map()
>>> converter = Converter.from_extended_prefix_map(extended_prefix_map)
>>> converter.expand("GEO:1")
>>> converter.expand("geo:1")
'http://www.opengis.net/ont/geosparql#1'
```

Even though prefix expansion is case sensitive, we intentionally block conflicts that differ only in case.

If we push bioregistry at the start of the list then GEOGEO can be used as the prefix for the OBO ontology

```python
>>> ctxt = load_multi_context(["bioregistry", "prefixcc", "obo"])
>>> extended_prefix_map = context.as_extended_prefix_map()
>>> converter = Converter.from_extended_prefix_map(extended_prefix_map)
>>> converter.expand("geo:1")
'http://identifiers.org/geo/1'
>>> converter.expand("GEO:1")
>>> converter.expand("GEOGEO:1")
'http://purl.obolibrary.org/obo/GEO_1'
```

Note that from the OBO perspective, GEOGEO is non-canonical

We get similar results using the upper-normalized variant of bioregistry:

```python
>>> ctxt = load_multi_context(["bioregistry.upper", "prefixcc", "obo"])
>>> extended_prefix_map = context.as_extended_prefix_map()
>>> converter = Converter.from_extended_prefix_map(extended_prefix_map)
>>> converter = Converter.from_extended_prefix_map(extended_prefix_map)
>>> converter = Converter.from_extended_prefix_map(extended_prefix_map)
>>> converter.expand("GEO:1")
'http://identifiers.org/geo/1'
>>> converter.expand("geo:1")
>>> converter.expand("GEOGEO:1")
'http://purl.obolibrary.org/obo/GEO_1'
```

Users of OBO ontologies will want to place OBO at the start of the list:

```python
>>> ctxt = load_multi_context(["obo", "bioregistry.upper", "prefixcc"])
>>> extended_prefix_map = context.as_extended_prefix_map()
>>> converter = Converter.from_extended_prefix_map(extended_prefix_map)
>>> converter.expand("geo:1")
>>> converter.expand("GEO:1")
'http://purl.obolibrary.org/obo/GEO_1'
>>> converter.expand("GEOGEO:1")
```

Note under this ordering there is no prefix for NCBI GEO. This is not
a major limitation as there is no canonical semantic rendering of NCBI
GEO. This could be added in future with a unique OBO prefix.

You can use the ready-made "merged" prefix set, which prioritizes OBO:

```python
>>> ctxt = load_context("merged")
>>> extended_prefix_map = context.as_extended_prefix_map()
>>> converter = Converter.from_extended_prefix_map(extended_prefix_map)
>>> converter.expand("GEOGEO:1")
>>> converter.expand("GEO:1")
'http://purl.obolibrary.org/obo/GEO_1'
>>> converter.expand("geo:1")
```

### Network independence and requesting latest versions

By default this will make use of metadata distributed alongside the package. This has certain advantages in terms
of reproducibility, but it means if a new ontology or prefix is added to an upstream source you won't see this.

To refresh and use the latest upstream:

```python
ctxt = load_context("obo", refresh=True)
```

This will perform a fetch from http://obofoundry.org/registry/obo_prefixes.ttl

## Context Metadata

See [contexts.curated.yaml](src/prefixmaps/data/contexts.curated.yaml)

See the description fields

## Code organization

Data files containing pre-build prefix maps using sources like OBO and Bioregistry are distributed alongside the python

Location:

 * [src/prefixmaps/data](src/prefixmaps/data/)

These can be regenerated using:

```
make etl
```

TODO: make a github action that auto-released new versions

## Requesting new prefixes

This repo is NOT a prefix registry. Its job is simply to aggregate
different prefix maps. Request changes upstream.
