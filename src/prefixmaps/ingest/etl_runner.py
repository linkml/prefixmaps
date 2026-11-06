"""ETL logic for retrieving and normalizing upstream contexts."""

from pathlib import Path
from typing import Callable, Dict, Mapping, Union

import click

from prefixmaps.data import data_path
from prefixmaps.datamodel.context import CONTEXT, Context
from prefixmaps.ingest.ingest_bioportal import from_bioportal_file
from prefixmaps.ingest.ingest_bioregistry import (
    from_bioregistry,
    from_bioregistry_upper,
)
from prefixmaps.ingest.ingest_go import parse_go_xrefs_from_remote
from prefixmaps.ingest.ingest_jsonld import from_prefixcc, from_prefixcc_snapshot
from prefixmaps.ingest.ingest_linkml import from_semweb_curated
from prefixmaps.ingest.ingest_shacl import from_obo
from prefixmaps.ingest.ingest_w3id import from_w3id
from prefixmaps.io.writer import context_to_file

# TODO: replace this with introspection from metadata file
CONTEXTS: Mapping[str, Callable[[], Context]] = {
    "obo": from_obo,
    "go": parse_go_xrefs_from_remote,
    "linked_data": from_semweb_curated,
    "bioportal": from_bioportal_file,
    "bioregistry.upper": from_bioregistry_upper,
    "bioregistry": from_bioregistry,
    "prefixcc": from_prefixcc_snapshot,
    "w3id": from_w3id,
}
"""Maps the name of a context to the python function that can generate it.

prefix.cc is frozen, see https://github.com/linkml/prefixmaps/issues/61. Pass
``refresh_prefixcc=True`` to :func:`run_etl` to download it again."""

COMBINED = {
    "merged": ["obo", "go", "linked_data", "bioregistry.upper", "prefixcc"],
    "merged.monarch": ["obo", "go", "linked_data", "bioregistry.upper", "prefixcc"],
    "merged.oak": ["obo", "go", "linked_data", "bioregistry.upper", "prefixcc"],
}
"""Contexts that remix other contexts. Order is significant, with the first listed having highest precedence."""


def load_context_from_source(context: CONTEXT) -> Context:
    """
    Loads a context from upstream source.

    The context name should be a handle for either:

    - An atomic context (e.g. obo, linked_data)
    - A conbined context (which remixes existing contexts)

    prefix.cc is the exception: it comes from the bundled snapshot, see :data:`CONTEXTS`.

    :param context: unique handle of the context
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


def run_etl(output_directory: Union[str, Path], refresh_prefixcc: bool = False) -> None:
    """
    Runs the complete ETL pipeline.

    All contexts except prefix.cc are refreshed from upstream sources, and written to the
    output directory, as CSV.

    :param output_directory:
    :param refresh_prefixcc: if True, also download prefix.cc and print what changed.
        prefix.cc has no curation, so review those changes before committing them.
    :return:
    """
    # contexts = load_contexts_meta()
    output_directory = Path(output_directory).resolve()
    output_directory.mkdir(exist_ok=True, parents=True)

    # Load all individual contexts
    contexts: Dict[str, Context] = {
        name: context_getter() for name, context_getter in CONTEXTS.items()
    }
    if refresh_prefixcc:
        snapshot = contexts["prefixcc"]
        contexts["prefixcc"] = from_prefixcc()
        echo_changes(snapshot, contexts["prefixcc"])

    # Create merged contexts
    for merged_name, names in COMBINED.items():
        context = Context(name=merged_name)
        contexts[merged_name] = context
        for name in names:
            context.combine(contexts[name])

    # Write all contexts
    for name, context in contexts.items():
        with output_directory.joinpath(f"{name}.csv").open("w", encoding="UTF-8") as file:
            context_to_file(context, file, include_expansion_source=context.name in COMBINED)


def echo_changes(old: Context, new: Context) -> None:
    """
    Prints the prefix expansions that were added (+) or removed (-) between two versions of a
    context. Changes that this causes in merged contexts only show up in their CSV diffs.

    :param old:
    :param new:
    :return:
    """
    old_rows = {(pe.prefix, pe.namespace, pe.status.value) for pe in old.prefix_expansions}
    new_rows = {(pe.prefix, pe.namespace, pe.status.value) for pe in new.prefix_expansions}
    for row in sorted(old_rows ^ new_rows, key=lambda row: (row[0].casefold(), row)):
        click.echo(f"{'+' if row in new_rows else '-'} {new.name} {' '.join(row)}")


@click.command
@click.option(
    "-d",
    "--output-directory",
    default=data_path,
    type=Path,
    help="Path to directory where CSVs are stored",
)
@click.option(
    "--refresh-prefixcc",
    is_flag=True,
    help="Also download prefix.cc, which is uncurated, and print what changed for review",
)
def cli(output_directory, refresh_prefixcc):
    run_etl(output_directory, refresh_prefixcc=refresh_prefixcc)


if __name__ == "__main__":
    cli()
