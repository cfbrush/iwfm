# shp_type_txt.py
# Returns text string of shape type for PyShp shapefile
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


def shp_type_txt(shp):
    '''Return a standard text string of the shape type for a PyShp shapefile.

    Parameters
    ----------
    sho : PyShp shapefile object

    Returns
    -------
    shape type : str
    '''
    from iwfm.gis.shp_type import shp_type

    type = shp_type(shp)
    if type == 1:
        return 'POINT'
    elif type == 3:
        return 'LINE'
    elif type == 5:
        return 'POLYGON'
    elif type == 8:
        return 'MULTIPOINT'
    elif type == 11:
        return 'POINTZ'
    elif type == 13:
        return 'POLYLINEZ'
    elif type == 15:
        return 'POLYGONZ'
    elif type == 18:
        return 'MULTIPOINTZ'
    elif type == 21:
        return 'POINTM'
    elif type == 23:
        return 'POLYLINEM'
    elif type == 25:
        return 'POLYGONM'
    elif type == 28:
        return 'MULTIPOINTM'
    elif type == 31:
        return 'MULTIPATCH'
    else:
        return 'NULL'
