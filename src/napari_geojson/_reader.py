"""Read geojson files into napari."""

from typing import TYPE_CHECKING, Any, Dict, List, Tuple

import geojson
import numpy as np
from geojson.geometry import Geometry, LineString, Point, Polygon
from napari_plugin_engine import napari_hook_implementation

if TYPE_CHECKING:
    import napari  # pragma: no cover


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
        path = path[0]

    if not path.lower().endswith((".json", ".geojson")):
        return None

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


# TODO if all objects are point, load into points layer?
def geojson_to_napari(fname: str) -> Tuple[Any, Dict, str]:
    """Convert geojson into napari shapes data."""
    # consider accepting string input instead of file
    with open(fname, "r") as f:
        collection = geojson.load(f)

        if "features" in collection.keys():
            collection = collection["features"]
        elif "geometries" in collection.keys():
            collection = collection["geometries"]

        shapes = [get_shape(geom) for geom in collection]
        shape_types = [get_shape_type(geom) for geom in collection]
        meta = {"shape_type": shape_types}

    return (shapes, meta, "shapes")


def get_shape(geom: Geometry, convert_point=True) -> List:
    """Return coordinates of shapes.

    Gives the option to convert points to square polygons.
    """
    if convert_point and isinstance(geom, Point):
        geom = point_to_polygon(geom)
    return get_coords(geom)


def get_coords(geom: Geometry) -> List:
    """Return coordinates for geojson shapes."""
    return list(geojson.utils.coords(geom))


def get_shape_type(geom: Geometry) -> str:
    """Translate geojson to napari shape notation."""
    if geom.type in ["Point", "Polygon"]:
        return "rectangle" if is_rectangle(geom) else "polygon"
    if geom.type == "LineString":
        return "path" if is_polyline(geom) else "line"
    else:
        raise ValueError(f"No matching napari shape for {geom.type}")


def is_rectangle(geom: Geometry) -> bool:
    """Check if a geometry is a rectangle."""
    # TODO fill in
    if isinstance(geom, Polygon):
        ...
    return False


def is_polyline(geom: Geometry) -> bool:
    """Check if a geometry is a path/polyline."""
    return isinstance(geom, LineString) and (len(get_coords(geom)) > 2)


def point_to_polygon(point: Point, width=1) -> Polygon:
    """Convert a point to a 1x1 square polygon."""
    coords = np.tile(np.array(get_coords(point)), (4, 1))
    coords[((0, 0, 1, 3), (0, 1, 0, 1))] -= width / 2
    coords[((1, 2, 2, 3), (1, 0, 1, 0))] += width / 2
    return Polygon(coords.tolist())


def estimate_ellipse(poly: Polygon) -> np.ndarray:
    """Fit an ellipse to the polygon."""
    raise NotImplementedError
