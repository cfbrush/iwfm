# flip_y.py
# multiply y values by -1 to flip image
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

'''Multiply y values by -1 to flip image.'''

def flip_y(dataset):
    '''Multiply y values by -1 to flip image.

    Parameters
    ----------
    dataset : list of lists
        [[x,y,value], [x,y,value], ...]

    Returns
    -------
    dataset : list of lists
        [[x,y,value], [x,y,value], ...]
    '''
    for item in dataset:
        item[1] = item[1] * -1

    return dataset

    