try:
    from importlib.metadata import version
except ImportError:  # for Python<3.8
    from importlib_metadata import version

__version__ = version(__name__)
