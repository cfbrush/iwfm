# get_mins.py
# FFind the minimum values of each parameter in a list of lists
# Copyright (C) 2023 University of California
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

def get_mins(dataset):
    '''Find the minimum values of each parameter in a list of lists.

    Parameters
    ----------
    dataset : list
        A list containing lists of values. Usually touples of (x, y, v), representing x and y coordinates along with
        their corresponding values.

    Returns
    -------
    mins : list
        A list containing the minimum value of each parameter in the lists.
    '''
    import math
    
    #  Set each value to positive infinity
    mins = []
    for _ in dataset[0]:
        mins.append(float('+inf'))

    #  Find the minimum value of the x coordinates, y coordinates, and values
    for coords in dataset:
        for i, coord in enumerate(coords):
            if coord < mins[i]:
                mins[i] = coord

    #   Minimums rounded down
    mins = [math.floor(coord) for coord in mins]

    return mins


