from csv import DictWriter
from typing import TextIO

from prefixmaps.datamodel.context import Context, PrefixExpansion, StatusType

STATUS_TYPE_ORDER = {
    StatusType.canonical: 0,
    StatusType.prefix_alias: 1,
    StatusType.namespace_alias: 2,
    StatusType.multi_alias: 3,
}


def _key(pe: PrefixExpansion):
    return pe.prefix.casefold(), STATUS_TYPE_ORDER[pe.status]


def context_to_file(context: Context, file: TextIO) -> None:
    """
    Writes a context to a file

    :param context:
    :param file:
    :return:
    """
    writer = DictWriter(file, fieldnames=["context", "prefix", "namespace", "status"])
    writer.writeheader()
    for pe in sorted(context.prefix_expansions, key=_key):
        row = vars(pe)
        row["status"] = pe.status.value
        writer.writerow(row)
