# calib_stats.py
# Read a PEST .smp file, IWFM groundwater hydrograph file, and IWFM groundwater.dat 
# file, and print a text file with the RMSE and bias of each well and of all observations
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

from iwfm.read_sim_hyd import read_sim_hyd
from iwfm.debug.logger_setup import logger


def calib_stats(pest_smp_file, gwhyd_info_file, gwhyd_file, verbose=False):
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

    import iwfm
    import iwfm.calib as ical

    if verbose:
        print(f'  pest_smp_file:\t{pest_smp_file}')
        print(f'  gwhyd_info_file:\t{gwhyd_info_file}')
        print(f'  gwhyd_file:   \t{gwhyd_file}\n')
    
    # == read pest observation file into array obs
    try:
        with open(pest_smp_file, encoding='utf-8') as f:
            head_obs = f.read().splitlines()
    except FileNotFoundError:
        logger.error(f'File not found: {pest_smp_file}')
        raise
    except PermissionError:
        logger.error(f'Permission denied reading file: {pest_smp_file}')
        raise
    except OSError as e:
        logger.error(f'OS error reading file {pest_smp_file}: {e}')
        raise
    logger.debug(f'Read {len(head_obs)} lines from {pest_smp_file}')
    for i in range(0,len(head_obs)):
        head_obs[i] = head_obs[i].split()
        date_str = head_obs[i][1]
        try:
            head_obs[i][1] = iwfm.safe_parse_date(date_str, f'{pest_smp_file} line {i+1}')
        except ValueError as e:
            logger.error(f'Error parsing date on line {i+1} of {pest_smp_file}: {e}')
            raise ValueError(f"Error reading {pest_smp_file} line {i+1}: {str(e)}") from e
        head_obs[i][3] = float(head_obs[i][3])
    if verbose:
        print(f'  Read {len(head_obs):,} observations from {pest_smp_file}')
        print(f'  head_obs[0]: {head_obs[0]}\n')

    # groundwater hydrograph info to dictionary of groundwater hydrograph info
    gw_hyd_dict = iwfm.read_hyd_dict(gwhyd_info_file)
    if verbose:
        print(f'  Read information for {len(gw_hyd_dict):,} observation wells from {gwhyd_info_file}')
        print(f'  Test: hyd_dict[{head_obs[0][0]}] {gw_hyd_dict[head_obs[0][0]]}\n')

    # read simulated values
    simhyd = read_sim_hyd(gwhyd_file)
    if verbose:
        print(f'  Read {len(simhyd):,} simulated values from {gwhyd_file}\n')

    # == cycle through the list of wells in pest_obs to calculate rmse & bias
    # -- initialize
    i = 1
    dates, meas, sim = [], [], []
    well_names, rmse_values, bias_values, sim_all = [], [], [], []
    meas_all, count, dates, meas, dates_all, names_all = [], [], [], [], [], []

    name, date = head_obs[0][0], head_obs[0][1]

    names_all.append(name)
    dates.append(date)
    dates_all.append(date)
    measured = head_obs[0][3]
    meas.append(measured)
    meas_all.append(measured)

    # use hyd_dict to find the column no for this obs well in simhyd_obs
    simhyd_col = int(gw_hyd_dict.get(name).column)

    # calculate the simulated value for this observation
    sim_head = ical.sim_equiv(simhyd, date, simhyd_col)
    sim.append(sim_head)
    sim_all.append(sim_head)

    # move through the head observations
    j, final = 1, 1
    while j < len(head_obs):
        new_name = head_obs[j][0]
        if new_name != name:  # new well name, finalize info for the last well

            if verbose:
                print(f'  Calculating RMSE and Bias for {name}')
            # calculate rmse and bias
            well_names.append(name)

            rmse = ical.rmse_calc(sim, meas)
            bias = ical.bias_calc(sim, meas)

            rmse_values.append(rmse)
            bias_values.append(bias)
            count.append(len(meas))

            dates, meas, sim = [], [], [] # re-initialize for next observation well

            # find next well from head_obs that is in hyd_dict
            while new_name not in gw_hyd_dict:
                j += 1
                if j >= len(head_obs):
                    final = 0   # no more wells in hyd_dict, stats for last already calculated
                    break
                new_name = head_obs[j][0]
            if j >= len(head_obs):
                break
            name = new_name
            simhyd_col = int(gw_hyd_dict.get(name).column)
    
        names_all.append(name)

        date = head_obs[j][1]
        dates.append(date)
        dates_all.append(date)

        measured = head_obs[j][3]
        meas.append(measured)
        meas_all.append(measured)

        sim_head = ical.sim_equiv(simhyd, date, simhyd_col)
        #simulated = simhyd_obs.sim_head(date,simhyd_col)
        sim.append(sim_head)
        sim_all.append(sim_head)

        j += 1

    # calculate final one
    if final:   # stats for final well not calculated yet
        rmse = ical.rmse_calc(sim, meas)
        bias = ical.bias_calc(sim, meas)

        rmse_values.append(rmse)
        bias_values.append(bias)
        well_names.append(name)
        count.append(len(meas))

    # write all simulated and measured values to a file
    out_file = gwhyd_file.replace('.out','_sim_obs.txt')
    try:
        with open(out_file,'w', encoding='utf-8') as of:
            of.write('Well Name\tDate\tSimulated\tObserved\n')
            for i in range(0,len(sim_all)):
                of.write(f'{names_all[i]}\t{dates_all[i].strftime("%m/%d/%y")}\t{sim_all[i]}\t{meas_all[i]}\n')
    except PermissionError:
        logger.error(f'Permission denied writing file: {out_file}')
        raise
    except OSError as e:
        logger.error(f'OS error writing file {out_file}: {e}')
        raise
    logger.debug(f'Wrote {len(sim_all)} simulated/observed values to {out_file}')
    logger.info(f'Wrote all simulated and observed values to {out_file}')

    # write out results for each well
    out_file = gwhyd_file.replace('.out','_rmse.txt')
    ical.write_rmse_bias(out_file,gw_hyd_dict,well_names,rmse_values,bias_values,count)
    logger.info(f'Wrote results for each well to {out_file}')


    # write out results for all wells
    out_file = gwhyd_file.replace('.out','_rmse_all.txt')
    try:
        with open(out_file,'w', encoding='utf-8') as of:
            of.write('Filename\tRMSE\tBIAS\n')
            rmse_all = round(ical.rmse_calc(sim_all,meas_all),2)
            bias_all = round(ical.bias_calc(sim_all,meas_all),2)
            of.write(f'{gwhyd_file}\t{rmse_all}\t{bias_all}\n')
    except PermissionError:
        logger.error(f'Permission denied writing file: {out_file}')
        raise
    except OSError as e:
        logger.error(f'OS error writing file {out_file}: {e}')
        raise
    logger.debug(f'Wrote overall RMSE={rmse_all} and BIAS={bias_all} to {out_file}')
    logger.info(f'Wrote results for all wells to {out_file}')
    
    return


if __name__ == '__main__':
    ' Run calib_stats() from command line '
    import sys
    import iwfm
    import iwfm.debug as idb
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
    calib_stats(pest_smp_file, gwhyd_info_file, gwhyd_file)

    idb.exe_time()  # print elapsed time
