# sim_smp.py
# Process text lines from a smp-format file into observation data sets
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


'''Process text lines from a smp-format file into observation data sets.'''

def sim_smp(smp_list):
    '''Process text lines from a sample bore (smp) file (smp_list) into observation data sets of [site_id, datetime object, observed value].

    Parameters
    ----------
    smp_list : list
        lines from a smp-format file

    Returns
    -------
    sim_data : list
        each list item contains [date (datetime obj), observation value (float)]

    sim_sites : list
        observation site names
    '''
    from datetime import date
    sim_data, sim_sites = [], []
    for line in smp_list:
        item = line.split()
        if len(item[0]) > 1:
            date_text = item[1].split('/')
            sim_data.append([item[0],date(int(date_text[2]),int(date_text[0]),int(date_text[1])),item[3]])
            if item[0] not in sim_sites:
                sim_sites.append(item[0])
    sim_data.sort( key = lambda l: (l[0], l[1]))
    sim_sites.sort( key = lambda l: (l[0], l[1]))

    return sim_data, sim_sites
