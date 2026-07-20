# setrot.py
# from setrot() by  C. Deutsch, September 1989
# Sets up the matrix to transform cartesian coordinates to coordinates
# accounting for angles and anisotropy (see GSLIB manual for a detailed
# definition)
# Copyright (C) 2020-2021 University of California
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


'''Set up the matrix to transform cartesian coordinates to coordinates accounting for angles and anisotropy (from setrot() by C.'''

def setrot(ang1, ang2, ang3, anis1, anis2):
    '''Set up the matrix to transform cartesian coordinates to coordinates accounting for angles and anisotropy (from setrot() by C.

    Deutsch, September 1989. See GSLIB manual for a detailed definition)

    Parameters
    ----------
    ang1 : float
        Angle 1

    ang2 : float
        Angle 2

    anis1 : float
        Anisotropy 1

    anis2 : float
        Anisotropy 2

    Returns
    -------
    rotmat : list of floats
        Rotation matrix
    '''
    import math

    deg2rad = math.pi / 180
    epsilon = 1.0e-10

    if 0 <= ang1 < 270:
        alpha = (90.0 - ang1) * deg2rad
    else:
        alpha = (450.0 - ang1) * deg2rad
    beta = -1 * ang2 * deg2rad
    theta = ang3 * deg2rad

    # Get the required sines and cosines:
    sina = math.sin(alpha)
    sinb = math.sin(beta)
    sint = math.sin(theta)
    cosa = math.cos(alpha)
    cosb = math.cos(beta)
    cost = math.cos(theta)

    # Construct the rotation matrix
    afac1 = 1.0 / max(anis1, epsilon)
    afac2 = 1.0 / max(anis2, epsilon)

    rotmat = []  # Note from Deutsch: only one rotation matrix
    temp = []
    temp.append(cosb * cosa)
    temp.append(cosb * sina)
    temp.append(-sinb)
    rotmat.append(temp)
    temp = []
    temp.append(afac1 * (-cost * sina + sint * sinb * cosa))
    temp.append(afac1 * (cost * cosa + sint * sinb * sina))
    temp.append(afac1 * (sint * cosb))
    rotmat.append(temp)
    temp = []
    temp.append(afac2 * (sint * sina + cost * sinb * cosa))
    temp.append(afac2 * (-sint * cosa + cost * sinb * sina))
    temp.append(afac2 * (cost * cosb))
    rotmat.append(temp)

    return rotmat
