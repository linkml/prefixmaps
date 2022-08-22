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


