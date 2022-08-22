import re

from prefixmaps.datamodel.context import Context

priority = ["obofoundry", "semweb", "miriam", "default", "bioportal", "ols", "n2t"]


def from_bioregistry_upper(**kwargs) -> Context:
    return from_bioregistry(upper=True, **kwargs)


def from_bioregistry(upper=False, canonical_idorg=True) -> Context:
    from bioregistry import get_prefix_map

    ctxt = Context("bioregistry", upper=upper)
    pm = get_prefix_map(priority=priority, use_preferred=True)
    pm_non_preferred = get_prefix_map(priority=priority, use_preferred=False)
    for k, v in pm.items():
        preferred = k not in pm_non_preferred
        if canonical_idorg:
            v = re.sub(
                r"^https://identifiers.org/(\S+):$", r"http://identifiers.org/\1/", v
            )
        ctxt.add_prefix(k, v, preferred=preferred)
    return ctxt
