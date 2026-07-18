# img_threshold.py
# Threshold an image to black and white
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


'''Threshold an image to black and white.'''

def img_threshold(source, target):
    '''Threshold an image to black and white.

    Parameters
    ----------
    source : str
        image file name

    target : str
        output image file name

    Returns
    -------
    nothing
    '''
    from osgeo import gdal_array as gdal_array

    srcArr = gdal_array.LoadFile(source)  # Load the image into numpy using gdal
    
    # Split the histogram into 20 bins as our classes
    classes = gdal_array.numpy.histogram(srcArr, bins=2)[1]  

    lut = [[255, 0, 0], [0, 0, 0], [255, 255, 255]]  # color lookup table (lut)

    start = 1  # Starting value for classification
    # Set up the output image
    rgb = gdal_array.numpy.zeros((3,srcArr.shape[0],srcArr.shape[1],),
        gdal_array.numpy.float32)  
    for i in range(len(classes)):  # Process all classes and assign colors
        mask = gdal_array.numpy.logical_and(start <= srcArr, srcArr <= classes[i])
        for j in range(len(lut[i])):
            rgb[j] = gdal_array.numpy.choose(mask, (rgb[j], lut[i][j]))
        start = classes[i] + 1
    gdal_array.SaveArray(
        rgb.astype(gdal_array.numpy.uint8), target, format='GTIFF', prototype=source
    )
    return
    