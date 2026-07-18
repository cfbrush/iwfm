# get_gw_params.py
# Get nodal coordinates and groundwater parameters from an IWFM simulation
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


def get_gw_params(gw_file):
    '''Get nodal coordinates and groundwater parameters from an IWFM simulation.

    Parameters
    ----------
    gw_file : str
        IWFM Simulation Groundwater file name

    node_file : str
        IWFM Nodes file name

    Returns
    -------
    np.array(coordinates): numpy array
        nodal coordinates

    layers: int
        number o fmodel layers

    Kh, Ss, Sy, Kq, Kv: numpy arrays
        groundwater parameters



    '''
    import iwfm
    import numpy as np

    #  Read all relevant values from Groundwater.dat
    _, _, layers, Kh, Ss, Sy, Kq, Kv, _, _, _, _ = iwfm.iwfm_read_gw(gw_file)
    Kh, Ss, Sy, Kq, Kv = np.array(Kh), np.array(Ss), np.array(Sy), np.array(Kq), np.array(Kv)

    return layers, Kh, Ss, Sy, Kq, Kv
