# img_2_array.py
# Converts a Python Imaging Library array to a gdal_array image
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


def img_2_array(img):
    '''Convert a Python Imaging Library array to a gdal_array image.

    Parameters
    ----------
    img : image as PIL array

    Returns
    -------
    a : image as gdal_array
    '''
    from osgeo import gdal_array as gdal_array

    a = gdal_array.numpy.fromstring(img.tobytes(), 'b')
    a.shape = img.im.size[1], img.im.size[0]
    return a
