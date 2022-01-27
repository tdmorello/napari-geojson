"""Read geojson files into napari."""

from collections import defaultdict
from typing import TYPE_CHECKING, Any, Dict, List, Tuple

import geojson
import numpy as np
from geojson.geometry import Geometry, LineString, Point, Polygon

if TYPE_CHECKING:
    import napari  # pragma: no cover


def napari_get_reader(path):
    """Get implementation of the napari_get_reader hook specification."""
    if isinstance(path, list):
        path = path[0]

    if not path.lower().endswith(".geojson"):
        return None

    return reader_function


def reader_function(path) -> List["napari.types.LayerDataTuple"]:
    """Take a path or list of paths and return a list of LayerData tuples."""
    # handle both a string and a list of strings
    paths = [path] if isinstance(path, str) else path
    return [geojson_to_napari(_path) for _path in paths]


# TODO if all objects are point, load into points layer?
def geojson_to_napari(fname: str) -> Tuple[Any, Dict, str]:
    """Convert geojson into napari shapes data."""
    with open(fname) as f:
        collection = geojson.load(f)

        try:
            if "features" in collection.keys():
                collection = collection["features"]
            elif "geometries" in collection.keys():
                collection = collection["geometries"]
        except AttributeError:
            # already a list?
            pass

        shapes = [get_shape(geom) for geom in collection]
        shape_types = [get_shape_type(geom) for geom in collection]
        properties = get_properties(collection)
        meta = {"shape_type": shape_types, "properties": properties}

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
    # QuPath stores 'type' under 'geometry'
    if geom.type == "Feature":
        geom_type = geom.geometry.type
    else:
        geom_type = geom.type

    if geom_type in ["Point", "Polygon"]:
        return "rectangle" if is_rectangle(geom) else "polygon"
    if geom_type == "LineString":
        return "path" if is_polyline(geom) else "line"
    else:
        raise ValueError(f"No matching napari shape for {geom_type}")


def is_rectangle(geom: Geometry) -> bool:
    """Check if a geometry is a rectangle."""
    # TODO automatically detect rectangular polygons
    if isinstance(geom, Polygon):
        ...
    return False


def is_polyline(geom: Geometry) -> bool:
    """Check if a geometry is a path/polyline."""
    return isinstance(geom, LineString) and (len(get_coords(geom)) > 2)


# alternatively, ignore points and print a message
def point_to_polygon(point: Point, width=1) -> Polygon:
    """Convert a point to a 1x1 square polygon."""
    coords = np.tile(np.array(get_coords(point)), (4, 1))
    coords[((0, 0, 1, 3), (0, 1, 0, 1))] -= width / 2
    coords[((1, 2, 2, 3), (1, 0, 1, 0))] += width / 2
    return Polygon(coords.tolist())


def estimate_ellipse(poly: Polygon) -> np.ndarray:
    """Fit an ellipse to the polygon."""
    raise NotImplementedError


# TODO extract color
def get_properties(collection) -> dict:
    """Return properties sorted into a dataframe-like dictionary."""
    properties = defaultdict(list)
    for geom in collection:
        for k, v in geom.properties.items():
            # handles QuPath measurement storage
            # TODO move to separate function
            if k == "measurements":
                for d in v:
                    try:
                        properties[d["name"]].append(d["value"])
                    except KeyError:
                        pass
            else:
                properties[k].append(v)
    return properties


# https://stackoverflow.com/questions/7822956/how-to-convert-negative-integer-value-to-hex-in-python
def int_to_hex(val: int, nbits=32):
    """Convert signed integers to 32 bit hex."""
    return hex((val + (1 << nbits)) % (1 << nbits))
