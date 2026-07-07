# test_gis_geop_plot.py 
# Test gis/geop_plot function for displaying geopandas plots
# Copyright (C) 2026 University of California
# -----------------------------------------------------------------------------
# This information is free; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This work is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# For a copy of the GNU General Public License, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
# -----------------------------------------------------------------------------


import importlib
from unittest.mock import patch, Mock


def _get_geop_plot_module():
    """Get the actual geop_plot module (not the function shadowed by __init__.py)."""
    return importlib.import_module('iwfm.gis.geop_plot')


def test_geop_plot_imports():
    '''Test that the geop_plot module exposes a callable function.'''
    mod = _get_geop_plot_module()

    assert callable(mod.geop_plot)


def test_geop_plot_basic():
    '''Test basic functionality of geop_plot.'''
    with patch('matplotlib.pyplot.show') as mock_show:
        from iwfm.gis.geop_plot import geop_plot

        # Create mock geopandas dataframe
        mock_gdf = Mock()
        mock_gdf.plot.return_value = Mock()

        geop_plot(mock_gdf)

        mock_gdf.plot.assert_called_once()
        mock_show.assert_called_once()


def test_geop_plot_with_args():
    '''Test geop_plot with arguments passed to plot.'''
    with patch('matplotlib.pyplot.show') as mock_show:
        from iwfm.gis.geop_plot import geop_plot

        mock_gdf = Mock()
        mock_gdf.plot.return_value = Mock()

        geop_plot(mock_gdf, column='value', cmap='viridis')

        mock_gdf.plot.assert_called_once()


def test_geop_plot_function_signature():
    '''Test that geop_plot has correct function signature.'''
    from iwfm.gis.geop_plot import geop_plot
    import inspect

    sig = inspect.signature(geop_plot)
    params = list(sig.parameters.keys())

    assert 'gdf' in params
