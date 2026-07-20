# pest_res_stats.py -  Read a PEST .res file, and print a text file with the RMSE and bias
# of each observation site
# Copyright (C) 2018-2023 Hydrolytics LLC
#-----------------------------------------------------------------------------
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
#-----------------------------------------------------------------------------


'''Read a PEST .res file, and print a text file with the RMSE and bias of each observation site.'''

def pest_res_stats(pest_res_file, verbose=False):
    '''Read a PEST .res file, and print a text file with the RMSE and bias of each observation site.

    Parameters
    ----------
    pest_res_file : string
        name of PEST .res file

    verbose : bool, default = False
        If True, print additional information to the screen

    Returns
    -------
    nothing
    '''
    import numpy as np

    # read pest results file
    with open(pest_res_file, encoding='utf-8') as f:
        pest_res = f.read().splitlines()
    
    pest_res.pop(0)                          # remove the header line

    # use list comprehension to split each line of pest_res
    pest_res = [line.split() for line in pest_res]

    # observation names have the format 'station_MMYYYY'
    # split first item into observation and date on '_', and append date to end
    for i in range(0, len(pest_res)):
        obs_name, obs_date = pest_res[i][0].split('_')
        pest_res[i][0] = obs_name
        pest_res[i].append(obs_date)

    names = list(set([x[0] for x in pest_res]))    # list of all different values of pest_res[0]

    obs = []
    for name in names:
        obs.append([name,0,0,0,0,0,''])  # name, n, mean, bias, rmse, stdev, group

    # cycle through pest_res and accumulate values
    for i in range(0, len(pest_res)):
        for j in range(0, len(names)):
            if pest_res[i][0] == names[j]:                          # name
                obs[j][1] += 1                                      # n
                obs[j][2] += float(pest_res[i][2])                  # mean accumulator
                obs[j][3] += float(pest_res[i][3])                  # bias accumulator
                obs[j][4] += (float(pest_res[i][3]))**2             # rmse accumulator
                obs[j][6] =  pest_res[i][1]                         # group
                
    # calculate mean, bias, rmse
    for i in range(0, len(obs)):
        if obs[i][1] > 0:
            obs[i][2] = obs[i][2]/obs[i][1]                             # mean
            obs[i][3] = obs[i][3]/obs[i][1]                             # bias
            obs[i][4] = np.sqrt(obs[i][4]/obs[i][1])                    # rmse
        else:
            obs[i][2] = -999                                            # mean
            obs[i][3] = -999                                            # bias
            obs[i][4] = -999                                            # rmse

    # cycle through pest_res and calculate stdev
    for i in range(0, len(pest_res)):
        for j in range(0, len(names)):
            if pest_res[i][0] == names[j]:                          # name
                obs[j][5] += (float(pest_res[i][2])-obs[j][2])**2   # stdev accumulator
    for i in range(0, len(obs)):
        if obs[i][1] > 1:
            obs[i][5] = np.sqrt(obs[i][5]/(obs[i][1]-1))                # stdev
        else:
            obs[i][5] = -999

    # sort obs on [6] then [1]
    obs.sort(key=lambda x: (x[1],x[6]))

    # write out results
    out_file = pest_res_file.replace('.res','_stats.out')
    from iwfm.debug.logger_setup import logger
    logger.info(f'Writing {out_file}')
    with open(out_file,"w", encoding='utf-8') as of:
        of.write('Name\tN\tMean\tBias\tRMSE\tStdev\tGroup\n')
        for i in range(0, len(obs)):
            of.write(f'{obs[i][0]}\t{obs[i][1]}\t{obs[i][2]:.2f}\t{obs[i][3]:.2f}\t{obs[i][4]:.2f}\t{obs[i][5]:.2f}\t{obs[i][6]}\n')


if __name__ == "__main__":
    import sys
    import iwfm
    import iwfm.debug as idb
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    if len(sys.argv) > 1:  # arguments are listed on the command line
        pest_res_file = sys.argv[1]
    else:                  # ask for file names from terminal
        pest_res_file   = input("  PEST results file name (*.res): ")

    iwfm.file_test(pest_res_file)    # test that the input files exist

    idb.exe_time()                   # initialize timer

    pest_res_stats(pest_res_file)

    idb.exe_time()                   # print elapsed time

    


