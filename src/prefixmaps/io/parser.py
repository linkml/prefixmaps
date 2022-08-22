from csv import DictReader
from pathlib import Path
from typing import List, TextIO

from prefixmaps.data import data_path
from prefixmaps.datamodel.context import (CONTEXT, Context, PrefixExpansion,
                                          StatusType)


def context_path(name: CONTEXT) -> Path:
    """
    Get the path in which the context datafile lives

    :param name:
    :return:
    """
    return data_path / f"{name}.csv"


def load_contexts(names: List[CONTEXT]) -> Context:
    """
    Merges multiple contexts

    :param names:
    :return:
    """
    name = "+".join(names)
    ctxt = Context(name)
    for n in names:
        ctxt.combine(load_context(n))
    return ctxt


def load_context(name: CONTEXT) -> Context:
    """
    Loads a context by name from standard location

    :param name:
    :return:
    """
    with open(data_path / f"{name}.csv", encoding="utf-8") as file:
        return context_from_file(name, file)


def context_from_file(name: CONTEXT, file: TextIO) -> Context:
    """
    Loads a context from a file

    :param name:
    :param file:
    :return:
    """
    reader = DictReader(file)
    context = Context(name=name)
    for row in reader:
        row["status"] = StatusType[row["status"]]
        pe = PrefixExpansion(**row)
        context.prefix_expansions.append(pe)
    return context
