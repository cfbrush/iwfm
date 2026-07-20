# qgis_print_geometry.py
# Print QGIS project geometry information
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

'''Print QGIS geometry informatio to screen.'''

from qgis.core import QgsWkbTypes


def qgis_print_geometry(geom):
    '''Print QGIS geometry informatio to screen.

    Parameters
    ----------
    geom : qgis object
        qgis object

    Returns
    -------
    nothing
    '''

    
    geom_SingleType = QgsWkbTypes.isSingleType(geom.wkbType())
    if geom.type() == QgsWkbTypes.PointGeometry:
        # the geometry type can be of single or multi type
        if geom_SingleType:
            x = geom.asPoint()
            print(f'Point: {x}')
        else:
            x = geom.asMultiPoint()
            print(f'MultiPoint: {x}')
    elif geom.type() == QgsWkbTypes.LineGeometry:
        if geom_SingleType:
            x = geom.asPolyline()
            print(f'Line: {x}, length: {geom.length()}')
        else:
            x = geom.asMultiPolyline()
            print(f'MultiLine: {x}, length: {geom.length()}')
    elif geom.type() == QgsWkbTypes.PolygonGeometry:
        if geom_SingleType:
            x = geom.asPolygon()
            print(f'Polygon: {x}, Area: {geom.area()}')
        else:
            x = geom.asMultiPolygon()
            print(f'MultiPolygon: {x}, Area: {geom.area()}')
    else:
        print('Unknown or invalid geometry')
    return
