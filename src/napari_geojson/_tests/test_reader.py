"""Test plugins."""

import geojson
import pytest
from geojson import FeatureCollection, GeometryCollection

from napari_geojson import napari_get_reader


@pytest.mark.parametrize(
    "collection_class",
    [FeatureCollection, GeometryCollection],
    ids=["features", "geometries"],
)
def test_read_collections(tmp_path, collection_class):
    """Reader loads the correct number of shapes."""
    fname = str(tmp_path / "sample.geojson")

    with open(fname, "w") as f:
        geojson_types = ["Point", "LineString", "Polygon"]
        feature_collection = collection_class(
            [geojson.utils.generate_random(_type) for _type in geojson_types]
        )
        geojson.dump(feature_collection, f)

    # try to read it back in
    reader = napari_get_reader(fname)
    assert callable(reader)

    # make sure we're delivering the right format
    layer_data_list = reader(fname)
    assert isinstance(layer_data_list, list) and len(layer_data_list) > 0
    layer_data_tuple = layer_data_list[0]
    assert isinstance(layer_data_tuple, tuple) and len(layer_data_tuple) > 0

    # make sure there are the proper number of shapes in the layer
    assert len(layer_data_tuple[0]) == len(geojson_types)


def test_get_reader_pass():
    """Reader passes on fake file."""
    reader = napari_get_reader("fake.file")
    assert reader is None
