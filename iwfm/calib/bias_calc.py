# bias_calc.py
# calculate bias between two lists of values
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


'''Return the Bias between measured (targets) and simulated (predictions) values.'''

def bias_calc(predictions, targets):
    '''Return the Bias between measured (targets) and simulated (predictions) values.

    Parameters
    ----------
    predictions : list
        simulated values as floats

    targets : list
        observed values as floats

    Returns
    -------
    mean : float
        mean of differences between preditions and targets
    '''
    import numpy as np

    return (np.array(predictions) - np.array(targets)).mean()
