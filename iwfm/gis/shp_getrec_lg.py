# shp_getrec_lg.py
# Returns a record as a string for a PyShp shapefile
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


'''Return a record as a string.'''

def shp_getrec_lg(f, i):
    '''Return a record as a string.

    Works better than shp_getrec() for large DBF files

    Parameters
    ----------
    f : PyShp shapefile

    i : int
        record number

    Returns
    -------
    Specified record : str
    '''
    return f.iterRecord(i)
