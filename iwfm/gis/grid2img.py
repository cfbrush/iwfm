# grid2img.py
# Convert an ASCII DEM to an image
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


def grid2img(source, target):
    '''Convert an ASCII DEM to an image.

    Parameters
    ----------
    source : str
        ASCII DEM file name

    target : str
        output image file name

    Returns
    -------
    nothing
    '''
    import numpy as np
    from PIL import Image, ImageOps  # pip install pillow

    arr = np.loadtxt(source, skiprows=6)  
    im = Image.fromarray(arr).convert('RGB')
    im = ImageOps.equalize(im)  # Enhance the image: equalize and increase contrast
    im = ImageOps.autocontrast(im)
    im.save(target)
    return
