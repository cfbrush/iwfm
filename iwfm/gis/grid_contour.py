# grid_contour.py
# Use GDAL and OGR to create a contour shapefile
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


def grid_contour(source, target):
    '''Use GDAL and OGR to create a contour shapefile.

    Parameters
    ----------
    source : str
        input shapefile name

    target : str
        output shapefile name

    Returns
    -------
    nothing
    '''
    from osgeo import ogr
    from osgeo import gdal

    if target[-4:] != '.shp':
        target += '.shp'
    ogr_driver = ogr.GetDriverByName('ESRI Shapefile')
    ogr_ds = ogr_driver.CreateDataSource(target)
    ogr_lyr = ogr_ds.CreateLayer(target, geom_type=ogr.wkbLineString25D)
    field_defn = ogr.FieldDefn('ID', ogr.OFTInteger)
    ogr_lyr.CreateField(field_defn)
    field_defn = ogr.FieldDefn('ELEV', ogr.OFTReal)
    ogr_lyr.CreateField(field_defn)

    # gdal.ContourGenerate() arguments:
    #   Band srcBand,
    #   double contourInterval,
    #   double contourBase,
    #   double[] fixedLevelCount,
    #   int useNoData,
    #   double noDataValue,
    #   Layer dstLayer,
    #   int idField,
    #   int elevField

    ds = gdal.Open(source)
    gdal.ContourGenerate(ds.GetRasterBand(1), 400, 10, [], 0, 0, ogr_lyr, 0, 1)

    return
    
