from importlib import metadata
from .io.parser import load_context

__all__ = [
    "load_context",
]
__version__ = metadata.version(__name__)

