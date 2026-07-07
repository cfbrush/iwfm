# shp_fields_print.py
# Print field property strings for a PyShp shapefile
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


def shp_fields_print(f):
    ''' shp_fields_print() - Print the field property strings for a PyShp
        shapefile
    
    Parameters
    ----------
    f : PyShp shapefile object
        shapefile

    Returns
    -------
    nothing

    '''
    from iwfm.gis.shp_fields import shp_fields

    fields = shp_fields(f)
    print("  ['NAME', 'TYPE', LENGTH, PRECISION]")
    for s in fields:
        print(f'  {s}')
    return
