#!/usr/bin/env python
# test_elem2shp.py
# Unit tests for gis/elem2shp.py
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

from iwfm.gis.elem2shp import elem2shp


@pytest.fixture
def two_quads():
    """Two adjacent quadrilateral elements sharing nodes 2,3.
    Nodes laid out as a 1x2 grid:
        4 - 3 - 6
        |   |   |
        1 - 2 - 5
    Element 1 = nodes [1,2,3,4]; element 2 = nodes [2,5,6,3].
    """
    elem_ids = [1, 2]
    elem_nodes = [[1, 2, 3, 4], [2, 5, 6, 3]]
    node_coord_dict = {
        1: (0.0, 0.0),
        2: (1.0, 0.0),
        3: (1.0, 1.0),
        4: (0.0, 1.0),
        5: (2.0, 0.0),
        6: (2.0, 1.0),
    }
    elem_sub = [1, 2]
    return elem_ids, elem_nodes, node_coord_dict, elem_sub


class TestElem2Shp:
    """elem2shp writes a POLYGON shapefile from per-element node-id lists.
    Output files: <base>_Elements.shp/.shx/.dbf/.prj. Fields: elem_id (N),
    subregion (N), lake_no (N)."""

    def test_creates_shapefile_set(self, tmp_path, two_quads):
        elem_ids, elem_nodes, node_coords, elem_sub = two_quads
        base = str(tmp_path / "model")
        elem2shp(elem_ids, elem_nodes, node_coords, elem_sub, [],
                 shape_name=base, epsg=26910)

        for ext in ('.shp', '.shx', '.dbf', '.prj'):
            assert os.path.isfile(base + '_Elements' + ext), f"missing {ext}"

    def test_polygon_type(self, tmp_path, two_quads):
        elem_ids, elem_nodes, node_coords, elem_sub = two_quads
        base = str(tmp_path / "model")
        elem2shp(elem_ids, elem_nodes, node_coords, elem_sub, [], shape_name=base)

        with shapefile.Reader(base + '_Elements.shp') as r:
            assert r.shapeType == shapefile.POLYGON

    def test_record_count(self, tmp_path, two_quads):
        elem_ids, elem_nodes, node_coords, elem_sub = two_quads
        base = str(tmp_path / "model")
        elem2shp(elem_ids, elem_nodes, node_coords, elem_sub, [], shape_name=base)

        with shapefile.Reader(base + '_Elements.shp') as r:
            assert len(r.records()) == 2

    def test_record_fields(self, tmp_path, two_quads):
        elem_ids, elem_nodes, node_coords, elem_sub = two_quads
        base = str(tmp_path / "model")
        elem2shp(elem_ids, elem_nodes, node_coords, elem_sub, [], shape_name=base)

        with shapefile.Reader(base + '_Elements.shp') as r:
            field_names = [f[0] for f in r.fields[1:]]
            assert {'elem_id', 'subregion', 'lake_no'} <= set(field_names)
            recs = r.records()
            assert recs[0]['elem_id'] == 1
            assert recs[0]['subregion'] == 1
            assert recs[1]['elem_id'] == 2

    def test_lake_no_zero_when_no_lakes(self, tmp_path, two_quads):
        elem_ids, elem_nodes, node_coords, elem_sub = two_quads
        base = str(tmp_path / "model")
        elem2shp(elem_ids, elem_nodes, node_coords, elem_sub, [], shape_name=base)

        with shapefile.Reader(base + '_Elements.shp') as r:
            for rec in r.records():
                assert rec['lake_no'] == 0

    def test_lake_assignment(self, tmp_path, two_quads):
        """When `lakes` lists [lake_no, elem_idx_1based], elements with that
        index get lake_no in their record."""
        elem_ids, elem_nodes, node_coords, elem_sub = two_quads
        # lake 7 is on element index 2 (1-based) — i.e. the second element
        lakes = [[7, 2]]
        base = str(tmp_path / "model")
        elem2shp(elem_ids, elem_nodes, node_coords, elem_sub, lakes, shape_name=base)

        with shapefile.Reader(base + '_Elements.shp') as r:
            recs = r.records()
            assert recs[0]['lake_no'] == 0
            assert recs[1]['lake_no'] == 7


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
