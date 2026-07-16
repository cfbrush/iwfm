# img_classify.py
# Classifies a remotely sensed image
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


def img_classify(source, target):
    ''' img_classify() - Classify a remotely sensed image
    
    Parameters
    ----------
    source : str
        imput image file name

    target : str
        output file name

    Returns
    -------
    nothing

    '''
    from osgeo import gdal_array as gdal_array

    srcArr = gdal_array.LoadFile(source)  # Load the image into numpy using gdal
    
    # Split the histogram into 20 bins as our classes
    classes = gdal_array.numpy.histogram(srcArr, bins=20)[1]

    # Color look-up table (LUT) - must be len(classes)+1, specified as R, G, B tuples
    lut = [
        [255, 0, 0],
        [191, 48, 48],
        [166, 0, 0],
        [255, 64, 64],
        [255, 115, 115],
        [255, 116, 0],
        [191, 113, 48],
        [255, 178, 115],
        [0, 153, 153],
        [29, 115, 115],
        [0, 99, 99],
        [166, 75, 0],
        [0, 204, 0],
        [51, 204, 204],
        [255, 150, 64],
        [92, 204, 204],
        [38, 153, 38],
        [0, 133, 0],
        [57, 230, 57],
        [103, 230, 103],
        [184, 138, 0],
    ]
    start = 1  # Starting value for classification

    # Set up the RGB color JPEG output image
    rgb = gdal_array.numpy.zeros(
        (
            3,
            srcArr.shape[0],
            srcArr.shape[1],
        ),
        gdal_array.numpy.float32,
    )
    for i in range(len(classes)):  # Process all classes and assign colors
        mask = gdal_array.numpy.logical_and(start <= srcArr, srcArr <= classes[i])
        for j in range(len(lut[i])):
            rgb[j] = gdal_array.numpy.choose(mask, (rgb[j], lut[i][j]))
        start = classes[i] + 1

    # Save the image
    output = gdal_array.SaveArray(
        rgb.astype(gdal_array.numpy.uint8), target, format="JPEG"
    )
    output = None  # noqa: F841  (releasing the ref flushes the GDAL dataset to disk)
    return
