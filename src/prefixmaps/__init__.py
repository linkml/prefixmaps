from importlib import metadata
from .io.parser import load_context

try:
    from importlib.metadata import version
except ImportError:  # for Python<3.8
    from importlib_metadata import version
    
__all__ = [
    "load_context",
]
__version__ = version(__name__)