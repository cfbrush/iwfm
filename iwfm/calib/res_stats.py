# res_stats.py
# Read a PEST .smp file, IWFM groundwater hydrograph file, and
# IWFM groundwater.dat file, and print a text file with
# the RMSE and bias of each well and of all observations
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

'''Read a PEST .smp file, IWFM groundwater hydrograph file, and IWFM groundwater.dat file, and print a text file with the RMSE and bias of each well and of all observations.'''

import iwfm
import iwfm.calib as icalib


def res_stats(pest_smp_file, gwhyd_info_file, gwhyd_file, verbose=False):
    '''Read a PEST .smp file, IWFM groundwater hydrograph file, and IWFM groundwater.dat file, and print a text file with the RMSE and bias of each well and of all observations.

    Parameters
    ----------
    pest_smp_file : str
        PEST .smp file name

    gwhyd_info_file : str
        IWFM groundwater hydrograph file name

    gwhyd_file : str
        IWFM groundwater.dat file name

    verbose : bool, default=False
        True = command line updates on

    Returns
    -------
    nothing
    '''
    
    # == read pest observation file into array obs
    with open(pest_smp_file, encoding='utf-8') as f:
        head_obs = f.read().splitlines()
    for i in range(0,len(head_obs)):
        head_obs[i] = head_obs[i].split()
        head_obs[i][0] = head_obs[i][0].lower()
        head_obs[i][3] = float(head_obs[i][3])
    if verbose:
        print(f'  Read {len(head_obs):,} observations from {pest_smp_file}')
        print(f'  head_obs[0]: {head_obs[0]}\n')

    # groundwater hydrograph info to dictionary of groundwater hydrograph info
    hyd_dict = iwfm.hyd_dict(gwhyd_info_file)       # hyd_dict is a dictionary
    if verbose:
        print(f'  Read observation well information from {gwhyd_info_file}')
        print(f'  hyd_dict[{head_obs[0][0]}] {hyd_dict[head_obs[0][0]]}\n')

    # read simulated values
    simhyd = iwfm.simhyds(gwhyd_file)               # simhyd is a class
    if verbose:
        print(f'  Read {len(simhyd.sim_vals):,} simulated values from {gwhyd_file}')
        print(f'  simhyd.sim_vals[0][0:3]: {simhyd.sim_vals[0][0:3]}\n')

    # == cycle through the list of wells in pest_obs to calculate rmse & bias
    # -- initialize
    i = 1
    dates, meas, sim = [], [], []
    well_names, rmse_values, bias_values, sim_all = [], [], [], []
    meas_all, count, dates, meas = [], [], [], []

    from iwfm.debug.logger_setup import logger

    name, date = head_obs[0][0], head_obs[0][1]
    logger.debug(f'name: {name}, date: {date}, meas: {head_obs[0][3]}')
    dates.append(date)
    meas.append(head_obs[0][3])

    # use hyd_dict to find the column no for this obs well in simhyd_obs
    simhyd_col = int(hyd_dict.get(name).column)
    logger.debug(f'simhyd_col: {simhyd_col}')

    # calculate the simulated value for this observation
    logger.debug(f'simhyd.sim_head({date},{simhyd_col}): {simhyd.sim_head(date,simhyd_col)}')
    sim.append(simhyd.sim_head(date,simhyd_col))    

    # move through the file
    j = 1
    while j < len(head_obs):
        new_name = head_obs[j][0]
        if new_name != name:  # new well name, finalize info for the last well
            # calculate rmse and bias
            well_names.append(name)
            rmse = icalib.rmse_calc(sim,meas)
            bias = icalib.bias_calc(sim,meas)
            rmse_values.append(rmse)
            bias_values.append(bias)
            count.append(len(meas))

            dates, meas, sim = [], [], [] # re-initialize for next observation well

            # find next well from head_obs that is in hyd_dict
            while new_name not in hyd_dict:
                j += 1
                new_name = head_obs[j][0]
            name = new_name
            simhyd_col = (hyd_dict.get(name).column)

        date = head_obs[j][1]
        dates.append(date)

        simulated = simhyd.sim_head(date,simhyd_col)  # Fixed: was simhyd_obs (typo)
        sim.append(simulated)
        sim_all.append(simulated)

        measured = head_obs[j][3]
        meas.append(measured)
        meas_all.append(measured)

        j += 1

    # calculate final one
    rmse_values.append(icalib.rmse_calc(sim,meas))
    well_names.append(name)
    bias_values.append(icalib.bias_calc(sim,meas))
    count.append(len(meas))

    # write out results
    out_file = gwhyd_file.replace('.out','_rmse.txt')

    icalib.write_rmse_bias(out_file,hyd_dict,well_names,rmse_values,bias_values,count)
    if verbose:
        print(f'  Wrote {out_file}')

    out_file = gwhyd_file.replace('.out','_rmse_all.txt')
    with open(out_file,'w', encoding='utf-8') as of:
        of.write('{}\t{}\t{}\n'.format(out_file,icalib.rmse_calc(sim_all,meas_all),icalib.bias_calc(sim_all,meas_all)))
    if verbose:
        print(f'  Wrote {out_file}')
    return


if __name__ == '__main__':
    ' Run res_stats() from command line '
    import sys
    import iwfm.debug as idb
    import iwfm
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    if len(sys.argv) > 1:  # arguments are listed on the command line
        pest_smp_file = sys.argv[1]
        gwhyd_info_file = sys.argv[2]
        gwhyd_file = sys.argv[3]
    else:
        # ask for file names from terminal
        pest_smp_file   = input('  Observation file name: ')
        gwhyd_info_file = input('  IWFM Groundwater.dat file name: ')
        gwhyd_file      = input('  IWFM Groundwater Hydrograph file name: ')

    iwfm.file_test(pest_smp_file)
    iwfm.file_test(gwhyd_info_file)
    iwfm.file_test(gwhyd_file)

    idb.exe_time()  # initialize timer
    res_stats(pest_smp_file, gwhyd_info_file, gwhyd_file) 

    idb.exe_time()  # print elapsed time
