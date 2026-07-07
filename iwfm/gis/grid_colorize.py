# grid_colorize.py
# Convert an ASCII DEM to an image and colorize using a heat-map color ramp
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

import colorsys
import numpy as np


def grid_colorize(source, target):
    ''' grid_colorize() - Convert an ASCII DEM to an image and colorize
        using a heat-map color ramp

    Parameters
    ----------
    source : str
        ASCII DEM input file name

    target : str
        output file name

    Returns
    -------
    nothing

    '''
    from PIL import Image, ImageOps

    arr = np.loadtxt(source, skiprows=6)  # Load the ASCII DEM into a numpy array
    im = Image.fromarray(arr).convert("L")  # Convert the numpy array to a PIL image
    im = ImageOps.equalize(im)  # Enhance the image
    im = ImageOps.autocontrast(im)
    palette = []  # Begin building our color ramp
    # Hue, Saturaction, Value
    # color space
    h = 0.67
    s = 1
    v = 1
    # Step through colors from: blue-green-yellow-orange-red.
    # Blue=low elevation, Red=high-elevation
    step = h / 256.0
    for _ in range(256):
        rp, gp, bp = colorsys.hsv_to_rgb(h, s, v)
        r = int(rp * 255)
        g = int(gp * 255)
        b = int(bp * 255)
        palette.extend([r, g, b])
        h -= step
    im.putpalette(palette)  # Apply the palette to the image
    im.save(target)
    return
