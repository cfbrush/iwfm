# shp_area.py
# Returns area of a polygon for PyShp shapefile
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


def shp_area(polygon):
    ''' shp_area() - Return the geodesic area of a polygon in
        geographic (lon-lat) coordinates

    Parameters
    ----------
    polygon : PyShp polygon shape or GeoJSON-like geometry dict
        polygon in WGS84 lon-lat coordinates

    Returns
    -------
    Polygon area in square meters : float

    '''
    from pyproj import Geod
    from shapely.geometry import shape

    geom = shape(getattr(polygon, '__geo_interface__', polygon))
    area_m2, _ = Geod(ellps='WGS84').geometry_area_perimeter(geom)
    return abs(area_m2)
