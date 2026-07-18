# ppk2fac.py
# Use inverse-distance weighting to calculate factors to translate parameter values 
# from pilot points to model nodes, and write to a file for use by PEST.
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


def read_pp_file(pp_file, verbose=False):
    '''Read pilot points file and return list of tuples.

    Parameters
    ----------
    pp_file : str
        Name of pilot points file

    verbose : bool, default=False   

    Returns
    -------
    pp_coord: list
        List of tuples representing pilot point coordinates.

    pp_list : list
        List of pilot points IDs.
    '''
    import numpy as np

    pp_list, pp_coord = [], []
    # open pp_file and read lines
    with open(pp_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('#'):
                continue
            else:
                line = line.split()
                pp_list.append(line[0])
                pp_coord.append((float(line[1]), float(line[2])))

    #  convert pp_coord to numpy arrays
    pp_coord = np.array(pp_coord)

    return pp_coord, pp_list


def par2fac_idw2(pp_coord, node_coord, n_ppoints=3, min_ppoints=3, max_ppoints=10, verbose=False):
    '''Calculate inverse-distance-squared weighting factors between nodes and n_ppoints pilot points.

    Parameters
    ----------
    pp_coord : list
        List of pilot point coordinates [x, y]

    node_coord : str
        List of nodal coordinates [x, y]

    n_ppoints : int; default = 3
        Number of pilot points for interpolation.

    min_ppoints : int; default = 3
        Minimum number of pilot points for interpolation.

    max_ppoints : int; default = 10
        Maximum number of pilot points for interpolation.

    verbose : bool, default=False
        Turn command-line output on or off

    Returns
    -------
    ppoints : list
        List of pilot points for each node (0-indexed).

    weights : list
        List of normalized pilot point weights for each node.
    '''

    import numpy as np
    # check that n_ppoints is within range
    if n_ppoints < min_ppoints or n_ppoints > max_ppoints:
        raise ValueError(f'n_ppoints = {n_ppoints} is outside of range {min_ppoints} to {max_ppoints}')

    ppoints, weights = [], []
    for node in node_coord:
        #  calculate distance from node to each pilot point
        dist = np.sqrt((pp_coord[:, 0] - node[0]) ** 2 + (pp_coord[:, 1] - node[1]) ** 2)

        dist_sort = np.sort(dist)                           # sort by distance
        dist_sort_index = np.argsort(dist)                  # get indices of sorted distances

        pp, wgt, wgt_sum = [], [], 0
        for n in range(n_ppoints):
            pp.append(dist_sort_index[n])                   # pilot point
            wgt.append(1 / dist_sort[n] ** 2)               # inverse distance squared weighting factor
            wgt_sum += wgt[n]                               # sum of weighting factors

        for n in range(n_ppoints):
            wgt[n] /= wgt_sum                               # normalize weighting factors

        ppoints.append(pp)                                  # assemble pilot points
        weights.append(wgt)                                 # assemble weights

    return ppoints, weights


def write_factors(factors_outfile, pp_file, pp_list, node_list, ppoints, weights, verbose):
    '''Write pilot point factors to output file (hard-wired for 3 ppoints).

    Parameters
    ----------
    factors_outfile : str
        Name of output file.

    pp_file : str
        Name of pilot points file

    pp_list : list
        List of pilot points IDs.

    node_list : list
        List of node IDs.

    ppoints : list
        List of pilot points for each node.

    weights : list
        List of pilot point weights for each node.

    verbose : bool, default=False
        Turn command-line output on or off

    Returns
    -------
    count : int
        Number of factors written to output file.


    '''

    count = 0

    with open(factors_outfile, 'w', encoding='utf-8') as f:
        f.write(f'{pp_file}\n')
        f.write(f'{str(len(node_list)).rjust(12)}\n')  # right-justify to 12 chars
        f.write(f'{str(len(pp_list)).rjust(12)}\n')  # right-justify to 12 chars
        for i in range(len(pp_list)):
            f.write(f'{pp_list[i]}\n')

        for i in range(len(node_list)):
            node = f'{str(node_list[i]).rjust(12)}'  # right-justify to 12 chars

            pp1  = f'{str(ppoints[i][0]+1).rjust(11)}'  # right-justify to 11 chars
            pp2  = f'{str(ppoints[i][1]+1).rjust(11)}'  # right-justify to 11 chars
            pp3  = f'{str(ppoints[i][2]+1).rjust(11)}'  # right-justify to 11 chars

            w1   = f'{str(weights[i][0]).rjust(11)}'  # right-justify to 11 chars
            w2   = f'{str(weights[i][1]).rjust(11)}'  # right-justify to 11 chars
            w3   = f'{str(weights[i][2]).rjust(11)}'  # right-justify to 11 chars

            f.write(f'{node}           1           3  0.0000000E+00{pp1} {w1}\n{pp2} {w2} {pp3} {w3}\n')
            
            count += 1
    return count


if __name__ == '__main__':
    ''' Run ppk2fac_idw2() from command line '''

    import sys
    import iwfm
    import iwfm.debug as idb
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()


    if len(sys.argv) > 1:  # arguments are listed on the command line
        pp_file          = sys.argv[1]
        node_file        = sys.argv[2]
        factors_outfile  = sys.argv[3]

    else:  # ask for file names from command lline
        pp_file          = input('Pilot points file name: ')
        node_file        = input('IWFM Node.dat file name: ')
        factors_outfile  = input('Factors output file name: ')

    iwfm.file_test(pp_file)
    iwfm.file_test(node_file)

    idb.exe_time()  # initialize timer

    #  read pilot points file
    pp_coord, pp_list = read_pp_file(pp_file, verbose=verbose)

    if verbose: print(f'\n Read {len(pp_list):,} pilot points from {pp_file}')

    #  read IWFM node file
    node_coord, node_list = iwfm.read_nodes(node_file)

    if verbose: print(f' Read {len(node_list):,} nodes from {node_file}')

    #  determine pilot points and weights for each node
    ppoints, weights = par2fac_idw2(pp_coord, node_coord, verbose=verbose)

    #  write pilot points and factors to output file
    count = write_factors(factors_outfile, pp_file, pp_list, node_list, ppoints, weights, verbose=verbose)

    if verbose: print(f' Wrote {count:,} factors to {factors_outfile}\n')  # update cli

    idb.exe_time()  # print elapsed time

        
