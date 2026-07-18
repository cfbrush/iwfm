# dd2dms.py
# Converts from degree-minute-second to decimal degrees
# Copyright (C) 2020-2025 University of California
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

import re

def dms2dd(lat, lon):
    '''Convert from degree-minute-second to decimal degrees.

    Parameters
    ----------
    lat : str
        Latitude in DMS format (e.g., "34°3'30"N")

    lon : str
        Longitude in DMS format (e.g., "118°15'0"W")

    Return
    ------
    (lat_dd, lon_dd) : (float, float)
        Decimal latitude and longitude values
    '''

    try:
        lat_deg, lat_min, lat_sec, lat_dir = re.split(r'[^\d\.A-Z]+', lat)
        lon_deg, lon_min, lon_sec, lon_dir = re.split(r'[^\d\.A-Z]+', lon)
    except ValueError:
        raise ValueError("Invalid input format for latitude or longitude")
    lat_dd = float(lat_deg) + float(lat_min) / 60 + float(lat_sec) / (60 * 60)
    lon_dd = float(lon_deg) + float(lon_min) / 60 + float(lon_sec) / (60 * 60)
    if lat_dir == 'S':
        lat_dd *= -1
    if lon_dir == 'W':
        lon_dd *= -1
    return (lat_dd, lon_dd)
