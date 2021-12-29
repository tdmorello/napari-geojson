"""GeoJSON reader and writer packages for napari."""
try:
    from ._version import version as __version__
except ImportError:  # pragma: no cover
    __version__ = "unknown"


from ._reader import napari_get_reader  # noqa F401
from ._writer import napari_get_writer, napari_write_shapes  # noqa F401
