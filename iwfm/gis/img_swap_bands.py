# img_swap_bands.py
# Reads a TIFF file, swaps two bands, and saves it
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


'''Read a TIFF file, swaps two bands, and saves it.'''

def img_swap_bands(infile, outfile, band1=1, band2=2):
    '''Read a TIFF file, swaps two bands, and saves it.

    Parameters
    ----------
    infile : str
        input image file name

    outfile : str
        output image file name

    band1, band2 : int
        bands to be swapped

    Return
    ------
    nothing
    '''
    
    from osgeo import gdal_array as gdal_array

    arr = gdal_array.LoadFile(infile)
    output = gdal_array.SaveArray(
        arr[[band1, 0, 2], :], outfile, format='GTIFF', prototype=infile
    )
    # prototype copies the georeferencing information to output file
    output = None  # noqa: F841  (releasing the ref flushes the GDAL dataset to disk)
    return
