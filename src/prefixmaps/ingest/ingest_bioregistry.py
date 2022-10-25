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


def from_bioregistry_upper(**kwargs) -> Context:
    """
    As :ref:`from_bioregistry` with default uppercase normalization on

    :param kwargs:
    :return:
    """
    return from_bioregistry(upper=True, **kwargs)


def from_bioregistry(upper=False, canonical_idorg=True, filter_dubious=True) -> Context:
    """
    Creates a Context from the bioregistry

    :param upper: if True, normalize prefix to uppercase
                    unless a preferred form is stated
    :param canonical_idorg: use the original/canonical identifiers.org PURLs
    :param filter_dubious: skip namespaces that do not match
                    strict namespace regular expression
    :return:
    """
    from bioregistry import get_prefix_map

    ctxt = Context("bioregistry", upper=upper)
    prefix_map = get_prefix_map(priority=priority, use_preferred=True)
    pm_non_preferred = get_prefix_map(priority=priority, use_preferred=False)
    pm_miriam = get_prefix_map(priority=["miriam"])
    for prefix, uri_prefix in prefix_map.items():
        preferred = prefix not in pm_non_preferred or prefix not in pm_miriam
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
