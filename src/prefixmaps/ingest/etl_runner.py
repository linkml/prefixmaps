from pathlib import Path
from typing import Union

import click

from prefixmaps.datamodel.context import CONTEXT, Context
from prefixmaps.ingest.ingest_bioregistry import (
    from_bioregistry,
    from_bioregistry_upper,
)
from prefixmaps.ingest.ingest_go import parse_go_xrefs_from_remote
from prefixmaps.ingest.ingest_jsonld import from_prefixcc
from prefixmaps.ingest.ingest_linkml import from_semweb_curated
from prefixmaps.ingest.ingest_shacl import from_obo
from prefixmaps.io.writer import context_to_file

# TODO: replace this with introspection from metadata file
CONTEXTS = {
    "obo": from_obo,
    "go": parse_go_xrefs_from_remote,
    "linked_data": from_semweb_curated,
    "bioregistry.upper": from_bioregistry_upper,
    "bioregistry": from_bioregistry,
    "prefixcc": from_prefixcc,
}
COMBINED = {
    "merged": ["obo", "go", "linked_data", "bioregistry.upper", "prefixcc"],
    "merged.oak": ["obo", "go", "linked_data", "bioregistry.upper", "prefixcc"],
}


def load_context_from_source(context: CONTEXT) -> Context:
    """
    Loads a context from upstream source

    :param context:
    :return:
    """
    if context in CONTEXTS:
        return CONTEXTS[context]()
    elif context in COMBINED:
        ctxt = Context(context)
        for v in COMBINED[context]:
            ctxt.combine(load_context_from_source(v))
        return ctxt
    else:
        raise ValueError(f"No such context: {context}")


def run_etl(output_directory: Union[str, Path]):
    # contexts = load_contexts_meta()
    if not isinstance(output_directory, Path):
        output_directory = Path(output_directory)
    output_directory.mkdir(exist_ok=True, parents=True)
    cmap = {}
    for k, f in CONTEXTS.items():
        ctxt = f()
        cmap[k] = ctxt
    for k, vs in COMBINED.items():
        ctxt = Context(k)
        cmap[k] = ctxt
        for v in vs:
            ctxt.combine(cmap[v])
    for k, ctxt in cmap.items():
        with open(str(output_directory / f"{k}.csv"), "w", encoding="UTF-8") as file:
            context_to_file(ctxt, file)


@click.command
@click.option(
    "-d",
    "--output-directory",
    required=True,
    help="Path to directory where CSVs are stored",
)
def cli(output_directory):
    run_etl(output_directory)


if __name__ == "__main__":
    cli()
