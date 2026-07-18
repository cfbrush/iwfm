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


def read_sim_hyd(gwhyd_file):
    '''Read simulated values from one IWFM output hydrograph file into a numpy array.

    Parameters
    ----------
    gwhyd_file : str
        input file name

    Returns
    -------
    gwhyd_sim : numpy.ndarray
        2D array of shape (num_timesteps, num_columns) where
        column 0 is datetime and columns 1..N are hydrograph values
    '''
    import numpy as np
    import iwfm

    with open(gwhyd_file, encoding='utf-8') as f:
        gwhyd_lines = (f.read().splitlines())
    gwhyd_lines = [word.replace('_24:00', ' ') for word in gwhyd_lines]

    temp_sim = []
    for j in range(9, len(gwhyd_lines)):
        items= gwhyd_lines[j].split()
        date_str = items.pop(0)
        try:
            date_dt = iwfm.safe_parse_date(date_str, f'{gwhyd_file} line {j+1}')
        except ValueError as e:
            raise ValueError(f"Error reading {gwhyd_file} line {j+1}: {str(e)}") from e
        temp = [date_dt]                   # date
        alist = [float(x) for x in items]       # values to floats
        temp.extend(alist)
        temp_sim.append(temp)

    gwhyd_sim = np.array(temp_sim)

    return gwhyd_sim
