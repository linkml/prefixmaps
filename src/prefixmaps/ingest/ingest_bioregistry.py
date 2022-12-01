"""ETL from bioregistry to prefixmaps."""
import logging
import re

from prefixmaps.datamodel.context import NAMESPACE_RE, Context

priority = [
    "obofoundry",
    "semweb",
    "miriam",
    "default",
    "bioportal",
    "ols",
    "n2t",
]
"""Priority order for bioregistry."""


def from_bioregistry_upper(**kwargs) -> Context:
    """
    As :ref:`from_bioregistry`, with default uppercase normalization on

    :param kwargs: pass-through to :ref:`from_bioregistry`
    :return:
    """
    return from_bioregistry(upper=True, **kwargs)


def from_bioregistry(upper=False, canonical_idorg=True, filter_dubious=True) -> Context:
    """
    Creates a Context from the bioregistry.

    This will transform bioregistry entries into semantic prefix expansions.

    Note: in future some of the logic from this can migrate up to the main
    bioregistries repository. For now, we deal with additional corner cases:

    URLs that look like they are not intended to be used as semantic URIs are
    filtered by default. This can be disabled with ``filter_dubious=False``.

    This method also has special handling for the identifiers.org registry
    (aka "miriam"). This is because a number of triplestores have historically
    used URIs of the form "http://identifiers.org/Prefix/LocalId" as the
    subject of their triples. While this is bad practice for "born semantic"
    IDs such as those in OBO, a lot of the bio-semantic web community have
    adopted this practice to provide semantic URIs non-born-semantic databases.
    In order to support this use case, we have an option to preserve these
    original namespaces. This can be disabled with ``canonical_idorg=False``.

    :param upper: if True, normalize prefix to uppercase
                    unless a preferred form is stated
    :param canonical_idorg: use the original/canonical identifiers.org PURLs
    :param filter_dubious: skip namespaces that do not match
                    strict namespace regular expression
    :return:
    """
    from bioregistry import get_prefix_map, get_resource

    ctxt = Context("bioregistry", upper=upper)
    # We always set use_preferred=True, which ensures that OBO prefixes
    # are either capitalized (e.g. GO) or use the preferred form (e.g. FBbt)
    prefix_map = get_prefix_map(priority=priority, use_preferred=True)
    pm_non_preferred = get_prefix_map(priority=priority, use_preferred=False)
    pm_miriam = get_prefix_map(priority=["miriam"])
    for prefix, uri_prefix in prefix_map.items():
        preferred = prefix not in pm_non_preferred or prefix not in pm_miriam
        if get_resource(prefix).deprecated:
            continue
        if canonical_idorg:
            uri_prefix = re.sub(
                r"^https://identifiers.org/(\S+):$",
                r"http://identifiers.org/\1/",
                uri_prefix,
            )
        if filter_dubious and not NAMESPACE_RE.match(uri_prefix):
            logging.debug(f"Skipping dubious ns {prefix} => {uri_prefix}")
            continue

        ctxt.add_prefix(prefix, uri_prefix, preferred=preferred)
    return ctxt
