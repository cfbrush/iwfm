# point2geojson.py
# Point to geojson format
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


def point2geojson(point, verbose=False):
    '''Convert a point to geojson format.

    Parameters
    ----------
    point : Point object

    verbose : bool, default=False
        True = command-line output on

    Returns
    -------
    geojs : Point as GeoJSON dict
    '''
    import json

    geojs = {'type': 'Point', 'coordinates': list(point)}
    if verbose:
        print('  GeoJSON Data: ')
        print(json.dumps(geojs, indent=5))
    return geojs
