# simhyd_obs.py
# Read simulated groundwater hydrographs
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


def simhyd_obs(gwhyd_file):
    ''' symhyd_obs() - Read simulated groundwater hydrographs from IWFM file

    Parameters
    ----------
    gwhyd_file : str
        IWFM groundwater hydrograph file name

    Returns
    -------
    simhyd_obs : list
        table of hydrograph information
    
    ''' 

    with open(gwhyd_file, encoding='utf-8') as f:
        gwhyd_lines = f.read().splitlines() 
    gwhyd_lines = [word.replace('_24:00', ' ') for word in gwhyd_lines]

    simhyd_obs = []
    for j in range(9, len(gwhyd_lines)):
        line = gwhyd_lines[j].split()
        for i in range(1, len(line)):
            line[i] = float(line[i])
        simhyd_obs.append(line)
    return simhyd_obs
