from pathlib import Path
from typing import Union

import click

from prefixmaps.datamodel.context import Context
from prefixmaps.etl.ingest_bioregistry import (from_bioregistry,
                                               from_bioregistry_upper)
from prefixmaps.etl.ingest_go import parse_go_xrefs_from_remote
from prefixmaps.etl.ingest_jsonld import from_prefixcc
from prefixmaps.etl.ingest_shacl import from_obo
from prefixmaps.io.writer import context_to_file

CONTEXTS = {
    "obo": from_obo,
    "go": parse_go_xrefs_from_remote,
    "bioregistry.upper": from_bioregistry_upper,
    "bioregistry": from_bioregistry,
    "prefixcc": from_prefixcc,
}
COMBINED = {"merged": ["obo", "bioregistry.upper", "prefixcc"]}


def run_etl(output_directory: Union[str, Path]):
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
