# iwfm_read_gw_params.py
# read IWFM simulation groundwater file groundwater parameters
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


def iwfm_read_gw_params(gw_file, node_coords=None):
    '''Read an IWFM Simulation Groundwater file and return a list of parameters.

    Parameters
    ----------
    gw_file : str
        IWFM Simulation Groundwater file name

    Returns
    -------
    params : list
        A list containing parameter values. It consists of 13 sublists, each representing a different parameter.


    '''
    import iwfm

    iwfm.file_test(gw_file)

    gw_files, node_id, layers, Kh, Ss, Sy, Kq, Kv, init_cond, units, hydrographs, factxy = iwfm.iwfm_read_gw(gw_file, node_coords=node_coords)
    if not Kh:
        return []   # parametric grid file and no node_coords given — parameters not available
    data = [Kh, Ss, Sy, Kq, Kv, init_cond]

    return data
