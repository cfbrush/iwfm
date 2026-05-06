#!/usr/bin/env python
# test_elem2boundingpoly.py
# Unit tests for gis/elem2boundingpoly.py
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

shapely = pytest.importorskip("shapely")
from shapely.geometry import Polygon

from iwfm.gis.elem2boundingpoly import elem2boundingpoly


class TestElem2BoundingPoly:
    """Builds a shapely Polygon of the model boundary by unioning per-element
    polygons. Skips nodes that are <=0 or missing from node_coords (sub-models
    with sentinel zeros). Returns Polygon() on empty/invalid input.

    `node_coords` is a list of `[node_id, x, y]` rows."""

    def test_two_quads_form_rectangle(self):
        """Two adjacent unit squares share an edge → bounding poly is the 2×1
        rectangle they cover."""
        node_coords = [
            [1, 0.0, 0.0],
            [2, 1.0, 0.0],
            [3, 1.0, 1.0],
            [4, 0.0, 1.0],
            [5, 2.0, 0.0],
            [6, 2.0, 1.0],
        ]
        elem_nodes = [[1, 2, 3, 4], [2, 5, 6, 3]]
        result = elem2boundingpoly(elem_nodes, node_coords)
        assert isinstance(result, Polygon)
        assert result.area == pytest.approx(2.0)

    def test_single_triangle(self):
        node_coords = [[1, 0.0, 0.0], [2, 1.0, 0.0], [3, 0.0, 1.0]]
        elem_nodes = [[1, 2, 3]]
        result = elem2boundingpoly(elem_nodes, node_coords)
        assert result.area == pytest.approx(0.5)

    def test_empty_returns_empty_polygon(self):
        """No elements → Polygon()."""
        result = elem2boundingpoly([], [[1, 0.0, 0.0]])
        assert isinstance(result, Polygon)
        assert result.is_empty

    def test_skip_zero_node_ids(self):
        """Elements may pad with `0` node ids (e.g. triangles in a quad slot);
        these are skipped."""
        node_coords = [
            [1, 0.0, 0.0],
            [2, 1.0, 0.0],
            [3, 0.0, 1.0],
        ]
        # 4-slot element with last slot = 0 (triangle in quad slot)
        elem_nodes = [[1, 2, 3, 0]]
        result = elem2boundingpoly(elem_nodes, node_coords)
        assert result.area == pytest.approx(0.5)

    def test_skip_missing_node_ids(self):
        """Sub-model: element references node 99 absent from node_coords. The
        function silently drops it and uses remaining 3 valid nodes."""
        node_coords = [[1, 0.0, 0.0], [2, 1.0, 0.0], [3, 0.0, 1.0]]
        elem_nodes = [[1, 2, 3, 99]]
        result = elem2boundingpoly(elem_nodes, node_coords)
        assert result.area == pytest.approx(0.5)

    def test_returns_polygon_type(self):
        node_coords = [[1, 0.0, 0.0], [2, 1.0, 0.0], [3, 0.0, 1.0]]
        elem_nodes = [[1, 2, 3]]
        result = elem2boundingpoly(elem_nodes, node_coords)
        assert result.geom_type == 'Polygon'

    def test_invalid_polygon_skipped(self):
        """Element with only 2 valid nodes (not enough for a polygon) is skipped.
        With one valid quad and one degenerate, result is just the valid quad."""
        node_coords = [
            [1, 0.0, 0.0],
            [2, 1.0, 0.0],
            [3, 1.0, 1.0],
            [4, 0.0, 1.0],
        ]
        elem_nodes = [[1, 2, 3, 4], [1, 2, 0, 0]]  # 2nd has only 2 valid nodes
        result = elem2boundingpoly(elem_nodes, node_coords)
        assert result.area == pytest.approx(1.0)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
