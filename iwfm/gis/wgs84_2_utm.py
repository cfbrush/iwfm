# wgs84_2_utm.py
# Reproject from geographic coordinates to UTM
# Copyright (C) 2020-2026 University of California
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


'''Reproject from geographic coordinates to UTM.'''

def wgs84_2_utm(lon, lat):
    '''Reproject a WGS84 shapefile to UTM.

    Parameters
    ----------
    lon : float
        longitude

    lat : float
        latitude

    Returns
    -------
    (easting, northing, altitude) : tuple
        UTM easting, northing, and altitude (0)
    '''
    from iwfm.gis.latlon_2_utm import latlon_2_utm

    easting, northing, zone_number, zone_letter = latlon_2_utm(lat, lon)
    return (easting, northing, 0)
