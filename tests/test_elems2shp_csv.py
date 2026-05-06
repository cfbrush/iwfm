#!/usr/bin/env python
# test_elems2shp_csv.py
# Unit tests for gis/elems2shp_csv.py
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

from iwfm.gis.elems2shp_csv import elems2shp_csv


@pytest.fixture
def two_quads():
    """Two adjacent quads. Each elem_nodes row is [elem_id, n1, n2, n3, n4]."""
    elem_nodes = [[1, 1, 2, 3, 4], [2, 2, 5, 6, 3]]
    node_coord_dict = {
        1: (0.0, 0.0),
        2: (1.0, 0.0),
        3: (1.0, 1.0),
        4: (0.0, 1.0),
        5: (2.0, 0.0),
        6: (2.0, 1.0),
    }
    return elem_nodes, node_coord_dict


class TestElems2ShpCsv:
    """Writes POLYGON shapefile from CSV-style input. Each elem_nodes row =
    [elem_id, n1, n2, n3, n4]. Trailing 0 in node slot indicates triangle.
    Output fields: elem_id, node1..nodeN."""

    def test_creates_files(self, tmp_path, two_quads):
        elem_nodes, node_coords = two_quads
        out = str(tmp_path / "elems.shp")
        elems2shp_csv(elem_nodes, node_coords, shapename=out, verbose=False)

        base = out[:-4]
        for ext in ('.shp', '.shx', '.dbf', '.prj'):
            assert os.path.isfile(base + ext)

    def test_polygon_type(self, tmp_path, two_quads):
        elem_nodes, node_coords = two_quads
        out = str(tmp_path / "e.shp")
        elems2shp_csv(elem_nodes, node_coords, shapename=out, verbose=False)
        with shapefile.Reader(out) as r:
            assert r.shapeType == shapefile.POLYGON
            assert len(r.shapes()) == 2

    def test_record_fields(self, tmp_path, two_quads):
        elem_nodes, node_coords = two_quads
        out = str(tmp_path / "e.shp")
        elems2shp_csv(elem_nodes, node_coords, shapename=out, verbose=False)
        with shapefile.Reader(out) as r:
            field_names = [f[0] for f in r.fields[1:]]
            assert 'elem_id' in field_names
            assert 'node1' in field_names
            recs = r.records()
            assert recs[0]['elem_id'] == 1
            assert recs[0]['node1'] == 1
            assert recs[1]['elem_id'] == 2

    def test_triangle_handled(self, tmp_path):
        """Trailing 0 in node slot marks triangle — node count drops by 1."""
        elem_nodes = [[1, 1, 2, 3, 0]]  # triangle
        node_coords = {1: (0.0, 0.0), 2: (1.0, 0.0), 3: (0.0, 1.0)}
        out = str(tmp_path / "tri.shp")
        elems2shp_csv(elem_nodes, node_coords, shapename=out, verbose=False)

        with shapefile.Reader(out) as r:
            shapes = r.shapes()
            assert len(shapes) == 1
            # Triangle polygon: 3 distinct points + closing point = 4 entries
            assert len(shapes[0].points) == 4

    def test_shapename_strips_extension(self, tmp_path, two_quads):
        elem_nodes, node_coords = two_quads
        # Pass with .shp and without — both should produce files
        out_with = str(tmp_path / "with.shp")
        elems2shp_csv(elem_nodes, node_coords, shapename=out_with, verbose=False)
        assert os.path.isfile(out_with)

        out_no = str(tmp_path / "no_ext")
        elems2shp_csv(elem_nodes, node_coords, shapename=out_no, verbose=False)
        assert os.path.isfile(out_no + '.shp')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
