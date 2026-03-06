# get_sim_hyd.py
# Get simulated hydrograph values
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

from iwfm.debug.logger_setup import logger


def get_sim_hyd(nt,file_name,start_date):
    ''' get_sim_hyd() - get simulated hydrograph values and return as a list of lists
        with row=timestep, 1st col=dates and remaining cols=sites, dates as datetime
        objects, everything else as numpy arrays of floats

    Parameters
    ----------
    nt : str
        hydrograph type

    file_name : str
        simulation hydrograph file name

    start_date : datetime object
        start date in

    Returns
    -------
    sim_hyd : array
        simulation hydrograph values

    dates : list of ints
        days since start date for each row of sim_hyd

    '''
    from datetime import datetime
    import numpy as np

    logger.debug(f'get_sim_hyd({nt}): reading {file_name}')
    with open(file_name) as f:
        hyd_lines = f.read().splitlines()
    hyd_index, dates, sim_hyd = 1, [], []
    logger.debug(f'  Read {len(hyd_lines):,} lines from {file_name}')

    while hyd_index < len(hyd_lines) and not hyd_lines[hyd_index][0].isdigit():  # skip to the dates
        hyd_index += 1

    if hyd_index >= len(hyd_lines):
        logger.warning(f'No simulation data found in {file_name} (empty hydrograph file)')
        print(f'  ** Warning: No simulation data found in {file_name}')
        return sim_hyd, dates

    while hyd_index < len(hyd_lines) and hyd_lines[hyd_index][0].isdigit() == True:   # get the dates
        temp = hyd_lines[hyd_index].split()
        date_obj = datetime.strptime(temp[0][:10], '%m/%d/%Y')  # string to datetime
        dates.append((date_obj - start_date).days)  # days since start date

        arr = []
        for i in range(1,len(temp)):
            arr.append(float(temp[i]))
        sim_hyd.append(np.array(arr))
        hyd_index += 1

    ncols = len(sim_hyd[0]) if sim_hyd else 0
    logger.info(f'  {nt}: read {len(dates):,} time steps, {ncols:,} sites from {file_name}')
    return sim_hyd, dates
