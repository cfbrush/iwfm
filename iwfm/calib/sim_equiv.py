# sim_equiv.py
# Calculate the simulated value for a given date from a simulated hydrograph
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

def sim_equiv(simhyd, date, simhyd_col, round_val = 2, verbose=False):
    '''Calculate the simulated value for a given date from a simulated hydrograph.

    Parameters
    ----------

    simhyd : numpy array
        simulated values

    date : datetime
        date for which to find the simulated value

    simhyd_col : int
        column number in the simulated hydrograph array

    round_val : int, default=2
        number of decimal places to round the result

    verbose : bool, default=False
        True = print intermediate calculations

    Returns
    -------
    sim_head : float
        simulated value for the given date
    '''
    import iwfm.calib as ical
    # calculate the simulated value for this observation
    idx = ical.find_nearest_index(simhyd, date)

    del_date = (simhyd[idx-1][0] - date)/(simhyd[idx-1][0] - simhyd[idx][0])
    del_head = simhyd[idx][simhyd_col] - simhyd[idx-1][simhyd_col]
    sim_head = round(simhyd[idx-1][simhyd_col] + del_head*del_date, round_val)

    return sim_head
