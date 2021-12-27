"""
This module is an example of a barebones numpy reader plugin for napari.

It implements the ``napari_get_reader`` hook specification, (to create
a reader plugin) but your plugin may choose to implement any of the hook
specifications offered by napari.
see: https://napari.org/docs/dev/plugins/hook_specifications.html

Replace code below accordingly.  For complete documentation see:
https://napari.org/docs/dev/plugins/for_plugin_developers.html
"""

from typing import List, Tuple

import geopandas as gpd
import numpy as np
from napari_plugin_engine import napari_hook_implementation


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


def reader_function(path):
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
    # load all files into array
    gdfs = [gpd.read_file(_path) for _path in paths]

    layer_tuples = []
    for gdf in gdfs:
        coords, shape_types = _gdf_to_napari(gdf)
        add_kwargs = {"shape_type": shape_types}
        layer_tuples.append((coords, add_kwargs, "shapes"))

    return layer_tuples


# napari Shapes supports:
# ellipses, rectangles, polygons, lines, polylines


def _get_coords(shape) -> Tuple[np.ndarray, str]:
    # if polygon, check if rectangle
    shape_type_conversion = {"Polygon": "polygon", "LineString": "path"}
    shape_type = shape_type_conversion[shape.geom_type]
    try:
        coords = np.array(shape.boundary.xy).T
        if np.isclose(shape.minimum_rotated_rectangle.area, shape.area):
            shape_type = "rectangle"
    except NotImplementedError:
        if shape_type == "ellipse":
            raise NotImplementedError
        elif shape_type == "line":
            raise NotImplementedError
        elif shape_type == "path":
            coords = np.array(shape.coords)

    return (coords, shape_type)


def _gdf_to_napari(gdf) -> Tuple[List[np.ndarray], List[str]]:
    shapes = gdf.geometry.apply(_get_coords)
    coords = [coord for coord, _ in shapes]
    shape_types = [shape_type for _, shape_type in shapes]
    return coords, shape_types
