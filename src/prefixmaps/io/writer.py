from csv import DictWriter
from typing import TextIO

from prefixmaps.datamodel.context import Context


def context_to_file(context: Context, file: TextIO) -> None:
    """
    Writes a context to a file

    :param context:
    :param file:
    :return:
    """
    writer = DictWriter(file, fieldnames=["context", "prefix", "namespace", "status"])
    writer.writeheader()
    for pe in context.prefix_expansions:
        row = vars(pe)
        row["status"] = pe.status.value
        writer.writerow(row)
