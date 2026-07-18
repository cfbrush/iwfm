# distance_sphere.py
# Distance between two lat-lon points on a sphere
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

import math

def distance_sphere(p1, p2, units='km'):
    '''Use the Haversine formula to calculate the distance between two (lat,lon) points on a sphere.

    p1 = [lat1,lon1], p2 = [lat2,lon2] in degrees units = 'km' (default), 'mi' for miles, or 'ft' for feet

    Parameters
    ----------
    p1 : list
        lat, lon coordinates of a point in degrees

    p2 : list
        lat, lon coordinates of a point in degrees

    units : str, default='km'
        distance units: 'km','mi' or 'ft'

    Returns
    -------
    distance : float
        distance between p1 and p2
    '''

    lat1 = p1[0]
    lon1 = p1[1]
    lat2 = p2[0]
    lon2 = p2[1]
    lat_dist = math.radians(lat2 - lat1)
    lon_dist = math.radians(lon2 - lon1)
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    a = math.sin(lat_dist / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(lon_dist / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    if units == 'ft':
        return c * 2.0902e7
    elif units == 'mi':
        return c * 3959
    else:
        return c * 6371
