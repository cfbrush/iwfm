#!/usr/bin/env python
# test_elem_poly_coords_wkt.py
# Unit tests for elem_poly_coords_wkt.py
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

from iwfm.elem_poly_coords_wkt import elem_poly_coords_wkt


# Shared fixtures: a minimal mesh with 4 nodes forming one square + one triangle.
# Node IDs are 1-based (IWFM convention); node_coords is 0-indexed (so
# elem_poly_coords_wkt subtracts 1 to look up coords).
NODE_COORDS = [
    [0.0, 0.0],   # node 1
    [10.0, 0.0],  # node 2
    [10.0, 10.0], # node 3
    [0.0, 10.0],  # node 4
    [20.0, 0.0],  # node 5
]


class TestElemPolyCoordsWkt:
    """Tests for elem_poly_coords_wkt() — convert per-element node id lists
    into WKT POLYGON strings, with the first vertex repeated for closure.
    """

    def test_single_quad(self):
        """A 4-node square produces one POLYGON with 5 coordinate pairs."""
        elem_nodes = [[1, 2, 3, 4]]
        result = elem_poly_coords_wkt(elem_nodes, NODE_COORDS)
        assert len(result) == 1
        assert result[0] == 'POLYGON ((0.0 0.0, 10.0 0.0, 10.0 10.0, 0.0 10.0, 0.0 0.0))'

    def test_single_triangle(self):
        """A 3-node triangle produces one POLYGON with 4 coordinate pairs."""
        elem_nodes = [[1, 2, 5]]
        result = elem_poly_coords_wkt(elem_nodes, NODE_COORDS)
        assert len(result) == 1
        assert result[0] == 'POLYGON ((0.0 0.0, 10.0 0.0, 20.0 0.0, 0.0 0.0))'

    def test_multiple_elements(self):
        """Order preserved: one WKT entry per element."""
        elem_nodes = [[1, 2, 3, 4], [1, 2, 5]]
        result = elem_poly_coords_wkt(elem_nodes, NODE_COORDS)
        assert len(result) == 2
        # First element is the quad, second is the triangle
        assert '0.0 0.0, 10.0 0.0, 10.0 10.0' in result[0]
        assert '0.0 0.0, 10.0 0.0, 20.0 0.0' in result[1]

    def test_polygon_closure(self):
        """First coordinate repeats at end (WKT requires closed rings)."""
        elem_nodes = [[1, 2, 3, 4]]
        wkt = elem_poly_coords_wkt(elem_nodes, NODE_COORDS)[0]
        # Strip "POLYGON ((" and "))"
        inner = wkt[len('POLYGON (('):-len('))')]
        coords = [pair.strip() for pair in inner.split(',')]
        assert coords[0] == coords[-1]

    def test_format_starts_with_polygon(self):
        """Each result is a WKT POLYGON literal."""
        elem_nodes = [[1, 2, 3, 4], [1, 2, 5]]
        for wkt in elem_poly_coords_wkt(elem_nodes, NODE_COORDS):
            assert wkt.startswith('POLYGON ((')
            assert wkt.endswith('))')

    def test_empty_elem_nodes(self):
        """No elements → empty list, no error."""
        assert elem_poly_coords_wkt([], NODE_COORDS) == []

    def test_uses_one_based_indexing(self):
        """Node IDs are 1-based: node 1 maps to node_coords[0], etc."""
        # Single triangle that uses only nodes 1 and 5 (index 0 and 4 in
        # node_coords). If indexing were broken, we'd see different x values.
        elem_nodes = [[1, 5, 1]]  # degenerate triangle just to test indexing
        result = elem_poly_coords_wkt(elem_nodes, NODE_COORDS)
        assert '0.0 0.0' in result[0]
        assert '20.0 0.0' in result[0]

    def test_exposed_via_iwfm_namespace(self):
        """elem_poly_coords_wkt is re-exported from iwfm/__init__.py."""
        import iwfm
        assert iwfm.elem_poly_coords_wkt is elem_poly_coords_wkt


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
