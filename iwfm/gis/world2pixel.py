# world2pixel.py
# uses a gdal geomatrix to calculate the pixel location of a geospatial coordinate
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


'''Use a gdal geomatrix to calculate the pixel location of a geospatial coordinate.'''

def world2pixel(geoMatrix, x, y):
    '''Use a GDAL geomatrix to calculate the pixel location of a geospatial coordinate.

    Parameters
    ----------
    geoMatrix :   GDAL geomatrix

    x : float
        x coordonate
    y : float
        y coordonate

    Returns
    -------
    (pixel, line) : (tuple)
        Geospatiol coordinate
    '''
    ulX = geoMatrix[0]
    ulY = geoMatrix[3]
    xDist = geoMatrix[1]
    yDist = geoMatrix[5]
    pixel = int((x - ulX) / xDist)
    line = int((ulY - y) / abs(yDist))
    return (pixel, line)
