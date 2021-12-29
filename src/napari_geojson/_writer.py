"""A module to write geojson files from napari shapes layers."""

from typing import Dict, List, Union

import geojson
from geojson.feature import FeatureCollection
from geojson.geometry import GeometryCollection, LineString, Polygon
from napari_plugin_engine import napari_hook_implementation


@napari_hook_implementation
def napari_get_writer(path, layer_types):
    """Return a writer for the given file extension."""
    if not path.lower().endswith((".json", ".geojson")):
        return None
    return napari_write_shapes


@napari_hook_implementation
def napari_write_shapes(path: str, data: List, meta: Dict) -> str:
    """Write a geojson file from napari shape layer data."""
    with open(path, "w") as fp:
        geojson.dump(napari_to_geojson(data, meta), fp)
        return fp.name


def napari_to_geojson(data: List, meta: Dict) -> FeatureCollection:
    """Create a geojson feature collection from a napari shapes layer."""
    return GeometryCollection(
        [
            get_geometry(s.tolist(), t) for s, t in zip(data, meta["shape_type"])  # noqa E501
        ]
    )


def get_geometry(coords: List, shape_type: str) -> Union[Polygon, LineString]:
    """Get GeoJSON type geometry from napari shape."""
    if shape_type == "ellipse":
        return ellipse_to_polygon(coords)
    if shape_type in ["rectangle", "polygon"]:
        return Polygon(coords)
    if shape_type in ["line", "path"]:
        return LineString(coords)
    raise ValueError(f"Shape type `{shape_type}` not supported.")


def ellipse_to_polygon(coords: List) -> Polygon:
    """Convert an ellipse to a polygon."""
    raise NotImplementedError("Ellipses are not yet supported")
