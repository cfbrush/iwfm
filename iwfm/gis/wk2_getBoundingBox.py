# wk2_getBoundingBox.py
# Get bounding polygon
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


'''Get WKT object bounding box.'''

def wk2_getBoundingBox(wkt):
    '''Get WKT object bounding box.

    Parameters
    ----------
    wkt : WKT object

    Return
    ------
    poly : bounding box
    '''
    from osgeo import ogr

    poly = ogr.CreateGeometryFromWkt(wkt)

    return poly
