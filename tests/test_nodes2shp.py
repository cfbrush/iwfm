#!/usr/bin/env python
# test_nodes2shp.py
# Unit tests for gis/nodes2shp.py
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

import os
import pytest

shapefile = pytest.importorskip("shapefile")

from iwfm.gis.nodes2shp import nodes2shp, calc_base


class TestNodes2Shp:
    """Writes a POINT shapefile from list-of-rows input where each row is
    `[node_id, x, y]`. Output base filename gets `_Nodes.shp` appended."""

    def test_basic_three_nodes(self, tmp_path):
        node_coords = [[1, 100.0, 200.0], [2, 150.0, 250.0], [3, 300.0, 400.0]]
        base = str(tmp_path / "model")
        nodes2shp(node_coords, base, epsg=26910)

        for ext in ('.shp', '.shx', '.dbf', '.prj'):
            assert os.path.isfile(base + '_Nodes' + ext)

    def test_point_type(self, tmp_path):
        node_coords = [[1, 0.0, 0.0]]
        base = str(tmp_path / "m")
        nodes2shp(node_coords, base)
        with shapefile.Reader(base + '_Nodes.shp') as r:
            assert r.shapeType == shapefile.POINT

    def test_node_id_field(self, tmp_path):
        node_coords = [[42, 12.5, 34.5]]
        base = str(tmp_path / "m")
        nodes2shp(node_coords, base)
        with shapefile.Reader(base + '_Nodes.shp') as r:
            field_names = [f[0] for f in r.fields[1:]]
            assert 'node_id' in field_names
            assert r.records()[0]['node_id'] == 42

    def test_geometry_matches(self, tmp_path):
        node_coords = [[1, 100.0, 200.0], [2, 300.0, 400.0]]
        base = str(tmp_path / "m")
        nodes2shp(node_coords, base)
        with shapefile.Reader(base + '_Nodes.shp') as r:
            pts = sorted([(s.points[0][0], s.points[0][1]) for s in r.shapes()])
            assert pts == [(100.0, 200.0), (300.0, 400.0)]


class TestCalcBase:
    """Helper that calculates per-node base elevation from stratigraphy.
    Each row: `[node_id, gse, layer1_aquitard, layer1_aquifer, ...]`.
    Base = gse - sum(all layer thicknesses)."""

    def test_single_layer(self):
        # 1 layer (aquitard + aquifer) per node: row length = 2 + 2 = 4
        strat = [[1, 100.0, 10.0, 50.0]]
        result = calc_base(strat)
        assert result == [40.0]

    def test_multi_layer(self):
        # 2 layers: row length = 2 + 4 = 6
        strat = [[1, 100.0, 5.0, 20.0, 5.0, 30.0]]
        result = calc_base(strat)
        assert result == [40.0]

    def test_multi_node(self):
        strat = [[1, 100.0, 10.0, 50.0], [2, 200.0, 20.0, 80.0]]
        result = calc_base(strat)
        assert result == [40.0, 100.0]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
