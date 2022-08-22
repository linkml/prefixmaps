from prefixmaps.datamodel.context import Context
from prefixmaps.io.parser import context_path
from prefixmaps.io.writer import context_to_file


def xxxsave_context(context: Context) -> None:
    """
    Saves a Context object in the standard place

    :param context:
    :return:
    """
    with open(context_path(context.name), "w", encoding="utf-8") as file:
        context_to_file(context, file)
