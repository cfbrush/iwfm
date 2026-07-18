# img_clip.py
# Clips a raster file to a shapefile clipping mask
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


'''Clips a raster file to a shapefile clipping mask.'''

def img_clip(raster, clipshape, outfile):
    '''Clip a raster file to a shapefile clipping mask.

    Parameters
    ----------
    raster : str
        raster image file name

    clipshape : str
        shapefile name

    outfile : str
        image output file name

    Returns
    -------
    nothing
    '''
    from osgeo import gdal_array
    from osgeo import gdal
    import shapefile  # pyshp
    from PIL import Image, ImageDraw  # pillow
    import iwfm.gis as igis

    if clipshape[-4:] != '.shp':
        clipshape += '.shp'
    if outfile[-4:] != '.tif':
        outfile += '.tif'

    # Load the source data as a gdal_array array
    srcArray = gdal_array.LoadFile(raster)  

    # Also load as a gdal image to get geotransform (world file) info
    srcImage = gdal.Open(raster)
    geoTrans = srcImage.GetGeoTransform()
    r = shapefile.Reader(clipshape)  # Use pyshp to open the shapefile

    # Convert the layer extent to image pixel coordinates
    minX,minY,maxX,maxY = r.bbox
    ulX, ulY = igis.world2pixel(geoTrans, minX, maxY)
    lrX, lrY = igis.world2pixel(geoTrans, maxX, minY)

    pxWidth = int(lrX - ulX)  # Calculate the pixel size of the new image
    pxHeight = int(lrY - ulY)
    clip = srcArray[:, ulY:lrY, ulX:lrX]

    # Create a new geomatrix for the image to contain georeferencing data
    geoTrans = list(geoTrans)
    geoTrans[0] = minX
    geoTrans[3] = maxY

    pixels = [igis.world2pixel(geoTrans, p[0], p[1]) for p in r.shape(0).points]
    rasterPoly = Image.new('L', (pxWidth, pxHeight), 1)

    # Create a blank image in PIL to draw the polygon.
    rasterize = ImageDraw.Draw(rasterPoly)
    rasterize.polygon(pixels, 0)
    mask = igis.img_2_array(rasterPoly)  # Convert the PIL image to a NumPy array

    # Clip the image using the mask
    clip = gdal_array.numpy.choose(mask, (clip, 0)).astype(gdal_array.numpy.uint8)  

    # Save ndvi as tiff
    output = gdal_array.SaveArray(clip, outfile, format='GTiff', prototype=raster)

    output = None  # noqa: F841  (releasing the ref flushes the GDAL dataset to disk)
    return
