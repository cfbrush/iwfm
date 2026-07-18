# density_plot.py
# Reads a shapefile and writes it as an image
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

'''Read a shapefile and writes it as an image.'''

import shapefile  # pyshp
import random


from iwfm.gis.world2screen import world2screen

def density_plot(infile,fieldname,iwidth=600,iheight=400,
    denrat=100,savename=None):
    '''Read a shapefile and write it as an image.

    Parameters
    ----------
    infile : str
        source shapefile name

    fieldname : str
        field name for shading

    iwidth : int, default=600
        image width in pixels

    iheight : int, default=400
        image height in pixels

    denrat : int, default=100
        density retio

    savename : str, default=None
        image destination file name (None = not saved)

    Returns
    -------
    nothing
    '''
    from PIL import Image, ImageDraw
    from shapely.geometry import Point, Polygon

    with shapefile.Reader(infile) as inShp:
        val_index = None
        for i, f in enumerate(inShp.fields):  # Get field index
            if f[0] == fieldname:
                val_index = i - 1  # Account for the Deletion Flag field

        dots = []
        for shaperec in inShp.iterShapeRecords():
            value = shaperec.record[val_index]  # get value from field <fieldname>
            density = value / denrat
            found = 0
            poly = Polygon(shaperec.shape.points)
            while found < density:
                minx, miny, maxx, maxy = shaperec.shape.bbox
                x = random.uniform(minx, maxx)
                y = random.uniform(miny, maxy)
                if poly.contains(Point(x, y)):
                    dots.append((x, y))
                    found += 1

        img = Image.new('RGBA', (iwidth, iheight), (255, 255, 255, 255))
        draw = ImageDraw.Draw(img)

        for dot in dots:  # red dots
            x, y = world2screen(inShp.bbox, iwidth, iheight, *dot)
            draw.rectangle([x - 1, y - 1, x + 1, y + 1], fill=(255, 0, 0, 255))

        for shp in inShp.iterShapes():  # black lines for shape boundaries
            pixels = []
            for p in shp.points:
                pixel = world2screen(inShp.bbox, iwidth, iheight, *p)
                pixels.append(tuple(pixel))
            draw.line(pixels, fill=(0, 0, 0, 255))

    if savename:
        img.save(savename)

