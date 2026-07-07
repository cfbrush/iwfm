# contour2png.py
# Draw an entire contour shapefile to a PNG image
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

import shapefile  # pyshp
from PIL import Image, ImageDraw

def contour2png(source, target, iwidth=800, iheight=600):
    ''' contour2png() - Draw an entire contour shapefile to a PNG image
    
    Parameters
    ----------
    source : str
        input shapefile name

    target : str
        output PNG file name

    iwidth : int, default=800
        image width in pixels

    iheight : int, default=600
        image height in pixels

    Returns
    -------
    nothing

    '''

    if source[-4:] != '.shp':
        source += '.shp'
    if target[-4:] != '.png':
        target += '.png'
    with shapefile.Reader(source) as r:  # Open the contour shapefile
        # Setup the world to pixels conversion
        xdist = r.bbox[2] - r.bbox[0]
        ydist = r.bbox[3] - r.bbox[1]
        xratio = iwidth / xdist
        yratio = iheight / ydist
        contours = []
        # Loop through all shapes
        for shape in r.shapes():
            # Loop through all parts
            for i in range(len(shape.parts)):
                pixels = []
                pt = None
                if i < len(shape.parts) - 1:
                    pt = shape.points[shape.parts[i] : shape.parts[i + 1]]
                else:
                    pt = shape.points[shape.parts[i] :]
                for x, y in pt:
                    px = int(iwidth - ((r.bbox[2] - x) * xratio))
                    py = int((r.bbox[3] - y) * yratio)
                    pixels.append([px, py])
                contours.append(pixels)
    # Set up the output canvas and draw the contours in red
    img = Image.new('RGBA', (iwidth, iheight), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    for c in contours:
        draw.line([tuple(pt) for pt in c], fill=(255, 0, 0, 255))
    img.save(target)

