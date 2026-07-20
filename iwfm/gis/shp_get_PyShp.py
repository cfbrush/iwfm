# shp_get_PyShp.py
# Open a shapefile with PyShp
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


'''Read a shapefile with PyShp.'''

def shp_get_PyShp(infile, verbose=False):
    '''Read a shapefile with PyShp.

    Parameters
    ----------
    infile : str
        input shapefile name

      verbose : bool, default=False
          True = command-line output on 

    Returns
    -------
    shp : PyShp shapefile.Reader
        The caller is responsible for closing it (``shp.close()`` or
        use as a context manager: ``with iwfm.shp_get_PyShp(...) as shp``).
    '''
    import shapefile  # pyshp

    shp = shapefile.Reader(infile)
    if verbose:
        print(f'  Opened shapefile {infile}')
    return shp
