# read_gw_file.py
# Read an IWFM Groundwater file and return the number of nodes, 
# the scaling factors, and the parameter values
# Copyright (C) 2020-2025 University of California
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


def read_gw_file(gw_file, nlay, keys_file='parvals_keys.txt', 
                 dict_file='parvals_d.txt', verbose=False):
    """ read_gw_file - Read an IWFM Groundwater file and return the number of nodes, 
        the scaling factors, and the parameter values
        
    Parameters
    ----------

    gw_file : str
        IWFM Groundwater file name

    nlay : int
        Number of layers (from Stratigraphy file, not in this file)

    keys_file : str, default = 'parvals_keys.txt'
        Output text file with parameter keys

    dict_file : str, default = 'parvals_d.txt'
        Output text file with parameter keys and values
    
    verbose : bool, default=False
        Print to screen?

    Returns
    -------
    factors : list
        multiplication factors

    params_d : dictionary of lists
        default model parameters, key = node_layer, value = list of parameter values
    
    """

    params_d = {}
    comments = 'Cc*#'

    with open(gw_file, 'r', encoding='utf-8') as f:
        gw_lines = f.read().splitlines()

    line_index = 10
    while line_index < len(gw_lines) and gw_lines[line_index] and gw_lines[line_index][0] in comments:  # skip comment lines
        line_index += 1

    while line_index < len(gw_lines) and gw_lines[line_index] and gw_lines[line_index][0] not in comments:  # skip file names and units etc
        line_index += 1

    while line_index < len(gw_lines) and gw_lines[line_index] and gw_lines[line_index][0] in comments:  # skip comment lines
        line_index += 1

    line_index += 1                                             # skip KDEB line

    while line_index < len(gw_lines) and gw_lines[line_index] and gw_lines[line_index][0] in comments:  # skip comment lines
        line_index += 1

    while line_index < len(gw_lines) and gw_lines[line_index] and gw_lines[line_index][0] not in comments:  # skip hydrograph information
        line_index += 1

    while line_index < len(gw_lines) and gw_lines[line_index] and gw_lines[line_index][0] in comments:  # skip comment lines
        line_index += 1

    while line_index < len(gw_lines) and gw_lines[line_index] and gw_lines[line_index][0] not in comments:  # skip hydrograph lines
        line_index += 1

    while line_index < len(gw_lines) and gw_lines[line_index] and gw_lines[line_index][0] in comments:  # skip comment lines
        line_index += 1

    while line_index < len(gw_lines) and gw_lines[line_index] and gw_lines[line_index][0] not in comments:  # skip face flow control lines
        line_index += 1

    while line_index < len(gw_lines) and gw_lines[line_index] and gw_lines[line_index][0] in comments:  # skip comment lines
        line_index += 1

    line_index += 1                                             # skip NGROUP line

    while line_index < len(gw_lines) and gw_lines[line_index] and gw_lines[line_index][0] in comments:  # skip comment lines
        line_index += 1

    factors = [float(x) for x in gw_lines[line_index].split()]  # read factors
    line_index += 1                                             # skip to next line

    while line_index < len(gw_lines) and gw_lines[line_index] and gw_lines[line_index][0] in comments:  # skip comment lines
        line_index += 1

    while line_index < len(gw_lines) and gw_lines[line_index] and gw_lines[line_index][0] not in comments:  # skip time units
        line_index += 1

    while line_index < len(gw_lines) and gw_lines[line_index] and gw_lines[line_index][0] in comments:  # skip comment lines
        line_index += 1

    with open(keys_file, 'w', encoding='utf-8') as f:                              # write parameter values to file
        parvals_d = {}                                              # initialize dictionary
        while line_index < len(gw_lines) and gw_lines[line_index] and gw_lines[line_index][0] not in comments:  # process parameter lines
            for l in range(0, nlay):                                # cycle through layers
                items = gw_lines[line_index].split()
                if l == 0:
                    node = int(items[0])
                    items.pop()

                key = f'{node}_{l+1}'
                parvals_d[key] = [float(x) for x in items]
                f.write(f'  => {node}=\t{l=}\t{key=}\t{parvals_d[key]=}\n')

                line_index += 1

    with open(dict_file, 'w', encoding='utf-8') as f:                              # write parameter values to file
        for key in parvals_d.keys():
            f.write(f'{key} {parvals_d[key]}\n')

    if verbose:     print(f'\n Read {gw_file}')

    return gw_lines, factors, parvals_d


if __name__ == "__main__":
    ''' Run read_gw_file() from command line '''
    import sys
    import iwfm.debug as idb
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()


    # read arguments from command line
    if len(sys.argv) > 1:  # arguments are listed on the command line
        gw_file          = sys.argv[1]         # Name of existing IWFM Groundwater file
        nlay             = int(sys.argv[2])    # Number of model layers

    else:  # get everything form the command line
        gw_file          = input('Name of existing IWFM Groundwater file: ')
        nlay             = int(input('Number of model layers: '))


    idb.exe_time()  # initialize timer

    # read the existing Groundwater file and parameters
    gw_lines, factors, parvals_d = read_gw_file(gw_file, nlay, verbose=verbose)

    if verbose:
        print(f'\n\n Read Groundwater file {gw_file}. ')
        print(f' Scaling factors: {factors=}" ')
    print('\n')

    idb.exe_time()  # print elapsed time

