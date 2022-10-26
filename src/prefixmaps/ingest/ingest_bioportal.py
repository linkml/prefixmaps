"""Simple ETL from bioportal to prefixmaps."""
from typing import Any, Dict, TextIO, Union

from prefixmaps.datamodel.context import Context

"""
In the future, Bioportal prefixes should be
retrieved from their API
(https://data.bioontology.org/documentation)
but are presently parsed from a curated set.
"""

def from_bioportal_file(file: Union[TextIO, str], name: str = None) -> Context:
    import yaml

    if isinstance(file, str):
        with open(file) as stream:
            return from_bioportal_file(stream, name)
    else:
        return from_bioportal(yaml.safe_load(file), name)


def from_bioportal(obj: Dict[str, Any], name: str = None) -> Context:
    if name is None:
        name = obj["name"]
    ctxt = Context(name)
    for prefix, uri_prefix in obj["prefixes"].items():
        ctxt.add_prefix(prefix, uri_prefix)
    return ctxt
