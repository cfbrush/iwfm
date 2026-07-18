# shp_get_OGR.py
# Open a shapefile with OGR
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


'''Open a shapefile with OGR.'''

def shp_get_OGR(infile, verbose=False):
    '''Open a shapefile with OGR.

    Parameters
    ----------
    infile : str
        name to save info from url

    verbose : bool, default=False
        True = command-line output on

    Returns
    -------
    shape :  shapefile as OGR object
    '''
    from osgeo import ogr

    shape = ogr.Open(infile)
    if verbose:
        print(f'  Opened file \'{infile}\' ')
    return shape
