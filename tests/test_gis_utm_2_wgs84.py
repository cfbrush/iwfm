# test_gis_utm_2_wgs84.py
# Tests for gis/utm_2_wgs84.py - Reproject from UTM to WGS84 geographic coordinates
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


class TestUtm2Wgs84:
    """Tests for utm_2_wgs84 function."""

    def test_returns_tuple(self):
        """Test that function returns a tuple of 3 values (lon, lat, altitude)."""
        from iwfm.gis.utm_2_wgs84 import utm_2_wgs84

        result = utm_2_wgs84(11, 385000, 3770000)

        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_returns_lon_lat_altitude_order(self):
        """Test that return order is (lon, lat, altitude)."""
        from iwfm.gis.utm_2_wgs84 import utm_2_wgs84

        # UTM for LA area: Zone 11, ~385000E, ~3770000N
        lon, lat, alt = utm_2_wgs84(11, 385000, 3770000)

        # Longitude should be negative (Western hemisphere)
        assert lon < 0
        # Latitude should be positive (Northern hemisphere)
        assert lat > 0
        # Altitude should be 0
        assert alt == 0

    def test_los_angeles_coordinates(self):
        """Test conversion of Los Angeles UTM coordinates."""
        from iwfm.gis.utm_2_wgs84 import utm_2_wgs84

        zone = 11
        easting = 385000
        northing = 3770000

        lon, lat, alt = utm_2_wgs84(zone, easting, northing)

        # Should be approximately -118°, 34°
        assert -119 < lon < -117
        assert 33 < lat < 35
        assert alt == 0

    def test_zone_as_string(self):
        """Test that zone can be passed as string."""
        from iwfm.gis.utm_2_wgs84 import utm_2_wgs84

        # Function should convert zone to int
        lon, lat, alt = utm_2_wgs84('11', 385000, 3770000)

        assert isinstance(lon, float)
        assert isinstance(lat, float)

    def test_northern_hemisphere_detection(self):
        """Test automatic hemisphere detection for northern hemisphere."""
        from iwfm.gis.utm_2_wgs84 import utm_2_wgs84

        # Positive northing should be treated as northern hemisphere
        lon, lat, alt = utm_2_wgs84(11, 500000, 4000000)

        # Should be in northern hemisphere
        assert lat > 0

    def test_round_trip_with_wgs84_2_utm(self):
        """Test round-trip conversion with wgs84_2_utm."""
        from iwfm.gis.utm_2_wgs84 import utm_2_wgs84
        from iwfm.gis.wgs84_2_utm import wgs84_2_utm

        original_lon, original_lat = -118.2437, 34.0522

        # Convert to UTM
        easting, northing, _ = wgs84_2_utm(original_lon, original_lat)

        # Get zone from the conversion
        from iwfm.gis.get_utm_zone import get_utm_zone
        zone_number = get_utm_zone(original_lon)

        # Convert back
        lon, lat, alt = utm_2_wgs84(zone_number, easting, northing)

        # Should be close to original
        assert abs(lon - original_lon) < 0.001
        assert abs(lat - original_lat) < 0.001


class TestUtm2Wgs84Imports:
    """Tests for utm_2_wgs84 imports."""

    def test_import_from_gis(self):
        """Test import from iwfm.gis."""
        from iwfm.gis import utm_2_wgs84
        assert callable(utm_2_wgs84)

    def test_import_directly(self):
        """Test direct module import."""
        from iwfm.gis.utm_2_wgs84 import utm_2_wgs84
        assert callable(utm_2_wgs84)

    def test_function_has_docstring(self):
        """Test that function has documentation."""
        from iwfm.gis.utm_2_wgs84 import utm_2_wgs84

        assert utm_2_wgs84.__doc__ is not None
        assert 'utm' in utm_2_wgs84.__doc__.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
