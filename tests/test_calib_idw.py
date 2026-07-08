# test_calib_idw.py
# Unit tests for calib/idw.py - Inverse distance weighting (INCOMPLETE)
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

import pytest


class TestIdwStructure:
    """Structural tests for idw function (marked INCOMPLETE in source)"""

    def test_function_exists(self):
        """Test that idw function exists."""
        from iwfm.calib.idw import idw
        assert callable(idw)

    def test_function_signature(self):
        """Test function has correct parameters."""
        from iwfm.calib.idw import idw
        import inspect
        
        sig = inspect.signature(idw)
        params = list(sig.parameters.keys())
        
        assert 'x' in params
        assert 'y' in params
        assert 'elem' in params
        assert 'nnodes' in params
        assert 'nlayers' in params
        assert 'nodexy' in params
        assert 'elevations' in params
        assert 'debug' in params

    def test_debug_default_zero(self):
        """Test that debug parameter defaults to 0."""
        from iwfm.calib.idw import idw
        import inspect
        
        sig = inspect.signature(idw)
        
        assert sig.parameters['debug'].default == 0

    def test_function_has_docstring(self):
        """Test that function has documentation."""
        from iwfm.calib.idw import idw

        assert idw.__doc__ is not None

    def test_returns_list(self):
        """Test that function returns a list (basic execution)."""
        from iwfm.calib.idw import idw

        # Minimal test data
        x, y = 5.0, 5.0
        elem = 1
        nnodes = [1, 2]
        nlayers = 2
        nodexy = [[0.0, 0.0], [10.0, 10.0]]
        elevations = [[100.0, 110.0], [95.0, 105.0]]

        result = idw(x, y, elem, nnodes, nlayers, nodexy, elevations)

        assert isinstance(result, list)


class TestIdwImports:
    """Tests for module imports."""

    def test_import_from_calib(self):
        """Test import from iwfm.calib."""
        from iwfm.calib import idw
        assert callable(idw)

    def test_import_directly(self):
        """Test direct module import."""
        from iwfm.calib.idw import idw
        assert callable(idw)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])


class TestIdwBehavior:
    """Behavioral tests for inverse distance weighting."""

    def _square(self):
        # unit square, values increase with node id; 2 layers
        nnodes = [1, 2, 3, 4]
        nodexy = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
        elevations = [[10.0, 110.0], [20.0, 120.0], [30.0, 130.0], [40.0, 140.0]]
        return nnodes, nodexy, elevations

    def test_exact_at_node(self):
        from iwfm.calib.idw import idw
        nnodes, nodexy, elevations = self._square()
        result = idw(1.0, 1.0, 1, nnodes, 2, nodexy, elevations)
        assert result == [30.0, 130.0]

    def test_center_is_mean(self):
        from iwfm.calib.idw import idw
        nnodes, nodexy, elevations = self._square()
        result = idw(0.5, 0.5, 1, nnodes, 2, nodexy, elevations)
        assert result[0] == pytest.approx(25.0)
        assert result[1] == pytest.approx(125.0)

    def test_closer_node_dominates(self):
        from iwfm.calib.idw import idw
        nnodes, nodexy, elevations = self._square()
        result = idw(0.1, 0.1, 1, nnodes, 2, nodexy, elevations)
        assert result[0] < 20.0  # nearer node 1 (value 10) dominates

    def test_triangle_placeholder_zero_skipped(self):
        from iwfm.calib.idw import idw
        nnodes = [1, 2, 3, 0]
        nodexy = [(0.0, 0.0), (2.0, 0.0), (0.0, 2.0), (99.0, 99.0)]
        elevations = [[3.0], [6.0], [9.0], [999.0]]
        result = idw(1.0, 1.0, 1, nnodes, 1, nodexy, elevations)
        assert result[0] == pytest.approx(6.0)  # circumcenter: equidistant nodes


class TestGwWellLayElev:
    """Tests for gw_well_lay_elev using the corrected idw."""

    def test_well_at_node_gets_node_stratigraphy(self):
        import iwfm

        # 2-layer stratigraphy: [node_id, lse, tard_thick_1, aq_thick_1,
        #                         tard_thick_2, aq_thick_2]
        strat = [
            [1, 100.0, 0.0, 50.0, 10.0, 40.0],
            [2, 110.0, 0.0, 50.0, 10.0, 40.0],
            [3, 120.0, 0.0, 50.0, 10.0, 40.0],
            [4, 130.0, 0.0, 50.0, 10.0, 40.0],
        ]
        elem_nodes_d = {1: [1, 2, 3, 4]}
        node_xy_d = {1: (0.0, 0.0), 2: (1.0, 0.0), 3: (1.0, 1.0), 4: (0.0, 1.0)}
        # well at node 1, element 1: value[0]=x, [1]=y, [4]=elem
        d_wellinfo = {'W1': [0.0, 0.0, 'a', 'b', 1]}

        out = iwfm.gw_well_lay_elev(d_wellinfo, elem_nodes_d, node_xy_d, strat)

        assert 'W1' in out
        e_nodes, well_elevs = out['W1'][-2], out['W1'][-1]
        assert e_nodes == [1, 2, 3, 4]
        aquifer_top, aquifer_bot, aquitard_top, aquitard_bot = well_elevs
        # at node 1: lse=100, layer 1 aquifer top=100, bottom=50;
        # layer 2 aquitard 50..40, aquifer 40..0
        assert aquifer_top == pytest.approx([100.0, 40.0])
        assert aquifer_bot == pytest.approx([50.0, 0.0])
        assert aquitard_bot == pytest.approx([100.0, 40.0])

    def test_center_well_is_mean_of_nodes(self):
        import iwfm

        strat = [
            [1, 100.0, 0.0, 50.0],
            [2, 110.0, 0.0, 50.0],
            [3, 120.0, 0.0, 50.0],
            [4, 130.0, 0.0, 50.0],
        ]
        elem_nodes_d = {7: [1, 2, 3, 4]}
        node_xy_d = {1: (0.0, 0.0), 2: (1.0, 0.0), 3: (1.0, 1.0), 4: (0.0, 1.0)}
        d_wellinfo = {'W1': [0.5, 0.5, 'a', 'b', 7]}

        out = iwfm.gw_well_lay_elev(d_wellinfo, elem_nodes_d, node_xy_d, strat)

        aquifer_top = out['W1'][-1][0]
        assert aquifer_top[0] == pytest.approx(115.0)  # mean of 100,110,120,130
