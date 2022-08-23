# prefixmaps

A python library for retrieving semantic prefix maps

A semantic prefix map will map a a prefix (e.g. `skos`) to a namespace (e.g `http://www.w3.org/2004/02/skos/core#`)

This library is designed to satisfy the following requirements

- coverage of prefixes from multiple different domains
- multiple authorities
- preferred semantic namespace is prioritized over web URLs
- authority preferred prefix is prioritized
- lightweight
- network-independence
- versioned prefix maps
- ability to retrieve latest from external authority on network

## Installation

```
pip install prefixmaps
```

## Usage

to use in combination with [curies](https://github.com/cthoyt/curies) library:

```python
from prefixmaps.io.parser import load_context, load_multi_context
from curies import Converter

ctxt = load_multi_context(["obo", "bioregistry.upper", "linked_data", "prefixcc"])
converter = Converter.from_prefix_map(ctxt.as_dict())

>>> converter.expand("CHEBI:1")
'http://purl.obolibrary.org/obo/CHEBI_1'
>>> converter.expand("GEO:1")
'http://purl.obolibrary.org/obo/GEO_1'
>>> converter.expand("owl:Class")
'http://www.w3.org/2002/07/owl#Class'
>>> converter.expand("FlyBase:FBgn123")
'http://identifiers.org/fb/FBgn123'
```

### Refresh

By default this will make use of metadata distributed alongside the package. This has certain advantages in terms
of reproducibility, but it means if a new ontology or prefix is added to an upstream source you won't see this.

To refresh and use the latest upstream:

```python
ctxt = load_context("obo", refresh=True)
```

### Order

order is significant - sources listed first will take priority. The as_dict method ensures that the map is bijective

## Contexts

See [contexts.curated.yaml](src/prefixmaps/data/contexts.curated.yaml)

See the description fields
