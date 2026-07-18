# get_XYvalues.py
# Create X, Y, values vectors from a dataset
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

'''Create X, Y, values vectors from a dataset.'''

def get_XYvalues(dataset):
    '''Create a colored image map representing groundwater data.

    Parameters
    ----------
    dataset : list of lists
        A list containing tuples of three values (x, y, value), representing the x and y coordinates of each
        data point along with their corresponding values.

    Returns
    -------
    X, Y, values: numpy arrays
        numpy arrays containing x, y, and value
    '''
    import numpy as np

    X, Y, value = [], [], []

    for item in dataset:
        X.append(item[0])
        Y.append(item[1])
        value.append(item[2])

    X = np.array(X)
    Y = np.array(Y)
    values = np.array(value)

    return X, Y, values
    

