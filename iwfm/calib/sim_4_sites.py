# sim_4_sites.py
# Select simulated values at sites with observed values
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


'''Select simulated values at sites with observed values, and return an array of simulated values for these sites and a corresponding list of dates for the simulated values.'''

def sim_4_sites(sim_data, obs_sites):
    '''Select simulated values at sites with observed values, and return an array of simulated values for these sites and a corresponding list of dates for the simulated values.

    Parameters
    ----------
    sim_data : list
        each list item contains [date (datetime obj), observation value (float)]

    sim_sites : list
        observation site names

    Returns
    -------
    sim_dates : list
        list of simulation dates

    sim_values : list
        list of simulation values for sim_dates
    '''
    sim_data.sort( key = lambda l: (l[0], l[1]))
    sim_dates, sim_values, d, v = [], [], [], []
    old_site = sim_data[0][0]                                           # site of first data item
    for item in sim_data:
        if item[0] != old_site:
            if len(d) > 0:
                sim_dates.append(d)
                sim_values.append(v)
            d, v = [], []
            old_site = item[0]
        if item[0] in obs_sites:
            d.append(item[1])        # date
            v.append(float(item[2])) # value
    if len(d) > 0:
        sim_dates.append(d)
        sim_values.append(v)

    return sim_dates, sim_values
