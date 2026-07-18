# obs_smp.py
# Return observation bore sample info for sites in sim_sites
# Copyright (C) 2020-2026 University of California
# Based on a PEST utility written by John Doherty
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


def obs_smp(obs_lines,sim_sites):
    '''Return observation bore sample info for sites in sim_sites.

    Parameters
    ----------
    obs_lines : list of strings
        observations in smp format

    sim_sites : list of strings
        simulation observation sites

    Returns
    -------
    obs_data : list of strings
        observation data for sites in sim_sites

    obs_sites : list of strings
        observation sites used in simulation

    missing : list of stringz
        observation sites not used in simulation
    '''
    from datetime import date

    missing, obs_data, obs_sites = [], [], []
    for line in obs_lines:
        item = line.split()
        if item[0] in sim_sites:
            date_text = item[1].split('/')
            obs_data.append([item[0],date(int(date_text[2]),int(date_text[0]),int(date_text[1])),item[1]])
            if item[0] not in obs_sites:
                obs_sites.append(item[0])
        else:
            if item[0] not in missing:
                missing.append(item[0])
    obs_data.sort( key = lambda l: (l[0], l[1]))
    obs_sites.sort( key = lambda l: (l[0]))
    #print(f'    {len(obs_sites)} sites in both simulation and observation sets')
    return obs_data, obs_sites, missing
