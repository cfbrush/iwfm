# shp_reproject.py
# Reproject a shapefile
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


def shp_reproject(srcName, tgtName, epsg=26910):
    ''' shp_reproject() - Project a shapefile to another shapefile in 
        <spatRef> coordinate system. 

    Parameters
    ----------
    srcName : str
        input shapefile name
    
    tgtName : str
        output shapefile name
    
    epsg : int, default=26910 (NAD 83 UTM 10, CA)
        EPSG projection

    Returns
    -------
    nothing
    
    '''

    import os
    import shutil
    from osgeo import osr
    from osgeo import ogr
    from iwfm.debug.logger_setup import logger

    # Set target spatial reference
    tgt_spatRef = osr.SpatialReference()
    tgt_spatRef.ImportFromEPSG(epsg)

    # Source shapefile
    driver = ogr.GetDriverByName('ESRI Shapefile')
    src = driver.Open(srcName, 0)
    srcLyr = src.GetLayer()
    src_spatRef = srcLyr.GetSpatialRef()  # Source spatial reference

    # Target shapefile - delete if it's already there.
    from pathlib import Path
    if Path(tgtName).exists():
        driver.DeleteDataSource(tgtName)
    tgt = driver.CreateDataSource(tgtName)
    lyrName = str(Path(tgtName).with_suffix(''))
    tgtLyr = tgt.CreateLayer(lyrName, geom_type=ogr.wkbPoint)
    # Layer definition
    featDef = srcLyr.GetLayerDefn()
    # Spatial Transform
    trans = osr.CoordinateTransformation(src_spatRef, tgt_spatRef)
    while srcFeat := srcLyr.GetNextFeature():
        geom = srcFeat.GetGeometryRef()
        geom.Transform(trans)
        feature = ogr.Feature(featDef)
        feature.SetGeometry(geom)
        tgtLyr.CreateFeature(feature)
        feature.Destroy()
        srcFeat.Destroy()
    src.Destroy()
    tgt.Destroy()
    # Create the prj file
    tgt_spatRef.MorphToESRI()  # Convert geometry to ESRI WKT format
    try:
        with open(f'{lyrName}.prj', 'w', encoding='utf-8') as prj:
            prj.write(tgt_spatRef.ExportToWkt())
    except (PermissionError, OSError) as e:
        logger.error(f'Failed to write projection file {lyrName}.prj: {e}')
        raise
    logger.debug(f'Wrote projection file {lyrName}.prj')

    # Just copy dbf contents over rather than rebuild the dbf using the
    # ogr API since we're not changing anything.
    srcDbf = str(Path(srcName).with_suffix('.dbf'))
    tgtDbf = f'{lyrName}.dbf'
    try:
        shutil.copyfile(srcDbf, tgtDbf)
    except (FileNotFoundError, PermissionError, OSError) as e:
        logger.error(f'Failed to copy dbf file {srcDbf} to {tgtDbf}: {e}')
        raise
    logger.debug(f'Copied dbf file {srcDbf} to {tgtDbf}')

    return
