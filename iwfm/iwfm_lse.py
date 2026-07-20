# iwfm_lse.py
# extract land surface altitude from IWFM stratigraphy information
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


'''Extract land surface elevation from IWFM stratigraphy information.'''

def iwfm_lse(strat):
    '''Extract land surface elevation from IWFM stratigraphy information.

    Parameters
    ----------
    strat : list
        stratigraphy for each model node

    Returns
    -------
    elevation : list
        land surface elevation for each model node
    '''
    elevation = [[i[0], i[1]] for i in strat]  
    # include node no because child models don't contain all nodes
    return elevation
