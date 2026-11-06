"""ETL from w3id to prefixmaps."""

from prefixmaps.datamodel.context import Context

API_LIST_CALL = "https://api.github.com/repos/perma-id/w3id.org/git/trees/master:ids"


def from_w3id() -> Context:
    """
    Creates a Context from the https://github.com/perma-id/w3id.org/.

    Each directory under ``ids/`` in that repository is served as ``https://w3id.org/<name>/``.

    :return:
    """
    import requests

    r = requests.get(API_LIST_CALL)
    if r.status_code != 200:
        raise ValueError(f"{API_LIST_CALL} returned {r.status_code}: {r.text}")
    results = r.json()
    if results["truncated"]:
        raise ValueError("truncated results")
    ctxt = Context("w3id")
    for entry in r.json()["tree"]:
        if entry["type"] != "tree":
            continue
        path = entry["path"]
        if "." in path:
            # skip hidden files like .htaccess
            continue
        ctxt.add_prefix(path, f"https://w3id.org/{path}/")
    return ctxt
