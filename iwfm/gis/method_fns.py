# method_fns.py
# Print methods associated with a shapefile
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

from inspect import getmembers


def method_fns(shpfilename, shpfile, verbose=False):
    '''Return the functions associated with the shpfile library.

    Parameters
    ----------
    shofilename : str
        shapefile name (for printing)

    shpfile : PyShp shapefile object

    verbose : bool, default=False
        True = update command line

    Returns
    -------
    mtds : list
        list of methods      

    '''
    # may only work with shpfile created with PyShp
    mtds = getmembers(shpfile)
    if verbose:
        print(f'\n  Functions for {shpfilename}: {mtds}')
    return mtds
