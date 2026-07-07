# test_gis_grid_colorize.py 
# Test gis/grid_colorize function for colorizing grids
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
import numpy as np


def _get_grid_colorize_module():
    """Get the actual grid_colorize module (not the function shadowed by __init__.py)."""
    return importlib.import_module('iwfm.gis.grid_colorize')


def test_grid_colorize_imports():
    '''Test that grid_colorize imports colorsys (verifies fix).'''
    # This verifies the fix: added 'import colorsys'
    mod = _get_grid_colorize_module()

    assert hasattr(mod, 'colorsys')
    assert hasattr(mod.colorsys, 'hsv_to_rgb')


def test_grid_colorize_basic(tmp_path):
    '''Test grid_colorize end-to-end on a small ASCII DEM.'''
    from PIL import Image
    from iwfm.gis.grid_colorize import grid_colorize

    source = tmp_path / 'input.asc'
    target = tmp_path / 'output.png'

    ascii_dem_content = '''ncols 3
nrows 2
xllcorner 0
yllcorner 0
cellsize 1
NODATA_value -9999
0 50 100
150 200 255'''
    source.write_text(ascii_dem_content)

    grid_colorize(str(source), str(target))

    assert target.exists()
    im = Image.open(str(target))
    assert im.size == (3, 2)


def test_grid_colorize_function_signature():
    '''Test that grid_colorize has correct function signature.'''
    from iwfm.gis.grid_colorize import grid_colorize
    import inspect

    sig = inspect.signature(grid_colorize)
    params = list(sig.parameters.keys())

    assert 'source' in params
    assert 'target' in params
