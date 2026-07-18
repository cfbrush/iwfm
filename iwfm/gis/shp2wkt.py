# shp2wkt.py
# Translate shapefile geometry info to WKT format
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


def shp2wkt(shapefile):
    '''Translate shapefile geometry info to WKT format.

    Parameters
    ----------
    shapefile : str
        shapefile name

    Returns
    -------
    wkt : list
        shaefile description in WKT format
    '''
    import iwfm

    shape = iwfm.shp_get_OGR(shapefile)
    layer = shape.GetLayer()
    feature = layer.GetNextFeature()
    geom = feature.GetGeometryRef()
    return geom.ExportToWkt()
