# hillshade.py
# Convert array to hillshade
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


'''Convert array to hillshade for a city Source: http://geoexamples.blogspot.com.br/2014/03/shaded-relief-images-using-gdal-python.html.'''

def hillshade(array, azimuth, angle_altitude):
    '''Convert array to hillshade for a city Source: http://geoexamples.blogspot.com.br/2014/03/shaded-relief-images-using-gdal-python.html.

    Parameters
    ----------
    array : list
      Array of [x,y] floats

    azimuth : float
      Hillshade azimuth

    angle_altitude : float
      Hillshade sun angle

    Return
    ------
    numpy array:  hillshade
    '''
    import numpy as np

    x, y = np.gradient(array)
    slope = np.pi / 2.0 - np.arctan(np.sqrt(x * x + y * y))
    aspect = np.arctan2(-x, y)
    azimuthrad = azimuth * np.pi / 180.0
    altituderad = angle_altitude * np.pi / 180.0
    shaded = np.sin(altituderad) * np.sin(slope) + np.cos(altituderad) * np.cos(slope) * np.cos(azimuthrad - aspect)
    return 255 * (shaded + 1) / 2
