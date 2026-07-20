# stretch.py
# Performs a histogram stretch on a gdal_array array image
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


'''Perform a histogram stretch on a gdal_array array image.'''

def stretch(a):
    '''Perform a histogram stretch on a gdal_array array image.

    Parameters
    ----------
    a : GDAL array object

    Returns
    -------
    a : GDAL array object
    '''
    import operator
    from osgeo import gdal_array
    import functools
    import iwfm

    h = iwfm.histogram_array(a)
    lut = []
    for b in range(0, len(h), 256):
        # step size
        step = functools.reduce(operator.add, h[b : b + 256]) / 255
        # create equalization lookup table
        n = 0
        for i in range(256):
            lut.append(n / step)
            n = n + h[i + b]
    gdal_array.numpy.take(lut, a, out=a)
    return a
