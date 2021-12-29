import geojson
import pytest

from napari_geojson import napari_get_writer

ellipse = [[[0, 0], [0, 5], [5, 5], [5, 0]], "ellipse", "Polygon"]
line = [[[0, 0], [5, 5]], "line", "LineString"]
polygon = [[[0, 0], [5, 5], [0, 10]], "polygon", "Polygon"]
polyline = [[[0, 0], [5, 5], [0, 10]], "path", "LineString"]
rectangle = [[[0, 0], [0, 5], [5, 5], [5, 0]], "rectangle", "Polygon"]

# sample_shapes = [ellipse, line, polygon, polyline, rectangle]
# sample_shapes_ids = ["ellipse", "line", "polygon", "polyline", "rectangle"]

sample_shapes = [line, polygon, polyline, rectangle]
sample_shapes_ids = ["line", "polygon", "polyline", "rectangle"]


@pytest.mark.parametrize(
    "coords,shape_type,expected", sample_shapes, ids=sample_shapes_ids
)
def test_write_each_shape(make_napari_viewer, tmp_path, coords, shape_type, expected):  # noqa E501
    """Writer writes a shapes layer as GeoJSON."""
    fname = str(tmp_path / "sample.geojson")
    viewer = make_napari_viewer()
    shapes_layer = viewer.add_shapes(coords, shape_type=shape_type)
    # shape was written
    assert len(shapes_layer.data) == 1

    writer = napari_get_writer(fname, "shapes")
    assert callable(writer)

    data, meta, _ = shapes_layer.as_layer_data_tuple()
    writer(fname, data, meta)

    # read back
    with open(fname, "r") as fp:
        collection = geojson.load(fp)
        geom = collection["geometries"][0]
        assert geom.type == expected


@pytest.mark.parametrize(
    "coords,shape_type,expected", [ellipse], ids=["ellipse"]
)
def test_writer_raises_error(tmp_path, make_napari_viewer, coords, shape_type, expected):  # noqa E501
    """Writer raises an error when shapes layer contains ellipses."""
    fname = str(tmp_path / "sample.geojson")
    viewer = make_napari_viewer()
    shapes_layer = viewer.add_shapes(coords, shape_type=shape_type)
    # shape was written
    assert len(shapes_layer.data) == 1

    with pytest.raises(NotImplementedError):
        writer = napari_get_writer(fname, "shapes")
        data, meta, _ = shapes_layer.as_layer_data_tuple()
        writer(fname, data, meta)


def test_get_writer_pass():
    """Reader passes on fake file."""
    reader = napari_get_writer("fake.file", "shapes")
    assert reader is None
