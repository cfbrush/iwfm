# read_sim_hyds.py
# Read simulated hydrographs from IWFM hydrograph.out file
# Copyright (C) 2020-2026 University of California
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


'''Read simulated hydrographs from IWFM hydrograph.out file.'''

def read_sim_hyds(gwhyd_files):
    '''Read simulated values from multiple IWFM output hydrograph files into numpy arrays.

    Parameters
    ----------
    gwhyd_files : list
        list of input file names

    Returns
    -------
    gwhyd_sim : list
        list with one item of hydrograph values for each input hydrograph file
    '''
    from iwfm.read_sim_hyd import read_sim_hyd

    gwhyd_sim = []

    for k in range(0, len(gwhyd_files)):
        sim_hyd = read_sim_hyd(gwhyd_files[k])
        gwhyd_sim.append(sim_hyd)

    return gwhyd_sim
