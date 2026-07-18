# par2iwfm.py 
# Use kriging to translate parameter values from pilot points to model nodes.
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


def par2iwfm(A, B):
    '''Implement krige function to create new parameter values.

    Parameters
    ----------
    A : list
        List of tuples representing grid A points. Each tuple contains (id, x, y) coordinates.

    B : list
        List of tuples representing grid B points. Each tuple contains (id, x, y, value) coordinates.

    Returns
    -------
    a_values : list
        List of calculated floats representing values for A in B's grid
    '''
    import iwfm.calib as calib
    import numpy as np

    #  get krige factors and base set values
    krige_factors = calib.krige(A, B)
    values = [val for _, _, _, val in B]
  
    #  convert to numpy arrays for computation
    first_array = np.array(values)
    second_array = np.array(krige_factors)
    
    #  Element-wise matrix multiplication
    a_value_array = first_array * second_array
    a_values = [np.sum(array) for array in a_value_array]

    return a_values

