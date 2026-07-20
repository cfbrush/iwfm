# choropleth.py
# Reads a shapefile and writes a choropleth image
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

'''Read a shapefile and write a choropleth image.'''

import shapefile  # pyshp
from iwfm.gis.world2screen import world2screen
import math

def choropleth(infile,fieldname1,fieldname2,iwidth=600,
    iheight=400,denrat=80.0,savename=None):
    '''Read a shapefile and write a choropleth image.

    Parameters
    ----------
    infile : str
        source shapefile name

    fieldname1 : str
        name of field for shading

    fieldname2 : str
        name of field for normalization

    iwidth : int, default=600
        image width in pixels

    iheight : int, default=400
        image height in pixels

    denrat : float, default=80.0
        density ratio

    savename : str, default=None
        image destination file name (None = not saved)

    Returns
    -------
    nothing
    '''
    from PIL import Image, ImageDraw

    inShp = shapefile.Reader(infile)

    img = Image.new('RGB', (iwidth, iheight), (255, 255, 255))  
    draw = ImageDraw.Draw(img)  

    val_index1, val_index2 = None, None
    for i, shape_field in enumerate(inShp.fields):
        if shape_field[0] == fieldname1:
            val_index1 = i - 1  # Account for the Deletion Flag field
        elif shape_field[0] == fieldname2:
            val_index2 = i - 1  # Account for the Deletion Flag field

    # Check if fields were found
    if val_index1 is None:
        raise ValueError(f"Field '{fieldname1}' not found in shapefile {infile}")
    if val_index2 is None:
        raise ValueError(f"Field '{fieldname2}' not found in shapefile {infile}")

    for shp in inShp.shapeRecords():
        # Skip if denominator is zero
        if shp.record[val_index2] == 0:
            continue
        density = shp.record[val_index1] / shp.record[val_index2]
        weight = (min(math.sqrt(density / denrat), 1.0) * 50) 
        R, G, B = int(205 - weight), int(215 - weight), int(245 - weight)
        pixels = []
        for x, y in shp.shape.points:
            (px, py) = world2screen(inShp.bbox, iwidth, iheight, x, y)
            pixels.append((px, py))
        draw.polygon(pixels, outline=(255, 255, 255), fill=(R, G, B))
    if savename:
        img.save(savename)

    