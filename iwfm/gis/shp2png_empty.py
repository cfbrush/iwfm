# shp2png_empty.py
# Save a shapefile as a raster with no fill
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


def shp2png_empty(shape, outname, iwidth=400, iheight=600):
    '''Convert a shapefile to a raster and saves as a png file - just the outline with no fills.

    Parameters
    ----------
    shape : shapefile object

    outname  : str
        output file name

    iwidth : int, default=400
        image width in pixels

    iheight : int, default=600
        image height in pixels

    Return
    ------
    nothing
    '''
    from PIL import Image, ImageDraw

    xdist = shape.bbox[2] - shape.bbox[0]
    ydist = shape.bbox[3] - shape.bbox[1]
    xratio = iwidth / xdist
    yratio = iheight / ydist
    pixels = []
    for x, y in shape.shapes()[0].points:
        px = int(iwidth - ((shape.bbox[2] - x) * xratio))
        py = int((shape.bbox[3] - y) * yratio)
        pixels.append([px, py])
    img = Image.new('RGBA', (iwidth, iheight), (255, 255, 255, 255))
    ImageDraw.Draw(img).line([tuple(pt) for pt in pixels], fill=(0, 0, 0, 255))
    img.save(outname)
    return
