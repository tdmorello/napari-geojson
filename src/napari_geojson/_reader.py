"""
This module is an example of a barebones numpy reader plugin for napari.

It implements the ``napari_get_reader`` hook specification, (to create
a reader plugin) but your plugin may choose to implement any of the hook
specifications offered by napari.
see: https://napari.org/docs/dev/plugins/hook_specifications.html

Replace code below accordingly.  For complete documentation see:
https://napari.org/docs/dev/plugins/for_plugin_developers.html
"""

from typing import TYPE_CHECKING, List

import geojson
import numpy as np
from geojson.geometry import Geometry, Polygon
from napari_plugin_engine import napari_hook_implementation

if TYPE_CHECKING:
    import napari


@napari_hook_implementation
def napari_get_reader(path):
    """Get a basic implementation of the napari_get_reader hook specification.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    function or None
        If the path is a recognized format, return a function that accepts the
        same path or list of paths, and returns a list of layer data tuples.
    """
    if isinstance(path, list):
        # reader plugins may be handed single path, or a list of paths.
        # if it is a list, it is assumed to be an image stack...
        # so we are only going to look at the first file.
        path = path[0]

    # if we know we cannot read the file, we immediately return None.
    if not path.lower().endswith((".json", ".geojson")):
        return None

    # otherwise we return the *function* that can read ``path``.
    return reader_function


def reader_function(path) -> List["napari.types.LayerDataTuple"]:
    """Take a path or list of paths and return a list of LayerData tuples.

    Readers are expected to return data as a list of tuples, where each tuple
    is (data, [add_kwargs, [layer_type]]), "add_kwargs" and "layer_type" are
    both optional.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    layer_data : list of tuples
        A list of LayerData tuples where each tuple in the list contains
        (data, metadata, layer_type), where data is a numpy array, metadata is
        a dict of keyword arguments for the corresponding viewer.add_* method
        in napari, and layer_type is a lower-case string naming the type of layer.  # noqa
        Both "meta", and "layer_type" are optional. napari will default to
        layer_type=="image" if not provided
    """
    # handle both a string and a list of strings
    paths = [path] if isinstance(path, str) else path
    return [geojson_to_napari(_path) for _path in paths]


# consider accepting string input instead of file
def geojson_to_napari(fname: str) -> "napari.types.LayerDataTuple":
    """Convert geojson into napari shapes data."""
    # napari shape types {‘line’, ‘rectangle’, ‘ellipse’, ‘path’, ‘polygon’}
    with open(fname, "r") as f:
        # load data
        collection = geojson.load(f)
        if "features" in collection.keys():
            collection = collection["features"]
        elif "geometries" in collection.keys():
            collection = collection["geometries"]
        # collect shape data
        shapes = [get_coords(geom) for geom in collection]
        shape_types = [get_shape_type(geom) for geom in collection]
        # TODO if all objects are point, load into points layer
        meta = {"shape_type": shape_types}
    return (shapes, meta, "shapes")


def get_coords(geom) -> List:
    """Return coordinates for geojson object."""
    return list(geojson.utils.coords(geom))


# TODO how to handle points?
def get_shape_type(geom: Geometry) -> str:
    """Convert geojson object type to napari shape type.

    :param geom: a geojson geometry
    :type geom: geojson.geometry.Geometry
    :return: "point", "rectangle", "polygon", "path", or "line"
    :rtype: str
    """
    if geom.type == "Point":
        return "point"
    if geom.type == "Polygon":
        return "rectangle" if is_rectangle(geom) else "polygon"
    if geom.type == "LineString":
        return "path" if is_polyline(geom) else "line"
    else:
        raise ValueError(f"No matching napari shape for {geom.type}")


def is_rectangle(geometry: Geometry) -> bool:
    """Check if a geometry is a rectangle."""
    # TODO fill in
    return False


def is_polyline(geometry: Geometry):
    """Check if a geometry is a path/polyline."""
    return (geometry.type == "LineString") and (len(get_coords(geometry)) > 2)


def estimate_ellipse(polygon: Polygon) -> np.ndarray:
    """Fit an ellipse to the polygon."""
    ...
