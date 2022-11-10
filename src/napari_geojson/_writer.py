"""A module to write geojson files from napari shapes layers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Sequence, Tuple, Union

import geojson
from geojson.geometry import LineString, MultiPoint, Polygon
from napari.layers.shapes._shapes_models import Ellipse

if TYPE_CHECKING:
    DataType = Union[Any, Sequence[Any]]
    FullLayerData = Tuple[DataType, dict, str]


def write_shapes(path: str, layer_data: List[Tuple[Any, Dict, str]]) -> str:
    """Write a single geojson file from napari shape layer data."""
    with open(path, "w") as fp:
        shapes = []
        for layer in layer_data:
            data, meta, kind = layer
            if kind == "points":
                shapes.append(MultiPoint([list(p) for p in data]))
            else:
                shapes.extend(
                    [
                        get_geometry(s.tolist(), t)
                        for s, t in zip(data, meta["shape_type"])  # noqa E501
                    ]
                )

        # convert shapes into QuPath friendly format
        shapes = [format_qupath(s) for s in shapes]

        geojson.dump(shapes, fp)
        return fp.name


def format_qupath(shape, object_type="annotation", is_locked=False):
    """Convert to QuPath friendly object format."""
    shape = {
        "type": "Feature",
        "geometry": shape,
        "properties": {"object_type": object_type, "isLocked": is_locked},
    }
    if shape["geometry"]["type"] == "Polygon":
        shape["geometry"]["coordinates"] = [shape["geometry"]["coordinates"]]
    return shape


def get_geometry(coords: List, shape_type: str) -> Union[Polygon, LineString]:
    """Get GeoJSON type geometry from napari shape."""
    if shape_type == "ellipse":
        return Polygon(ellipse_to_polygon(coords))
    if shape_type in ["rectangle", "polygon"]:
        return Polygon(coords)
    if shape_type in ["line", "path"]:
        return LineString(coords)
    raise ValueError(f"Shape type `{shape_type}` not supported.")


def get_points(coords: List) -> MultiPoint:
    """Get GeoJSON MultiPoints from napari points layer."""
    ...


def ellipse_to_polygon(coords: List) -> List:
    """Convert an ellipse to a polygon."""
    # TODO implement custom function
    # Hacky way to use napari's internal conversion
    return Ellipse(coords)._edge_vertices.tolist()
