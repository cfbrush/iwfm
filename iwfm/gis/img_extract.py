# img_extract.py
# Automatically extract features of a threshold image to a shapefile
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


def img_extract(source, target):
    '''Automatically extract features of a threshold image to a shapefile.

    Parameters
    ----------
    source : str
        input file name

    target : str
        ouput file name

    Returns
    -------
    extract : OGR object
        extracted features


    '''
    from osgeo import gdal
    from osgeo import ogr
    from osgeo import osr

    srcDS = gdal.Open(source)
    band = srcDS.GetRasterBand(1)
    mask = band                                     # Force gdal to use the band as a mask

    driver = ogr.GetDriverByName('ESRI Shapefile')  # Set up the output shapefile
    shp = driver.CreateDataSource(target)
    srs = osr.SpatialReference()  # Copy the spatial reference
    srs.ImportFromWkt(srcDS.GetProjectionRef())

    tgtLayer = 'extract'  # OGR layer name
    layer = shp.CreateLayer(tgtLayer, srs=srs)
    fd = ogr.FieldDefn('DN', ogr.OFTInteger)  # Set up the dbf file
    layer.CreateField(fd)
    dst_field = 0
    return gdal.Polygonize(band, mask, layer, dst_field, [], None)
