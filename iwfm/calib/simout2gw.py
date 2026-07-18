# simout2gw.py
# Read groundwater parameters from SimulationMessages.out file and write to
# Groundwater.dat file
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


'''Read groundwater parameters from SimulationMessages.out file and write to.

Groundwater.dat file.
'''

def read_gw_file(gw_file):
    '''Read groundwater file.

    Parameters
    ----------
    gw_file : str
        The path of the file containing the groundwater data.

    Returns
    -------
    gw_data : list
        A list containing the groundwater data file contents.

    param_line : int
        Line number where groundwater parameters are located.
    '''
    import iwfm
    from iwfm.file_utils import read_next_line_value

    iwfm.file_test(gw_file)
    with open(gw_file, encoding='utf-8') as f:
        gw_data = f.read().splitlines()

    nouth_str, line_index = read_next_line_value(gw_data, 0, column=0, skip_lines=20)
    nouth = int(nouth_str)             # number of hydrograph lines to skip

    noutf_str, line_index = read_next_line_value(gw_data, line_index - 1, column=0, skip_lines=nouth + 3)
    noutf = int(noutf_str)             # number of flow lines to skip

    _, line_index = read_next_line_value(gw_data, line_index - 1, skip_lines=noutf + 7)
    param_line = line_index

    return gw_data, param_line


    


def read_gw_params(simout_file):
    '''Read groundwater parameters from a file and organize them into lists.

    Parameters
    ----------
    simout_file : str
        The path of the file containing the groundwater data.

    Returns
    -------
    gw_params : list
        A list containing the groundwater parameters.
    '''
    import iwfm

    iwfm.file_test(simout_file)
    with open(simout_file, encoding='utf-8') as f:
        sim_lines = f.read().splitlines() 

    #  Find line number
    desired = "   NODE          PKH                       PS                        PN                        PV                        PL"
    for line_num, line in enumerate(sim_lines):
        if line == desired:
            break
 
    # find the start and end lines of the groundwater parameter section
    start = line_num + 1
    end = line_num + 2
    while len(sim_lines[end].split()) > 1:
        end += 1
    gw_params = sim_lines[start:end]

    return gw_params


def replace_params(gw_params, gw_data, param_line):
    '''Process groundwater data.

    Parameters
    ----------
    gw_params : list
        A list containing the groundwater parameters.

    gw_data : list
        A list containing the groundwater data file contents.

    Returns
    -------
    gw_data : list
        A list containing the groundwater data file contents w/new parameters.
    '''
    param_len = len(gw_params)

    gw_data[param_line:param_line + param_len] = gw_params

    return gw_data


def simout2gw(simout_file, gw_in_file, output_file):
    '''Read groundwater parameters from SimulationMessages.out file, replace parameters in template groundwater.dat file, and write to a new groundwater.dat file.

    Parameters
    ----------
    simout_file : str
        The path of the file containing the groundwater data.

    gw_in_file : str
        The path of the file containing the groundwater template data.

    output_file : str
        The path of the file to write the groundwater data to.

    Returns
    -------
    None
    '''

    # read input files
    gw_params = read_gw_params(simout_file)

    gw_data, param_line = read_gw_file(gw_in_file)

    # replace parameters in templage groundwater.dat file
    gw_data = replace_params(gw_params, gw_data, param_line)

    # write output file
    with open(output_file, 'w', encoding='utf-8') as out_file:
        for item in gw_data:
            out_file.write(f'{item}\n')


if __name__ == "__main__":
    ''' Run simout2gw() from command line '''

    import sys
    import iwfm
    import iwfm.debug as idb
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()
  
    if len(sys.argv) > 1:  # arguments are listed on the command line
        simout_file  = sys.argv[1]
        gw_in_file   = sys.argv[2]
        output_file  = sys.argv[3]
    else:                                                      # ask for file names from terminal
        simout_file   = input("SimulationMessages.out file name: ")
        gw_in_file    = input("Geroundwater template file name.: ")
        output_file   = input("Groundwater output file name: ")

    iwfm.file_test(simout_file)
    iwfm.file_test(gw_in_file)

    idb.exe_time()  # initialize timer

    simout2gw(simout_file, gw_in_file, output_file)

    print(f'\n  Read {simout_file} and wrote {output_file}.')  # update cli

    idb.exe_time()  # print elapsed time
