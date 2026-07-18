# shp_getrec_fn.py
# Returns the item in column of field_name for record i for a PyShp shapefile
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


'''Return the item in column of field_name for record i for a PyShp shapefile.'''

def shp_getrec_fn(f, i, field_name):
    '''Return the item in the column specified by field_name for record i for a PyShp shapefile.

    Parameters
    ----------
    f : Shapefile object

    i : int
        record number

    field_name : str
        shapefile field name

    Returns:
    The requested item (undetermined type)
    '''
    from iwfm.shp_fieldnames import shp_fieldnames
    from iwfm.gis.shp_getrec import shp_getrec

    field_names = shp_fieldnames(f)
    record = shp_getrec(f, i)
    position = field_names.index(field_name)
    return record[position]
