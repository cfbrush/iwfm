# find_nearest_index.py
# Finds the index of the value in the first column of the array that is closest 
# to the given value.
# Copyright (C) 2020-2025 University of California
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

'''Find the index of the value in the first column of the array that is closest to the given value.'''

def find_nearest_index(array, value):
    '''Find the index of the value in the first column of the array that is closest to the given value.

    Parameters
    ----------
    array : numpy array
        array of values

    value : float
        value to find in the array

    Returns
    -------
    idx : int
        index of the value in the array                 

    '''

    import numpy as np
    idx = np.abs(array[:, 0] - value).argmin()
    return idx
