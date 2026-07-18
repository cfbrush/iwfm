# interp_val.py
# Return the simulated value that corresponds to the observation date.
# Copyright (C) 2020-2023 University of California
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


'''Return the simulated value that corresponds to the observation date.'''

def interp_val(obs_date,early_date,early_val,late_date,late_val):
    '''Return the simulated value that corresponds to the observation date.

    Parameters
    ----------
    obs_date : datetime object
        observation date

    early_date, early_val : datetime object, float
        simulation date and simulated value before obs_date

    late_date, late_val : datetime object, float
        simulation date and simulated value after obs_date

    Returns
    -------
    return value : float
        simulated value interpolated to obs_date
    '''
    if early_date == obs_date:
        return early_val
    elif late_date == obs_date:
        return late_val
    else:    # interpolate sim to obs date
        return early_val + (late_val - early_val) * (obs_date - early_date).days/(late_date - early_date).days

