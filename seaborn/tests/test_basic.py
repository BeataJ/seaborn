from __future__ import division
from itertools import product
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import pytest
from .. import basic
from ..palettes import color_palette
from ..utils import categorical_order


class TestBasicPlotter(object):

    @pytest.fixture
    def wide_df(self):

        columns = list("abc")
        index = pd.Int64Index(np.arange(10, 50, 2), name="wide_index")
        values = np.random.randn(len(index), len(columns))
        return pd.DataFrame(values, index=index, columns=columns)

    @pytest.fixture
    def wide_array(self):

        return np.random.randn(20, 3)

    @pytest.fixture
    def flat_array(self):

        return np.random.randn(20)

    @pytest.fixture
    def flat_series(self):

        index = pd.Int64Index(np.arange(10, 30), name="t")
        return pd.Series(np.random.randn(20), index, name="s")

    @pytest.fixture
    def wide_list(self):

        return [np.random.randn(20), np.random.randn(10)]

    @pytest.fixture
    def wide_list_of_series(self):

        return [pd.Series(np.random.randn(20), np.arange(20), name="a"),
                pd.Series(np.random.randn(10), np.arange(5, 15), name="b")]

    @pytest.fixture
    def long_df(self):

        n = 100
        rs = np.random.RandomState()
        return pd.DataFrame(dict(
            x=rs.randint(0, 20, n),
            y=rs.randn(n),
            a=np.take(list("abc"), rs.randint(0, 3, n)),
            b=np.take(list("mnop"), rs.randint(0, 4, n)),
            s=np.take([2, 4, 8], rs.randint(0, 3, n)),
        ))

    @pytest.fixture
    def null_column(self):

        return pd.Series(index=np.arange(20))

    def test_wide_df_variables(self, wide_df):

        p = basic._BasicPlotter()
        p.establish_variables(data=wide_df)
        assert p.input_format == "wide"
        assert len(p.plot_data) == np.product(wide_df.shape)

        x = p.plot_data["x"]
        expected_x = np.tile(wide_df.index, wide_df.shape[1])
        assert np.array_equal(x, expected_x)

        y = p.plot_data["y"]
        expected_y = wide_df.values.ravel(order="f")
        assert np.array_equal(y, expected_y)

        hue = p.plot_data["hue"]
        expected_hue = np.repeat(wide_df.columns.values, wide_df.shape[0])
        assert np.array_equal(hue, expected_hue)

        style = p.plot_data["style"]
        expected_style = expected_hue
        assert np.array_equal(style, expected_style)

        assert p.plot_data["size"].isnull().all()

        assert p.x_label == wide_df.index.name
        assert p.y_label is None
        assert p.hue_label == wide_df.columns.name
        assert p.size_label is None
        assert p.style_label == wide_df.columns.name

    def test_wide_df_variables_check(self, wide_df):

        p = basic._BasicPlotter()
        wide_df = wide_df.copy()
        wide_df.loc[:, "not_numeric"] = "a"
        with pytest.raises(ValueError):
            p.establish_variables(data=wide_df)

    def test_wide_array_variables(self, wide_array):

        p = basic._BasicPlotter()
        p.establish_variables(data=wide_array)
        assert p.input_format == "wide"
        assert len(p.plot_data) == np.product(wide_array.shape)

        nrow, ncol = wide_array.shape

        x = p.plot_data["x"]
        expected_x = np.tile(np.arange(nrow), ncol)
        assert np.array_equal(x, expected_x)

        y = p.plot_data["y"]
        expected_y = wide_array.ravel(order="f")
        assert np.array_equal(y, expected_y)

        hue = p.plot_data["hue"]
        expected_hue = np.repeat(np.arange(ncol), nrow)
        assert np.array_equal(hue, expected_hue)

        style = p.plot_data["style"]
        expected_style = expected_hue
        assert np.array_equal(style, expected_style)

        assert p.plot_data["size"].isnull().all()

        assert p.x_label is None
        assert p.y_label is None
        assert p.hue_label is None
        assert p.size_label is None
        assert p.style_label is None

    def test_flat_array_variables(self, flat_array):

        p = basic._BasicPlotter()
        p.establish_variables(data=flat_array)
        assert p.input_format == "wide"
        assert len(p.plot_data) == np.product(flat_array.shape)

        x = p.plot_data["x"]
        expected_x = np.arange(flat_array.shape[0])
        assert np.array_equal(x, expected_x)

        y = p.plot_data["y"]
        expected_y = flat_array
        assert np.array_equal(y, expected_y)

        assert p.plot_data["hue"].isnull().all()
        assert p.plot_data["style"].isnull().all()
        assert p.plot_data["size"].isnull().all()

        assert p.x_label is None
        assert p.y_label is None
        assert p.hue_label is None
        assert p.size_label is None
        assert p.style_label is None

    def test_flat_series_variables(self, flat_series):

        p = basic._BasicPlotter()
        p.establish_variables(data=flat_series)
        assert p.input_format == "wide"
        assert len(p.plot_data) == len(flat_series)

        x = p.plot_data["x"]
        expected_x = flat_series.index
        assert np.array_equal(x, expected_x)

        y = p.plot_data["y"]
        expected_y = flat_series
        assert np.array_equal(y, expected_y)

        assert p.x_label is None
        assert p.y_label is None
        assert p.hue_label is None
        assert p.size_label is None
        assert p.style_label is None

    def test_wide_list_variables(self, wide_list):

        p = basic._BasicPlotter()
        p.establish_variables(data=wide_list)
        assert p.input_format == "wide"
        assert len(p.plot_data) == sum(len(l) for l in wide_list)

        x = p.plot_data["x"]
        expected_x = np.concatenate([np.arange(len(l)) for l in wide_list])
        assert np.array_equal(x, expected_x)

        y = p.plot_data["y"]
        expected_y = np.concatenate(wide_list)
        assert np.array_equal(y, expected_y)

        hue = p.plot_data["hue"]
        expected_hue = np.concatenate([
            np.ones_like(l) * i for i, l in enumerate(wide_list)
        ])
        assert np.array_equal(hue, expected_hue)

        style = p.plot_data["style"]
        expected_style = expected_hue
        assert np.array_equal(style, expected_style)

        assert p.plot_data["size"].isnull().all()

        assert p.x_label is None
        assert p.y_label is None
        assert p.hue_label is None
        assert p.size_label is None
        assert p.style_label is None

    def test_wide_list_of_series_variables(self, wide_list_of_series):

        p = basic._BasicPlotter()
        p.establish_variables(data=wide_list_of_series)
        assert p.input_format == "wide"
        assert len(p.plot_data) == sum(len(l) for l in wide_list_of_series)

        x = p.plot_data["x"]
        expected_x = np.concatenate([s.index for s in wide_list_of_series])
        assert np.array_equal(x, expected_x)

        y = p.plot_data["y"]
        expected_y = np.concatenate(wide_list_of_series)
        assert np.array_equal(y, expected_y)

        hue = p.plot_data["hue"]
        expected_hue = np.concatenate([
            np.full(len(s), s.name, object) for s in wide_list_of_series
        ])
        assert np.array_equal(hue, expected_hue)

        style = p.plot_data["style"]
        expected_style = expected_hue
        assert np.array_equal(style, expected_style)

        assert p.plot_data["size"].isnull().all()

        assert p.x_label is None
        assert p.y_label is None
        assert p.hue_label is None
        assert p.size_label is None
        assert p.style_label is None

    def test_long_df(self, long_df):

        p = basic._BasicPlotter()
        p.establish_variables(x="x", y="y", data=long_df)
        assert p.input_format == "long"

        assert np.array_equal(p.plot_data["x"], long_df["x"])
        assert np.array_equal(p.plot_data["y"], long_df["y"])
        for col in ["hue", "style", "size"]:
            assert p.plot_data[col].isnull().all()
        assert (p.x_label, p.y_label) == ("x", "y")
        assert p.hue_label is None
        assert p.size_label is None
        assert p.style_label is None

        p.establish_variables(x=long_df.x, y="y", data=long_df)
        assert np.array_equal(p.plot_data["x"], long_df["x"])
        assert np.array_equal(p.plot_data["y"], long_df["y"])
        assert (p.x_label, p.y_label) == ("x", "y")

        p.establish_variables(x="x", y=long_df.y, data=long_df)
        assert np.array_equal(p.plot_data["x"], long_df["x"])
        assert np.array_equal(p.plot_data["y"], long_df["y"])
        assert (p.x_label, p.y_label) == ("x", "y")

        p.establish_variables(x="x", y="y", hue="a", data=long_df)
        assert np.array_equal(p.plot_data["hue"], long_df["a"])
        for col in ["style", "size"]:
            assert p.plot_data[col].isnull().all()
        assert p.hue_label == "a"
        assert p.size_label is None and p.style_label is None

        p.establish_variables(x="x", y="y", hue="a", style="a", data=long_df)
        assert np.array_equal(p.plot_data["hue"], long_df["a"])
        assert np.array_equal(p.plot_data["style"], long_df["a"])
        assert p.plot_data["size"].isnull().all()
        assert p.hue_label == p.style_label == "a"
        assert p.size_label is None

        p.establish_variables(x="x", y="y", hue="a", style="b", data=long_df)
        assert np.array_equal(p.plot_data["hue"], long_df["a"])
        assert np.array_equal(p.plot_data["style"], long_df["b"])
        assert p.plot_data["size"].isnull().all()

        p.establish_variables(x="x", y="y", size="y", data=long_df)
        assert np.array_equal(p.plot_data["size"], long_df["y"])
        assert p.size_label == "y"
        assert p.hue_label is None and p.style_label is None

    def test_bad_input(self, long_df):

        p = basic._BasicPlotter()

        with pytest.raises(ValueError):
            p.establish_variables(x=long_df.x)

        with pytest.raises(ValueError):
            p.establish_variables(y=long_df.y)

        with pytest.raises(ValueError):
            p.establish_variables(x="not_in_df", data=long_df)

        with pytest.raises(ValueError):
            p.establish_variables(x="x", y="not_in_df", data=long_df)

        with pytest.raises(ValueError):
            p.establish_variables(x="x", y="not_in_df", data=long_df)

    def test_empty_input(self):

        p = basic._BasicPlotter()

        p.establish_variables(data=[])
        p.establish_variables(data=np.array([]))
        p.establish_variables(data=pd.DataFrame())
        p.establish_variables(x=[], y=[])


