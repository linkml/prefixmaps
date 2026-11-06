"""Generic JSON-LD ingests."""

import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, TextIO, Union
from urllib.parse import urlparse

import requests
import yaml

from prefixmaps.data import data_path
from prefixmaps.datamodel.context import Context
from prefixmaps.io.parser import load_context

AT_CONTEXT = "@context"

PREFIXCC_URL = "http://prefix.cc/context.jsonld"

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
    """
    Ingests from a remote JSON-LD context.

    :param url:
    :param name:
    :param excludes:
    :return:
    """
    response = requests.get(url=url)
    if name is None:
        name = url
    return from_jsonld_context(response.json(), name, excludes)


def from_jsonld_context_file(
    file: Union[TextIO, str], name: str, excludes: Optional[List[str]] = None
) -> Context:
    """
    Ingests from a local JSON-LD context.

    :param file:
    :param name:
    :param excludes:
    :return:
    """
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
    """
    Ingests from a JSON-LD context stored as a dictionary.

    .. note::

        Does not support JSON-LD 1.1 contexts.

    :param jsonld_context:
    :param name:
    :param excludes:
    :return:
    """
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
    """
    Ingests from prefix.cc.

    Note that prefix.cc is an extremely messy source, but it can be useful
    for semweb namespaces.

    In order to prioritize "better" prefixes we have an exclusion list, that attempts to
    exclude the most egregious entries, and prioritize more official sources. However,
    there are still no guarantees as to quality.

    Longer term we should focus on the curated linked_data.yaml file, and
    moving this to bioregistry.

    Spam and broken entries listed in prefixcc.excluded.yaml are dropped.

    :return:
    """
    exclusions = load_prefixcc_exclusions()
    jsonld_context = requests.get(url=PREFIXCC_URL).json()
    if AT_CONTEXT in jsonld_context:
        jsonld_context[AT_CONTEXT] = {
            prefix: namespace
            for prefix, namespace in jsonld_context[AT_CONTEXT].items()
            if not (
                isinstance(namespace, str)
                and is_excluded_from_prefixcc(prefix, namespace, exclusions)
            )
        }
    return from_jsonld_context(jsonld_context, "prefixcc", PREFIXCC_EXCLUDE)


def from_prefixcc_snapshot() -> Context:
    """
    Loads the prefix.cc snapshot bundled with this package.

    prefix.cc has no curation, so it is not refreshed by default, see
    https://github.com/linkml/prefixmaps/issues/61. To fix a semweb prefix, add it to
    linked_data.curated.yaml, which takes precedence over prefix.cc in merged contexts.

    Entries listed in prefixcc.excluded.yaml are still dropped, so a new exclusion takes
    effect on the next ETL run. Canonical expansions come first, so that merging the
    snapshot gives the same statuses as merging a fresh download. That relies on prefix.cc
    having no prefix aliases, which holds because its prefixes are unique and lowercase.

    :return:
    """
    exclusions = load_prefixcc_exclusions()
    context = load_context("prefixcc")
    context.prefix_expansions = sorted(
        (
            pe
            for pe in context.prefix_expansions
            if not is_excluded_from_prefixcc(pe.prefix, pe.namespace, exclusions)
        ),
        key=lambda pe: not pe.canonical(),
    )
    return context


def load_prefixcc_exclusions(
    path: Path = data_path / "prefixcc.excluded.yaml",
) -> Mapping[str, Mapping[str, str]]:
    """
    Loads the prefix.cc entries that are never imported.

    :param path: the exclusions file
    :return: the excluded ``hosts`` and ``prefixes``, each mapped to the reason
    """
    with open(path, encoding="utf-8") as file:
        exclusions = yaml.safe_load(file) or {}
    unknown = set(exclusions) - {"hosts", "prefixes"}
    if unknown:
        # a misspelled key would otherwise silently disable those exclusions
        raise ValueError(f"unknown keys in {path.name}: {sorted(unknown)}")
    return {key: exclusions.get(key) or {} for key in ("hosts", "prefixes")}


def is_excluded_from_prefixcc(
    prefix: str, namespace: str, exclusions: Mapping[str, Mapping[str, str]]
) -> bool:
    """
    Checks whether a prefix.cc entry is excluded by its prefix or by its namespace's host.

    :param prefix:
    :param namespace:
    :param exclusions: as returned by :func:`load_prefixcc_exclusions`
    :return: True if the entry must not be imported
    """
    if prefix in exclusions["prefixes"]:
        return True
    try:
        host = (urlparse(namespace).hostname or "").rstrip(".")
    except ValueError:
        # not a URL with a parsable host, such as "http://[abc/"
        return False
    return any(
        host == excluded or host.endswith(f".{excluded}") for excluded in exclusions["hosts"]
    )
