# distance_ellipse.py
# Distance between two lat-lon points on an ellipse
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

def distance_ellipse(p1, p2, units='m'):
    '''Use the Vincenty formula to calculate the distance between two (lat,lon) points on an ellipsoid Earth.

    Vincenty formula at https://en.wikipedia.org/wiki/Vincenty%27s_formulae

    Parameters
    ----------
    p1 : list
        point coordinates as floats [latitude,longitude]

    p2 : list
        point coordinates as floats [latitude,longitude]

    units : str, default='m'
        units, from 'm', 'km','mi' or 'ft'

    Returns
    -------
    distance : float
        distance between p1 and p2
    '''

    if not (isinstance(p1, list) and isinstance(p2, list) and len(p1) == 2 and len(p2) == 2):
        raise ValueError("Both p1 and p2 must be lists with two elements each [latitude, longitude]")
    
    lat1, lon1 = p1[0], p1[1]
    lat2, lon2 = p2[0], p2[1]
    # Ellipsoid Parameters
    # Example is NAD83
    a = 6378137  # semi-major axis
    f = 1 / 298.257222101  # inverse flattening
    b = abs((f * a) - a)  # semi-minor axis
    L = math.radians(lat2 - lat1)
    U1 = math.atan((1 - f) * math.tan(math.radians(lon1)))
    U2 = math.atan((1 - f) * math.tan(math.radians(lon2)))
    sinU1 = math.sin(U1)
    cosU1 = math.cos(U1)
    sinU2 = math.sin(U2)
    cosU2 = math.cos(U2)
    lam = L

    for _ in range(100):
        sinLam = math.sin(lam)
        cosLam = math.cos(lam)
        sinSigma = math.sqrt(
            (cosU2 * sinLam) ** 2 + (cosU1 * sinU2 - sinU1 * cosU2 * cosLam) ** 2
        )
        if sinSigma == 0:
            return 0.0  # coincident points
        cosSigma = sinU1 * sinU2 + cosU1 * cosU2 * cosLam
        sigma = math.atan2(sinSigma, cosSigma)
        sinAlpha = cosU1 * cosU2 * sinLam / sinSigma
        cosSqAlpha = 1 - sinAlpha ** 2
        cos2SigmaM = cosSigma - 2 * sinU1 * sinU2 / cosSqAlpha
        if math.isnan(cos2SigmaM):
            cos2SigmaM = 0  # equatorial line
        C = f / 16 * cosSqAlpha * (4 + f * (4 - 3 * cosSqAlpha))
        LP = lam
        lam = L + (1 - C) * f * sinAlpha * (
            sigma
            + C
            * sinSigma
            * (cos2SigmaM + C * cosSigma * (-1 + 2 * cos2SigmaM * cos2SigmaM))
        )
        if abs(lam - LP) <= 1e-12:
            break
    uSq = cosSqAlpha * (a ** 2 - b ** 2) / b ** 2
    A = 1 + uSq / 16384 * (4096 + uSq * (-768 + uSq * (320 - 175 * uSq)))
    B = uSq / 1024 * (256 + uSq * (-128 + uSq * (74 - 47 * uSq)))
    deltaSigma = (
        B
        * sinSigma
        * (
            cos2SigmaM
            + B
            / 4
            * (
                cosSigma * (-1 + 2 * cos2SigmaM * cos2SigmaM)
                - B
                / 6
                * cos2SigmaM
                * (-3 + 4 * sinSigma * sinSigma)
                * (-3 + 4 * cos2SigmaM * cos2SigmaM)
            )
        )
    )
    s = b * A * (sigma - deltaSigma)  # distance in meters
    if units == 'ft':
        return s * 3.28084
    elif units == 'km':
        return s / 1000
    elif units == 'mi':
        return s * 0.000621371
    else:
        return s
