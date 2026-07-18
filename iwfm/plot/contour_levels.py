# contour_levels.py
# Define the contour levels for a contour map.
# Copyright (C) 2023-2024 University of California
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

def contour_levels(Z, no_levels=20, verbose=False):
    '''Define the contour levels for a contour map.

    Parameters
    ----------
    Z : numpy array
        The values to be contoured.

    step_level : int, default = 25
        Step size for contour levels.

    verbose : bool, default = False
        If True, print status messages.

    Returns
    -------
    levels : numpy array
        The contour levels.
    '''

    import numpy as np

    # Define the contour levels
    if Z.max() - Z.min() > 10:
        # set interval for contour levels
        if Z.max() - Z.min() > 500:
            step_level = 50
        elif Z.max() - Z.min() > 200:
            step_level = 20
        elif Z.max() - Z.min() > 100:
            step_level = 10
        else:
            step_level = 5
        min_level = int(Z.min())
        while min_level % step_level != 0:
            min_level -= 1
        max_level = int(Z.max())
        while max_level % step_level != 0:
            max_level += 1
        levels = np.arange(min_level, max_level + step_level, step_level)
    else:
        levels = np.linspace(Z.min(), Z.max(), no_levels)

    return levels