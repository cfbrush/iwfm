# test_gis_shp_crs.py
# Unit tests for the shp_crs function in the iwfm.gis package
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
import tempfile

import pytest
import shapefile
from pyproj import CRS


def _write_point_shapefile(basepath):
    """Write a minimal point shapefile at basepath (no extension)."""
    with shapefile.Writer(basepath, shapeType=shapefile.POINT) as w:
        w.field('ID', 'N')
        w.point(-121.5, 38.5)
        w.record(1)


class TestShpCrsFunctionExists:
    def test_import_from_gis(self):
        import iwfm.gis
        assert callable(iwfm.gis.shp_crs)

    def test_import_directly(self):
        from iwfm.gis.shp_crs import shp_crs
        assert callable(shp_crs)

    def test_function_has_docstring(self):
        from iwfm.gis.shp_crs import shp_crs
        assert shp_crs.__doc__ is not None


class TestShpCrs:
    def test_reads_crs_from_prj(self):
        from iwfm.gis.shp_crs import shp_crs

        with tempfile.TemporaryDirectory() as d:
            base = os.path.join(d, 'pts')
            _write_point_shapefile(base)
            with open(base + '.prj', 'w', encoding='utf-8') as f:
                f.write(CRS.from_epsg(4326).to_wkt(version='WKT1_ESRI'))

            crs = shp_crs(base + '.shp')

            assert crs is not None
            assert crs.to_epsg() == 4326

    def test_projected_crs(self):
        from iwfm.gis.shp_crs import shp_crs

        with tempfile.TemporaryDirectory() as d:
            base = os.path.join(d, 'pts')
            _write_point_shapefile(base)
            with open(base + '.prj', 'w', encoding='utf-8') as f:
                f.write(CRS.from_epsg(26910).to_wkt(version='WKT1_ESRI'))  # NAD83 / UTM 10N

            crs = shp_crs(base + '.shp')

            assert crs is not None
            assert crs.is_projected

    def test_missing_prj_returns_none(self):
        from iwfm.gis.shp_crs import shp_crs

        with tempfile.TemporaryDirectory() as d:
            base = os.path.join(d, 'pts')
            _write_point_shapefile(base)

            assert shp_crs(base + '.shp') is None
