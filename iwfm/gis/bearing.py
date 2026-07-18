# bearing.py
# Bearing between two lat-lon points
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

'''Bearing between two lat-lon points.'''

import math

def bearing(p1, p2):
    '''Return the bearing between two (lat,lon) points p1 = [lat1,lon1], p2 = [lat2,lon2] in degrees Description of algorithm at https://www.mathsisfun.com/sine-cosine-tangent.html.

    Parameters
    ----------
    p1 : list
        point coordinates as floats [latitude,longitude]

    p2 : list
        point coordinates as floats [latitude,longitude]

    Returns
    -------
    bearing : float
        angle between p1 and p2    

    '''
    
    lat1, lon1 = math.radians(p1[0]), math.radians(p1[1])
    lat2, lon2 = math.radians(p2[0]), math.radians(p2[1])
    dlon = lon2 - lon1
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    angle = math.atan2(x, y)
    return (math.degrees(angle) + 360) % 360

