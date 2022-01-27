"""A module to write geojson files from napari shapes layers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Sequence, Tuple, Union

import geojson
from geojson.feature import FeatureCollection
from geojson.geometry import GeometryCollection, LineString, Polygon
from napari.layers.shapes._shapes_models import Ellipse

if TYPE_CHECKING:
    DataType = Union[Any, Sequence[Any]]
    FullLayerData = Tuple[DataType, dict, str]


def write_shapes(path: str, data: Any, meta: dict) -> str:
    """Write a single geojson file from napari shape layer data."""
    with open(path, "w") as fp:
        geojson.dump(napari_to_geojson(data, meta), fp)
        return fp.name


def napari_to_geojson(data: List, meta: Dict) -> FeatureCollection:
    """Create a geojson feature collection from a napari shapes layer."""
    return GeometryCollection(
        [
            get_geometry(s.tolist(), t)
            for s, t in zip(data, meta["shape_type"])  # noqa E501
        ]
    )


def get_geometry(coords: List, shape_type: str) -> Union[Polygon, LineString]:
    """Get GeoJSON type geometry from napari shape."""
    if shape_type == "ellipse":
        return Polygon(ellipse_to_polygon(coords))
    if shape_type in ["rectangle", "polygon"]:
        return Polygon(coords)
    if shape_type in ["line", "path"]:
        return LineString(coords)
    raise ValueError(f"Shape type `{shape_type}` not supported.")


def ellipse_to_polygon(coords: List) -> List:
    """Convert an ellipse to a polygon."""
    # Hacky way to use napari's internal conversion
    return Ellipse(coords)._edge_vertices.tolist()
