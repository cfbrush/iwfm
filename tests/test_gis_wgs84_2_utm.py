# test_gis_wgs84_2_utm.py
# Tests for gis/wgs84_2_utm.py - Reproject from WGS84 geographic coordinates to UTM
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


class TestWgs842Utm:
    """Tests for wgs84_2_utm function."""

    def test_returns_tuple(self):
        """Test that function returns a tuple of 3 values (easting, northing, altitude)."""
        from iwfm.gis.wgs84_2_utm import wgs84_2_utm

        result = wgs84_2_utm(-118.0, 34.0)

        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_returns_easting_northing_altitude_order(self):
        """Test that return order is (easting, northing, altitude)."""
        from iwfm.gis.wgs84_2_utm import wgs84_2_utm

        easting, northing, alt = wgs84_2_utm(-118.0, 34.0)

        # Easting should be positive
        assert easting > 0
        # Northing should be positive for northern hemisphere
        assert northing > 0
        # Altitude should be 0
        assert alt == 0

    def test_los_angeles_coordinates(self):
        """Test conversion of Los Angeles WGS84 coordinates."""
        from iwfm.gis.wgs84_2_utm import wgs84_2_utm

        lon, lat = -118.2437, 34.0522

        easting, northing, alt = wgs84_2_utm(lon, lat)

        # Should be reasonable UTM values for Zone 11
        assert 300000 < easting < 800000
        assert 3000000 < northing < 4500000
        assert alt == 0

    def test_san_francisco_coordinates(self):
        """Test conversion of San Francisco WGS84 coordinates."""
        from iwfm.gis.wgs84_2_utm import wgs84_2_utm

        lon, lat = -122.4194, 37.7749

        easting, northing, alt = wgs84_2_utm(lon, lat)

        # Should be reasonable UTM values for Zone 10
        assert 300000 < easting < 800000
        assert 4000000 < northing < 5000000

    def test_round_trip_with_utm_2_wgs84(self):
        """Test round-trip conversion with utm_2_wgs84."""
        from iwfm.gis.wgs84_2_utm import wgs84_2_utm
        from iwfm.gis.utm_2_wgs84 import utm_2_wgs84

        original_lon, original_lat = -118.2437, 34.0522

        # Convert to UTM
        easting, northing, _ = wgs84_2_utm(original_lon, original_lat)

        # Get zone for reverse conversion
        from iwfm.gis.get_utm_zone import get_utm_zone
        zone_number = get_utm_zone(original_lon)

        # Convert back
        lon, lat, _ = utm_2_wgs84(zone_number, easting, northing)

        # Should be close to original
        assert abs(lon - original_lon) < 0.001
        assert abs(lat - original_lat) < 0.001

    def test_easting_range(self):
        """Test that easting is in valid UTM range."""
        from iwfm.gis.wgs84_2_utm import wgs84_2_utm

        # Test several points
        test_points = [
            (-118.0, 34.0),
            (-122.0, 37.0),
            (-93.0, 45.0),
        ]

        for lon, lat in test_points:
            easting, northing, _ = wgs84_2_utm(lon, lat)
            # Valid UTM easting range is typically 100,000 to 900,000
            assert 100000 < easting < 900000


class TestWgs842UtmImports:
    """Tests for wgs84_2_utm imports."""

    def test_import_from_gis(self):
        """Test import from iwfm.gis."""
        from iwfm.gis import wgs84_2_utm
        assert callable(wgs84_2_utm)

    def test_import_directly(self):
        """Test direct module import."""
        from iwfm.gis.wgs84_2_utm import wgs84_2_utm
        assert callable(wgs84_2_utm)

    def test_function_has_docstring(self):
        """Test that function has documentation."""
        from iwfm.gis.wgs84_2_utm import wgs84_2_utm

        assert wgs84_2_utm.__doc__ is not None
        assert 'utm' in wgs84_2_utm.__doc__.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
