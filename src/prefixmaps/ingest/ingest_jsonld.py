import json
from typing import Any, Dict, List, Optional, TextIO, Union

import requests

from prefixmaps.datamodel.context import Context

AT_CONTEXT = "@context"

PREFIXCC_EXCLUDE = [
    "bp",
    "terms",
    "dc",
    "ma",
    "ont",
    "fb",
    "obo",
    "http",
    "dcterm",
    "dc11",
    "uniprot",
    "go",
    "gold",
    "chebi",
]


def from_jsonld_context_url(url: str, name: str, excludes: Optional[List[str]] = None) -> Context:
    response = requests.get(url=url)
    if name is None:
        name = url
    return from_jsonld_context(response.json(), name, excludes)


def from_jsonld_context_file(
    file: Union[TextIO, str], name: str, excludes: Optional[List[str]] = None
) -> Context:
    if isinstance(file, str):
        if name is None:
            name = file
        with open(file) as stream:
            return from_jsonld_context_file(stream, name, excludes)
    else:
        return from_jsonld_context(json.load(file), name, excludes)


def from_jsonld_context(
    jsonld_context: Dict[str, Any],
    name: str,
    excludes: Optional[List[str]] = None,
) -> Context:
    if name is None:
        raise ValueError("Must pass name")
    ctxt = Context(name)
    if AT_CONTEXT in jsonld_context:
        for k, v in jsonld_context[AT_CONTEXT].items():
            if k in excludes:
                continue
            if isinstance(v, str):
                ctxt.add_prefix(k, v)
            else:
                raise NotImplementedError("JSONLD 1.1 contexts not implemented")
        return ctxt
    else:
        raise ValueError(f"Expected {AT_CONTEXT}")


def from_prefixcc() -> Context:
    return from_jsonld_context_url("http://prefix.cc/context.jsonld", "prefixcc", PREFIXCC_EXCLUDE)
