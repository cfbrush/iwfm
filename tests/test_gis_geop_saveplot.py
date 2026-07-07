# test_gis_geop_saveplot.py 
# Test gis/geop_saveplot function for saving geopandas plots
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


def _get_geop_saveplot_module():
    """Get the actual geop_saveplot module (not the function shadowed by __init__.py)."""
    return importlib.import_module('iwfm.gis.geop_saveplot')


def test_geop_saveplot_imports():
    '''Test that the geop_saveplot module exposes a callable function.'''
    mod = _get_geop_saveplot_module()

    assert callable(mod.geop_saveplot)


def test_geop_saveplot_basic(tmp_path):
    '''Test basic functionality of geop_saveplot.'''
    with patch('matplotlib.pyplot.savefig') as mock_savefig:
        from iwfm.gis.geop_saveplot import geop_saveplot

        # Create mock geopandas dataframe
        mock_gdf = Mock()
        mock_gdf.plot.return_value = Mock()

        outfile = tmp_path / 'plot.png'

        geop_saveplot(mock_gdf, str(outfile))

        mock_gdf.plot.assert_called_once()
        mock_savefig.assert_called_once()


def test_geop_saveplot_with_args(tmp_path):
    '''Test geop_saveplot with plot arguments.'''
    with patch('matplotlib.pyplot.savefig') as mock_savefig:
        from iwfm.gis.geop_saveplot import geop_saveplot

        mock_gdf = Mock()
        mock_gdf.plot.return_value = Mock()

        outfile = tmp_path / 'plot.png'

        geop_saveplot(mock_gdf, str(outfile), column='value', cmap='plasma')

        mock_gdf.plot.assert_called_once()


def test_geop_saveplot_function_signature():
    '''Test that geop_saveplot has correct function signature.'''
    from iwfm.gis.geop_saveplot import geop_saveplot
    import inspect

    sig = inspect.signature(geop_saveplot)
    params = list(sig.parameters.keys())

    assert 'gdf' in params
    assert 'outname' in params
