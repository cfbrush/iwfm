# test_gw_well_lay_elev.py
# Unit tests for gw_well_lay_elev in the iwfm package
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

import inspect

import pytest


def test_gw_well_lay_elev_function_exists():
    """Test that the function exists and is callable."""
    from iwfm.gw_well_lay_elev import gw_well_lay_elev
    assert callable(gw_well_lay_elev)


def test_gw_well_lay_elev_function_signature():
    """Test the function signature."""
    from iwfm.gw_well_lay_elev import gw_well_lay_elev

    params = list(inspect.signature(gw_well_lay_elev).parameters)
    assert params == ['d_wellinfo', 'elem_nodes_d', 'node_xy_d', 'strat', 'verbose']


def test_gw_well_lay_elev_has_docstring():
    """Test that the function is documented."""
    from iwfm.gw_well_lay_elev import gw_well_lay_elev
    assert gw_well_lay_elev.__doc__ is not None


def test_gw_well_lay_elev_smoke():
    """Interpolate layer elevations for a well at an element node."""
    import iwfm

    strat = [
        [1, 100.0, 0.0, 50.0],
        [2, 110.0, 0.0, 50.0],
        [3, 120.0, 0.0, 50.0],
        [4, 130.0, 0.0, 50.0],
    ]
    elem_nodes_d = {1: [1, 2, 3, 4]}
    node_xy_d = {1: (0.0, 0.0), 2: (1.0, 0.0), 3: (1.0, 1.0), 4: (0.0, 1.0)}
    d_wellinfo = {'W1': [0.0, 0.0, 'x', 'y', 1]}

    out = iwfm.gw_well_lay_elev(d_wellinfo, elem_nodes_d, node_xy_d, strat)

    aquifer_top = out['W1'][-1][0]
    assert aquifer_top[0] == pytest.approx(100.0)  # exact at node 1
