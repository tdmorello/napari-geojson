"""Test plugins."""

import geopandas as gpd
import geopandas.testing
from shapely.geometry import LineString, Polygon

from napari_geojson import napari_get_reader


# tmp_path is a pytest fixture
def test_reader(tmp_path):
    """An example of how you might test your plugin."""
    # write some fake data using your supported file format
    my_test_file = str(tmp_path / "myfile.geojson")

    # include other data types, Point, Line, ...
    shapes = [
        Polygon([(0, 0), (1, 0), (0.5, 1), (0, 0)]),
        Polygon([(0, 2), (1, 2), (1, 3), (0, 3), (0, 2)]),
        LineString([(0, 2), (1, 2), (1, 3), (0, 3)]),
    ]
    gdf = gpd.GeoDataFrame({"geometry": shapes})
    gdf.to_file(my_test_file)

    # try to read it back in
    reader = napari_get_reader(my_test_file)
    assert callable(reader)

    # make sure we're delivering the right format
    layer_data_list = reader(my_test_file)
    assert isinstance(layer_data_list, list) and len(layer_data_list) > 0
    layer_data_tuple = layer_data_list[0]
    assert isinstance(layer_data_tuple, tuple) and len(layer_data_tuple) > 0

    data = layer_data_tuple[0]
    shape_types = layer_data_tuple[1]["shape_type"]
    shape_type_conversion = {"polygon": Polygon, "path": LineString}

    # make sure it's the same as it started
    test_gdf = gpd.GeoDataFrame(
        {
            "geometry": [
                shape_type_conversion[shape_type](coords)
                for coords, shape_type in zip(data, shape_types)
            ]
        }
    )
    geopandas.testing.assert_geodataframe_equal(gdf, test_gdf)


def test_get_reader_pass():
    """Reader passes on fake file."""
    reader = napari_get_reader("fake.file")
    assert reader is None
