#!/usr/bin/env python
# test_gis_prj_wkt1.py
# Regression tests: shapefile .prj sidecars must be ESRI WKT1, not WKT2
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

"""Every shapefile writer's .prj sidecar must be ESRI WKT1.

QGIS (and ArcGIS) do not accept WKT2 in .prj files: an ESRI WKT1 string
starts with ``PROJCS[``, a WKT2 string with ``PROJCRS[``. pyproj's
``to_wkt()`` defaults to WKT2, so every writer must request
``version='WKT1_ESRI'`` explicitly.
"""

import pytest

shapefile = pytest.importorskip("shapefile")

import iwfm.gis as gis


def assert_wkt1(prj_path):
    wkt = prj_path.read_text()
    assert wkt.startswith('PROJCS['), f'{prj_path.name} is not ESRI WKT1: {wkt[:40]}'
    assert 'PROJCRS' not in wkt


NODE_COORDS = [[1, 0.0, 0.0], [2, 1.0, 0.0], [3, 1.0, 1.0], [4, 0.0, 1.0]]
COORD_DICT = {1: (0.0, 0.0), 2: (1.0, 0.0), 3: (1.0, 1.0), 4: (0.0, 1.0)}


class TestPrjIsEsriWkt1:

    def test_elem2shp(self, tmp_path):
        base = str(tmp_path / 'm')
        gis.elem2shp([1], [[1, 2, 3, 4]], COORD_DICT, [1], [],
                     shape_name=base, epsg=26910)
        assert_wkt1(tmp_path / 'm_Elements.prj')

    def test_nodes2shp(self, tmp_path):
        base = str(tmp_path / 'm')
        gis.nodes2shp(NODE_COORDS, base, epsg=26910)
        assert_wkt1(tmp_path / 'm_Nodes.prj')

    def test_snodes2shp(self, tmp_path):
        base = str(tmp_path / 'm')
        gis.snodes2shp(1, [(101, 1, 1)], NODE_COORDS, base, epsg=26910)
        assert_wkt1(tmp_path / 'm_StreamNodes.prj')

    def test_reach2shp(self, tmp_path):
        base = str(tmp_path / 'm')
        reach_list = [[1, 101, 102, 0]]
        stnodes_dict = {101: [1, 1, 0.0], 102: [2, 1, 0.0]}
        gis.reach2shp(reach_list, stnodes_dict, NODE_COORDS, base, epsg=26910)
        assert_wkt1(tmp_path / 'm_StreamReaches.prj')

    def test_igsm_elem2shp(self, tmp_path):
        base = str(tmp_path / 'm')
        elem_char = [[1, 1, 1, 1, 1]]
        gis.igsm_elem2shp([[1, 1, 2, 3, 4]], NODE_COORDS, elem_char, [],
                          base, epsg=26910)
        assert_wkt1(tmp_path / 'm_Elements.prj')

    def test_nodes2shp_csv(self, tmp_path):
        out = str(tmp_path / 'n.shp')
        gis.nodes2shp_csv(COORD_DICT, shapename=out, epsg=26910)
        assert_wkt1(tmp_path / 'n.prj')

    def test_elems2shp_csv(self, tmp_path):
        out = str(tmp_path / 'e.shp')
        gis.elems2shp_csv([[1, 1, 2, 3, 4]], COORD_DICT, shapename=out,
                          epsg=26910, verbose=False)
        assert_wkt1(tmp_path / 'e.prj')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
