# img_diff.py
# Perform a simple difference image change detection on matched 'before' and 'after' images
# Copyright (C) 2020-2021 Hydrolytics LLC
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


def img_diff(img1, img2, outfile):
    """img_diff() Perform a simple difference image change detection on matched 'before' and 'after' images"""
    from osgeo import gdal_array as gdal_array
    import numpy as np

    # Load before and after into arrays
    ar1 = gdal_array.LoadFile(img1).astype(np.int8)
    ar2 = gdal_array.LoadFile(img2)[1].astype(np.int8)
    diff = ar2 - ar1  # Perform a simple array difference on the images
    classes = np.histogram(diff, bins=5)[
        1
    ]  # Set up our classification scheme to try and isolate significant changes
    # The color black is repeated to mask insignificant changes
    lut = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 255, 0], [255, 0, 0]]
    start = 1  # Starting value for classification
    rgb = np.zeros(
        (
            3,
            diff.shape[0],
            diff.shape[1],
        ),
        np.int8,
    )  # Set up the output image
    for i in range(len(classes)):  # Process all classes and assign colors
        mask = np.logical_and(start <= diff, diff <= classes[i])
        for j in range(len(lut[i])):
            rgb[j] = np.choose(mask, (rgb[j], lut[i][j]))
        start = classes[i] + 1
    output = gdal_array.SaveArray(
        rgb, outfile, format="GTiff", prototype=img2
    )  # Save the output image
    output = None