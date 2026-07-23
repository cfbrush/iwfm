#!/usr/bin/env python
# test_nodes2shp_csv.py
# Unit tests for gis/nodes2shp_csv.py
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

from iwfm.gis.nodes2shp_csv import nodes2shp_csv


class TestNodes2ShpCsv:
    """nodes2shp_csv writes a POINT shapefile from {node_id: (x, y)} input.
    Outputs .shp/.shx/.dbf/.prj files with fields node_id (N), x (F), y (F)."""

    def test_basic_three_points(self, tmp_path):
        coords = {1: (100.0, 200.0), 2: (150.5, 250.5), 3: (300.0, 400.0)}
        out = str(tmp_path / "nodes.shp")
        nodes2shp_csv(coords, shapename=out, epsg=26910)

        # Verify all four files were created
        base = out[:-4]
        assert os.path.isfile(base + '.shp')
        assert os.path.isfile(base + '.shx')
        assert os.path.isfile(base + '.dbf')
        assert os.path.isfile(base + '.prj')

    def test_shapefile_is_point_type(self, tmp_path):
        coords = {1: (0.0, 0.0)}
        out = str(tmp_path / "p.shp")
        nodes2shp_csv(coords, shapename=out)

        with shapefile.Reader(out) as r:
            assert r.shapeType == shapefile.POINT
            assert len(r.shapes()) == 1

    def test_record_count_matches_input(self, tmp_path):
        coords = {i: (float(i), float(i * 10)) for i in range(1, 6)}
        out = str(tmp_path / "n.shp")
        nodes2shp_csv(coords, shapename=out)

        with shapefile.Reader(out) as r:
            assert len(r.records()) == 5

    def test_record_fields(self, tmp_path):
        coords = {42: (12.5, 34.5)}
        out = str(tmp_path / "n.shp")
        nodes2shp_csv(coords, shapename=out)

        with shapefile.Reader(out) as r:
            field_names = [f[0] for f in r.fields[1:]]  # skip DeletionFlag
            assert 'node_id' in field_names
            assert 'x' in field_names
            assert 'y' in field_names
            rec = r.records()[0]
            assert rec['node_id'] == 42
            assert rec['x'] == pytest.approx(12.5)
            assert rec['y'] == pytest.approx(34.5)

    def test_geometry_matches_input(self, tmp_path):
        coords = {1: (100.0, 200.0), 2: (300.0, 400.0)}
        out = str(tmp_path / "n.shp")
        nodes2shp_csv(coords, shapename=out)

        with shapefile.Reader(out) as r:
            shapes = r.shapes()
            pts = sorted([(s.points[0][0], s.points[0][1]) for s in shapes])
            assert pts == [(100.0, 200.0), (300.0, 400.0)]

    def test_shapename_with_or_without_extension(self, tmp_path):
        """Function strips trailing '.shp' from shapename."""
        coords = {1: (1.0, 2.0)}
        out = str(tmp_path / "with_ext.shp")
        nodes2shp_csv(coords, shapename=out)
        assert os.path.isfile(out)

        out2_base = str(tmp_path / "no_ext")
        nodes2shp_csv(coords, shapename=out2_base)
        assert os.path.isfile(out2_base + '.shp')

    def test_prj_file_has_epsg_wkt(self, tmp_path):
        coords = {1: (0.0, 0.0)}
        out = str(tmp_path / "n.shp")
        nodes2shp_csv(coords, shapename=out, epsg=26910)
        prj = (tmp_path / "n.prj").read_text()
        # .prj sidecars must be ESRI WKT1 (PROJCS[...); QGIS rejects WKT2
        assert prj.startswith('PROJCS[')
        assert 'NAD' in prj and 'UTM' in prj

    def test_empty_coords(self, tmp_path):
        out = str(tmp_path / "empty.shp")
        nodes2shp_csv({}, shapename=out)
        with shapefile.Reader(out) as r:
            assert len(r.shapes()) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
