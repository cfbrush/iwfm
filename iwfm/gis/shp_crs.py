# shp_crs.py
# Return shapefile coordinate reference system
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


'''Return shapefile coordinate reference system.'''

def shp_crs(filename):
    '''Return the shapefile coordinate reference system from the sidecar .prj file.

    Parameters
    ----------
    filename : str
        shapefile name

    Returns
    -------
    c : pyproj.CRS or None
        shapefile coordinate reference system (None if no .prj file)
    '''
    from pathlib import Path
    from pyproj import CRS

    prj = Path(filename).with_suffix('.prj')
    if not prj.is_file():
        return None
    return CRS.from_wkt(prj.read_text())
