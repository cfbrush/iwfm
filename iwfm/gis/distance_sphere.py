# distance_sphere.py
# Distance between two lat-lon points on a sphere
# Copyright (C) 2020-2021 Hydrolytics LLC
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


def distance_sphere(p1, p2, units="km"):
    '''distance_sphere() uses the Haversine formula to calculate the
    distance between two (lat,lon) points on a sphere.
    p1 = [lat1,lon1], p2 = [lat2,lon2] in degrees
    units = "km","mi" or "ft"'''
    import math

    lat1 = p1[0]
    lon1 = p1[1]
    lat2 = p2[0]
    lon2 = p2[1]
    lat_dist = math.radians(lat1 - lat2)
    lon_dist = math.radians(lon1 - lon2)
    lon1_rad = math.radians(lat1)
    lon2_rad = math.radians(lat2)
    a = math.sin(lon_dist / 2) ** 2 + math.sin(lat_dist / 2) ** 2 * math.cos(
        lon1_rad
    ) * math.cos(lon2_rad)
    c = 2 * math.asin(math.sqrt(a))
    if units == "mi":
        distance = c * 3959  # miles
    elif units == "ft":
        distance = c * 2.0902e7  # feet
    else:  # units == "km"
        distance = c * 6371  # kilometers
    return distance