class TestLinePlotter(TestBasicPlotter):

    def test_parse_hue_null(self, wide_df, null_column):

        p = basic._LinePlotter(data=wide_df)
        p.parse_hue(null_column, "Blues", None, None)
        assert p.hue_levels == [None]
        assert p.palette == {}
        assert p.hue_type is None
        assert p.cmap is None

    def test_parse_hue_categorical(self, wide_df, long_df):

        p = basic._LinePlotter(data=wide_df)
        assert p.hue_levels == wide_df.columns.tolist()
        assert p.hue_type is "categorical"
        assert p.cmap is None

        # Test named palette
        palette = "Blues"
        expected_colors = color_palette(palette, wide_df.shape[1])
        expected_palette = dict(zip(wide_df.columns, expected_colors))
        p.parse_hue(p.plot_data.hue, palette, None, None)
        assert p.palette == expected_palette

        # Test list palette
        palette = color_palette("Reds", wide_df.shape[1])
        p.parse_hue(p.plot_data.hue, palette, None, None)
        expected_palette = dict(zip(wide_df.columns, palette))
        assert p.palette == expected_palette

        # Test dict palette
        colors = color_palette("Set1", 8)
        palette = dict(zip(wide_df.columns, colors))
        p.parse_hue(p.plot_data.hue, palette, None, None)
        assert p.palette == palette

        # Test dict with missing keys
        palette = dict(zip(wide_df.columns[:-1], colors))
        with pytest.raises(ValueError):
            p.parse_hue(p.plot_data.hue, palette, None, None)

        # Test list with wrong number of colors
        palette = colors[:-1]
        with pytest.raises(ValueError):
            p.parse_hue(p.plot_data.hue, palette, None, None)

        # Test hue order
        hue_order = ["a", "c", "d"]
        p.parse_hue(p.plot_data.hue, None, hue_order, None)
        assert p.hue_levels == hue_order

        # Test long data
        p = basic._LinePlotter(x="x", y="y", hue="a", data=long_df)
        assert p.hue_levels == categorical_order(long_df.a)
        assert p.hue_type is "categorical"
        assert p.cmap is None

        # Test default palette
        p.parse_hue(p.plot_data.hue, None, None, None)
        hue_levels = categorical_order(long_df.a)
        expected_colors = color_palette(n_colors=len(hue_levels))
        expected_palette = dict(zip(hue_levels, expected_colors))
        assert p.palette == expected_palette

        # Test default palette with many levels
        levels = pd.Series(list("abcdefghijklmnopqrstuvwxyz"))
        p.parse_hue(levels, None, None, None)
        expected_colors = color_palette("husl", n_colors=len(levels))
        expected_palette = dict(zip(levels, expected_colors))
        assert p.palette == expected_palette

    def test_parse_hue_numeric(self, long_df):

        p = basic._LinePlotter(x="x", y="y", hue="s", data=long_df)
        hue_levels = list(np.sort(long_df.s.unique()))
        assert p.hue_levels == hue_levels
        assert p.hue_type is "numeric"
        assert p.cmap is mpl.cm.get_cmap(mpl.rcParams["image.cmap"])

        # Test named colormap
        palette = "Purples"
        p.parse_hue(p.plot_data.hue, palette, None, None)
        assert p.cmap is mpl.cm.get_cmap(palette)

        # Test colormap object
        palette = mpl.cm.get_cmap("Greens")
        p.parse_hue(p.plot_data.hue, palette, None, None)
        assert p.cmap is palette

        # Test default hue limits
        p.parse_hue(p.plot_data.hue, None, None, None)
        assert p.hue_limits == (p.plot_data.hue.min(), p.plot_data.hue.max())

        # Test specified hue limits
        hue_limits = 1, 4
        p.parse_hue(p.plot_data.hue, None, None, hue_limits)
        assert p.hue_limits == hue_limits

        # Test default colormap values
        hmin, hmax = p.plot_data.hue.min(), p.plot_data.hue.max()
        p.parse_hue(p.plot_data.hue, None, None, None)
        assert p.palette[hmin] == pytest.approx(p.cmap(0.0))
        assert p.palette[hmax] == pytest.approx(p.cmap(1.0))

        # Test specified colormap values
        hue_limits = hmin - 1, hmax - 1
        p.parse_hue(p.plot_data.hue, None, None, hue_limits)
        norm_min = (hmin - hue_limits[0]) / (hue_limits[1] - hue_limits[0])
        assert p.palette[hmin] == pytest.approx(p.cmap(norm_min))
        assert p.palette[hmax] == pytest.approx(p.cmap(1.0))

        # Test list of colors
        hue_levels = list(np.sort(long_df.s.unique()))
        palette = color_palette("Blues", len(hue_levels))
        p.parse_hue(p.plot_data.hue, palette, None, None)
        assert p.palette == dict(zip(hue_levels, palette))

        palette = color_palette("Blues", len(hue_levels) + 1)
        with pytest.raises(ValueError):
            p.parse_hue(p.plot_data.hue, palette, None, None)

        # Test dictionary of colors
        palette = dict(zip(hue_levels, color_palette("Reds")))
        p.parse_hue(p.plot_data.hue, palette, None, None)
        assert p.palette == palette

        palette.pop(hue_levels[0])
        with pytest.raises(ValueError):
            p.parse_hue(p.plot_data.hue, palette, None, None)

        # Test invalid palette
        palette = "not_a_valid_palette"
        with pytest.raises(ValueError):
            p.parse_hue(p.plot_data.hue, palette, None, None)

    def test_parse_size(self, long_df):

        p = basic._LinePlotter(x="x", y="y", size="s", data=long_df)

        # Test default size limits and range
        default_linewidth = mpl.rcParams["lines.linewidth"]
        default_limits = p.plot_data["size"].min(), p.plot_data["size"].max()
        default_range = .5 * default_linewidth, 2 * default_linewidth
        p.parse_size(p.plot_data["size"], None, None, None)
        assert p.size_limits == default_limits
        size_range = min(p.sizes.values()), max(p.sizes.values())
        assert size_range == default_range

        # Test specified size limits
        size_limits = (1, 5)
        p.parse_size(p.plot_data["size"], None, None, size_limits)
        assert p.size_limits == size_limits

        # Test specified size range
        sizes = (.1, .5)
        p.parse_size(p.plot_data["size"], sizes, None, None)
        assert p.size_limits == default_limits

        # Test size values inferred from ranges
        sizes = (1, 5)
        size_limits = (1, 10)
        p.parse_size(p.plot_data["size"], sizes, None, size_limits)
        normalize = mpl.colors.Normalize(*size_limits, clip=False)
        for level, width in p.sizes.items():
            assert width == sizes[0] + (sizes[1] - sizes[0]) * normalize(level)

        # Test list of sizes
        var = "a"
        levels = categorical_order(long_df[var])
        sizes = list(np.random.rand(len(levels)))
        p = basic._LinePlotter(x="x", y="y", size=var, data=long_df)
        p.parse_size(p.plot_data["size"], sizes, None, None)
        assert p.sizes == dict(zip(levels, sizes))

        # Test dict of sizes
        var = "a"
        levels = categorical_order(long_df[var])
        sizes = dict(zip(levels, np.random.rand(len(levels))))
        p = basic._LinePlotter(x="x", y="y", size=var, data=long_df)
        p.parse_size(p.plot_data["size"], sizes, None, None)
        assert p.sizes == sizes

        # Test sizes list with wrong length
        sizes = list(np.random.rand(len(levels) + 1))
        with pytest.raises(ValueError):
            p.parse_size(p.plot_data["size"], sizes, None, None)

        # Test sizes dict with missing levels
        sizes = dict(zip(levels, np.random.rand(len(levels) - 1)))
        with pytest.raises(ValueError):
            p.parse_size(p.plot_data["size"], sizes, None, None)

        # Test bad sizes argument
        sizes = "bad_size"
        with pytest.raises(ValueError):
            p.parse_size(p.plot_data["size"], sizes, None, None)

    def test_parse_style(self, long_df):

        p = basic._LinePlotter(x="x", y="y", style="a", data=long_df)

        # Test defaults
        markers, dashes = True, True
        p.parse_style(p.plot_data["style"], markers, dashes, None)
        assert p.markers == dict(zip(p.style_levels, p.default_markers))
        assert p.dashes == dict(zip(p.style_levels, p.default_dashes))

        # Test lists
        markers, dashes = ["o", "s", "d"], [(1, 0), (1, 1), (2, 1, 3, 1)]
        p.parse_style(p.plot_data["style"], markers, dashes, None)
        assert p.markers == dict(zip(p.style_levels, markers))
        assert p.dashes == dict(zip(p.style_levels, dashes))

        # Test dicts
        markers = dict(zip(p.style_levels, markers))
        dashes = dict(zip(p.style_levels, dashes))
        p.parse_style(p.plot_data["style"], markers, dashes, None)
        assert p.markers == markers
        assert p.dashes == dashes

        # Test style order with defaults
        style_order = np.take(p.style_levels, [1, 2, 0])
        markers = dashes = True
        p.parse_style(p.plot_data["style"], markers, dashes, style_order)
        assert p.markers == dict(zip(style_order, p.default_markers))
        assert p.dashes == dict(zip(style_order, p.default_dashes))

        # Test too many levels with style lists
        markers, dashes = ["o", "s"], False
        with pytest.raises(ValueError):
            p.parse_style(p.plot_data["style"], markers, dashes, None)

        markers, dashes = False, [(2, 1)]
        with pytest.raises(ValueError):
            p.parse_style(p.plot_data["style"], markers, dashes, None)

        # Test too many levels with style dicts
        markers, dashes = {"a": "o", "b": "s"}, False
        with pytest.raises(ValueError):
            p.parse_style(p.plot_data["style"], markers, dashes, None)

        markers, dashes = False, {"a": (1, 0), "b": (2, 1)}
        with pytest.raises(ValueError):
            p.parse_style(p.plot_data["style"], markers, dashes, None)

    def test_subset_data_quantities(self, long_df):

        p = basic._LinePlotter(x="x", y="y", data=long_df)
        assert len(list(p.subset_data())) == 1

        # --

        var = "a"
        n_subsets = len(long_df[var].unique())

        p = basic._LinePlotter(x="x", y="y", hue=var, data=long_df)
        assert len(list(p.subset_data())) == n_subsets

        p = basic._LinePlotter(x="x", y="y", style=var, data=long_df)
        assert len(list(p.subset_data())) == n_subsets

        n_subsets = len(long_df[var].unique())

        p = basic._LinePlotter(x="x", y="y", size=var, data=long_df)
        assert len(list(p.subset_data())) == n_subsets

        # --

        var = "a"
        n_subsets = len(long_df[var].unique())

        p = basic._LinePlotter(x="x", y="y", hue=var, style=var, data=long_df)
        assert len(list(p.subset_data())) == n_subsets

        # --

        var1, var2 = "a", "s"
        n_subsets = len(set(list(map(tuple, long_df[[var1, var2]].values))))

        p = basic._LinePlotter(x="x", y="y", hue=var1, style=var2,
                               data=long_df)
        assert len(list(p.subset_data())) == n_subsets

        p = basic._LinePlotter(x="x", y="y", hue=var1, size=var2, style=var1,
                               data=long_df)
        assert len(list(p.subset_data())) == n_subsets

        # --

        var1, var2, var3 = "a", "s", "b"
        cols = [var1, var2, var3]
        n_subsets = len(set(list(map(tuple, long_df[cols].values))))

        p = basic._LinePlotter(x="x", y="y", hue=var1, size=var2, style=var3,
                               data=long_df)
        assert len(list(p.subset_data())) == n_subsets

    def test_subset_data_keys(self, long_df):

        p = basic._LinePlotter(x="x", y="y", data=long_df)
        for (hue, size, style), _ in p.subset_data():
            assert hue is None
            assert size is None
            assert style is None

        # --

        var = "a"

        p = basic._LinePlotter(x="x", y="y", hue=var, data=long_df)
        for (hue, size, style), _ in p.subset_data():
            assert hue in long_df[var].values
            assert size is None
            assert style is None

        p = basic._LinePlotter(x="x", y="y", style=var, data=long_df)
        for (hue, size, style), _ in p.subset_data():
            assert hue is None
            assert size is None
            assert style in long_df[var].values

        p = basic._LinePlotter(x="x", y="y", hue=var, style=var, data=long_df)
        for (hue, size, style), _ in p.subset_data():
            assert hue in long_df[var].values
            assert size is None
            assert style in long_df[var].values

        p = basic._LinePlotter(x="x", y="y", size=var, data=long_df)
        for (hue, size, style), _ in p.subset_data():
            assert hue is None
            assert size in long_df[var].values
            assert style is None

        # --

        var1, var2 = "a", "s"

        p = basic._LinePlotter(x="x", y="y", hue=var1, size=var2, data=long_df)
        for (hue, size, style), _ in p.subset_data():
            assert hue in long_df[var1].values
            assert size in long_df[var2].values
            assert style is None

    def test_subset_data_values(self, long_df):

        p = basic._LinePlotter(x="x", y="y", data=long_df)
        _, data = next(p.subset_data())
        expected = basic.sort_df(p.plot_data.loc[:, ["x", "y"]], ["x", "y"])
        assert np.array_equal(data.values, expected)

        p = basic._LinePlotter(x="x", y="y", data=long_df, sort=False)
        _, data = next(p.subset_data())
        expected = p.plot_data.loc[:, ["x", "y"]]
        assert np.array_equal(data.values, expected)

        p = basic._LinePlotter(x="x", y="y", hue="a", data=long_df)
        for (hue, _, _), data in p.subset_data():
            rows = p.plot_data["hue"] == hue
            cols = ["x", "y"]
            expected = basic.sort_df(p.plot_data.loc[rows, cols], cols)
            assert np.array_equal(data.values, expected.values)

        p = basic._LinePlotter(x="x", y="y", hue="a", data=long_df, sort=False)
        for (hue, _, _), data in p.subset_data():
            rows = p.plot_data["hue"] == hue
            cols = ["x", "y"]
            expected = p.plot_data.loc[rows, cols]
            assert np.array_equal(data.values, expected.values)

        p = basic._LinePlotter(x="x", y="y", hue="a", style="a", data=long_df)
        for (hue, _, _), data in p.subset_data():
            rows = p.plot_data["hue"] == hue
            cols = ["x", "y"]
            expected = basic.sort_df(p.plot_data.loc[rows, cols], cols)
            assert np.array_equal(data.values, expected.values)

        p = basic._LinePlotter(x="x", y="y", hue="a", size="s", data=long_df)
        for (hue, size, _), data in p.subset_data():
            rows = (p.plot_data["hue"] == hue) & (p.plot_data["size"] == size)
            cols = ["x", "y"]
            expected = basic.sort_df(p.plot_data.loc[rows, cols], cols)
            assert np.array_equal(data.values, expected.values)

    def test_aggregate(self, long_df):

        p = basic._LinePlotter(x="x", y="y", data=long_df)
        p.n_boot = 10000
        p.sort = False

        x = pd.Series(np.tile([1, 2], 100))
        y = pd.Series(np.random.randn(200))
        y_mean = y.groupby(x).mean()

        def sem(x):
            return np.std(x) / np.sqrt(len(x))

        y_sem = y.groupby(x).apply(sem)
        y_cis = pd.DataFrame(dict(low=y_mean - y_sem,
                                  high=y_mean + y_sem),
                             columns=["low", "high"])

        index, est, cis = p.aggregate(y, x, "mean", 68)
        assert np.array_equal(index.values, x.unique())
        assert est.index.equals(index)
        assert est.values == pytest.approx(y_mean.values)
        assert cis.values == pytest.approx(y_cis.values, 4)
        assert list(cis.columns) == ["low", "high"]

        index, est, cis = p.aggregate(y, x, np.mean, 68)
        assert np.array_equal(index.values, x.unique())
        assert est.index.equals(index)
        assert est.values == pytest.approx(y_mean.values)
        assert cis.values == pytest.approx(y_cis.values, 4)
        assert list(cis.columns) == ["low", "high"]

        y_std = y.groupby(x).std()
        y_cis = pd.DataFrame(dict(low=y_mean - y_std,
                                  high=y_mean + y_std),
                             columns=["low", "high"])

        index, est, cis = p.aggregate(y, x, "mean", "sd")
        assert np.array_equal(index.values, x.unique())
        assert est.index.equals(index)
        assert est.values == pytest.approx(y_mean.values)
        assert cis.values == pytest.approx(y_cis.values)
        assert list(cis.columns) == ["low", "high"]

        index, est, cis = p.aggregate(y, x, "mean", None)
        assert cis is None

        x, y = pd.Series([1, 2, 3]), pd.Series([4, 3, 2])
        index, est, cis = p.aggregate(y, x, "mean", 68)
        assert np.array_equal(index.values, x)
        assert np.array_equal(est.values, y)
        assert cis is None

        x, y = pd.Series([1, 1, 2]), pd.Series([2, 3, 4])
        index, est, cis = p.aggregate(y, x, "mean", 68)
        assert cis.loc[2].isnull().all()

    def test_legend_data(self, long_df):

        f, ax = plt.subplots()

        p = basic._LinePlotter(x="x", y="y", data=long_df, legend="full")
        p.add_legend_data(ax)
        handles, _ = ax.get_legend_handles_labels()
        assert handles == []

        # --

        ax.clear()
        p = basic._LinePlotter(x="x", y="y", hue="a", data=long_df,
                               legend="full")
        p.add_legend_data(ax)
        handles, labels = ax.get_legend_handles_labels()
        colors = [h.get_color() for h in handles]
        assert labels == p.hue_levels
        assert colors == [p.palette[l] for l in labels]

        # --

        ax.clear()
        p = basic._LinePlotter(x="x", y="y", hue="a", style="a",
                               markers=True, legend="full", data=long_df)
        p.add_legend_data(ax)
        handles, labels = ax.get_legend_handles_labels()
        colors = [h.get_color() for h in handles]
        markers = [h.get_marker() for h in handles]
        assert labels == p.hue_levels == p.style_levels
        assert colors == [p.palette[l] for l in labels]
        assert markers == [p.markers[l] for l in labels]

        # --

        ax.clear()
        p = basic._LinePlotter(x="x", y="y", hue="a", style="b",
                               markers=True, legend="full", data=long_df)
        p.add_legend_data(ax)
        handles, labels = ax.get_legend_handles_labels()
        colors = [h.get_color() for h in handles]
        markers = [h.get_marker() for h in handles]
        expected_colors = ([p.palette[l] for l in p.hue_levels]
                           + [".2" for _ in p.style_levels])
        expected_markers = (["None" for _ in p.hue_levels]
                            + [p.markers[l] for l in p.style_levels])
        assert labels == p.hue_levels + p.style_levels
        assert colors == expected_colors
        assert markers == expected_markers

        # --

        ax.clear()
        p = basic._LinePlotter(x="x", y="y", hue="a", size="a", data=long_df,
                               legend="full")
        p.add_legend_data(ax)
        handles, labels = ax.get_legend_handles_labels()
        colors = [h.get_color() for h in handles]
        widths = [h.get_linewidth() for h in handles]
        assert labels == p.hue_levels == p.size_levels
        assert colors == [p.palette[l] for l in labels]
        assert widths == [p.sizes[l] for l in labels]

        # --

        x, y = np.random.randn(2, 40)
        z = np.tile(np.arange(20), 2)

        p = basic._LinePlotter(x=x, y=y, hue=z)

        ax.clear()
        p.legend = "full"
        p.add_legend_data(ax)
        handles, labels = ax.get_legend_handles_labels()
        assert labels == [str(l) for l in p.hue_levels]

        ax.clear()
        p.legend = "brief"
        p.add_legend_data(ax)
        handles, labels = ax.get_legend_handles_labels()
        assert len(labels) == 4

        p = basic._LinePlotter(x=x, y=y, size=z)

        ax.clear()
        p.legend = "full"
        p.add_legend_data(ax)
        handles, labels = ax.get_legend_handles_labels()
        assert labels == [str(l) for l in p.size_levels]

        ax.clear()
        p.legend = "brief"
        p.add_legend_data(ax)
        handles, labels = ax.get_legend_handles_labels()
        assert len(labels) == 4

        ax.clear()
        p.legend = "bad_value"
        with pytest.raises(ValueError):
            p.add_legend_data(ax)

    def test_plot(self, long_df):

        f, ax = plt.subplots()

        p = basic._LinePlotter(x="x", y="y", data=long_df,
                               sort=False, estimator=None)
        p.plot(ax, {})
        line, = ax.lines
        assert np.array_equal(line.get_xdata(), long_df.x.values)
        assert np.array_equal(line.get_ydata(), long_df.y.values)

        ax.clear()
        p.plot(ax, {"color": "k", "label": "test"})
        line, = ax.lines
        assert line.get_color() == "k"
        assert line.get_label() == "test"

        p = basic._LinePlotter(x="x", y="y", data=long_df,
                               sort=True, estimator=None)

        ax.clear()
        p.plot(ax, {})
        line, = ax.lines
        sorted_data = basic.sort_df(long_df, ["x", "y"])
        assert np.array_equal(line.get_xdata(), sorted_data.x.values)
        assert np.array_equal(line.get_ydata(), sorted_data.y.values)

        p = basic._LinePlotter(x="x", y="y", hue="a", data=long_df)

        ax.clear()
        p.plot(ax, {})
        assert len(ax.lines) == len(p.hue_levels)
        for line, level in zip(ax.lines, p.hue_levels):
            assert line.get_color() == p.palette[level]

        p = basic._LinePlotter(x="x", y="y", size="a", data=long_df)

        ax.clear()
        p.plot(ax, {})
        assert len(ax.lines) == len(p.size_levels)
        for line, level in zip(ax.lines, p.size_levels):
            assert line.get_linewidth() == p.sizes[level]

        p = basic._LinePlotter(x="x", y="y", hue="a", style="a",
                               markers=True, data=long_df)

        ax.clear()
        p.plot(ax, {})
        assert len(ax.lines) == len(p.hue_levels) == len(p.style_levels)
        for line, level in zip(ax.lines, p.hue_levels):
            assert line.get_color() == p.palette[level]
            assert line.get_marker() == p.markers[level]

        p = basic._LinePlotter(x="x", y="y", hue="a", style="b",
                               markers=True, data=long_df)

        ax.clear()
        p.plot(ax, {})
        levels = product(p.hue_levels, p.style_levels)
        assert len(ax.lines) == (len(p.hue_levels) * len(p.style_levels))
        for line, (hue, style) in zip(ax.lines, levels):
            assert line.get_color() == p.palette[hue]
            assert line.get_marker() == p.markers[style]

        p = basic._LinePlotter(x="x", y="y", data=long_df,
                               estimator="mean", errstyle="band", ci="sd",
                               sort=True)

        ax.clear()
        p.plot(ax, {})
        line, = ax.lines
        expected_data = long_df.groupby("x").y.mean()
        assert np.array_equal(line.get_xdata(), expected_data.index.values)
        assert np.allclose(line.get_ydata(), expected_data.values)
        assert len(ax.collections) == 1

        p = basic._LinePlotter(x="x", y="y", hue="a", data=long_df,
                               estimator="mean", errstyle="band", ci="sd")

        ax.clear()
        p.plot(ax, {})
        assert len(ax.lines) == len(ax.collections) == len(p.hue_levels)
        for c in ax.collections:
            assert isinstance(c, mpl.collections.PolyCollection)

        p = basic._LinePlotter(x="x", y="y", hue="a", data=long_df,
                               estimator="mean", errstyle="bars", ci="sd")

        ax.clear()
        p.plot(ax, {})
        assert len(ax.lines) == len(ax.collections) == len(p.hue_levels)
        for c in ax.collections:
            assert isinstance(c, mpl.collections.LineCollection)

    def test_axis_labels(self, long_df):

        f, (ax1, ax2) = plt.subplots(1, 2, sharey=True)

        p = basic._LinePlotter(x="x", y="y", data=long_df)

        p.plot(ax1, {})
        assert ax1.get_xlabel() == "x"
        assert ax1.get_ylabel() == "y"

        p.plot(ax2, {})
        assert ax2.get_xlabel() == "x"
        assert ax2.get_ylabel() == "y"
        assert not ax2.yaxis.label.get_visible()

    def test_lineplot_axes(self, wide_df):

        f1, ax1 = plt.subplots()
        f2, ax2 = plt.subplots()

        ax = basic.lineplot(data=wide_df)
        assert ax is ax2

        ax = basic.lineplot(data=wide_df, ax=ax1)
        assert ax is ax1

    def test_lineplot_smoke(self, flat_array, flat_series,
                            wide_array, wide_list, wide_list_of_series,
                            wide_df, long_df):

        f, ax = plt.subplots()

        basic.lineplot(data=flat_array)
        ax.clear()

        basic.lineplot(data=flat_series)
        ax.clear()

        basic.lineplot(data=wide_array)
        ax.clear()

        basic.lineplot(data=wide_list)
        ax.clear()

        basic.lineplot(data=wide_list_of_series)
        ax.clear()

        basic.lineplot(data=wide_df)
        ax.clear()

        basic.lineplot(x="x", y="y", data=long_df)
        ax.clear()

        basic.lineplot(x=long_df.x, y=long_df.y)
        ax.clear()

        basic.lineplot(x=long_df.x, y="y", data=long_df)
        ax.clear()

        basic.lineplot(x="x", y=long_df.y.values, data=long_df)
        ax.clear()

        basic.lineplot(x="x", y="y", hue="a", data=long_df)
        ax.clear()

        basic.lineplot(x="x", y="y", hue="a", style="a", data=long_df)
        ax.clear()

        basic.lineplot(x="x", y="y", hue="a", style="b", data=long_df)
        ax.clear()

        basic.lineplot(x="x", y="y", hue="a", size="a", data=long_df)
        ax.clear()

        basic.lineplot(x="x", y="y", hue="a", size="s", data=long_df)
        ax.clear()
