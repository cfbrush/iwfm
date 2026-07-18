# real2iwfm.py
# Read parameter values for model nodes and combine into an IWFM
# overwrite file
# Copyright (C) 2020-2026 University of California
# Based on a PEST utility written by Matt Tonkin
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



'''Read parameter values for model nodes and combine into an IWFM overwrite file.'''

def real2iwfm(verbose=False):
    '''Read pilot point parameters and write to IWFM Overwrite.dat file.

    Prompt the user for the no. of layers (nlay) in an IWFM model application; and the no. of parameter types (ntype) for which pilot points have been employed in order to define node values. program real2iwfm then prompts for (nlay*ntype) file names where each of these files is the output from running program ppk2fac_iwfm in order to use pilot points to define nodal parameter values. These files are formatted with a header indicating the number of nodes that are in the full IWFM application, and the number of nodes that are 'informed' by the contents of that file on the basis of pilot points. program real2iwfm then concatenates these files, for each layer and for each parameter type, into a file compatible with the new IWFM external node-value replacement file designed by Can Dogrul.

         From REAL2IGSM.F90 by Matt Tonkin, with modifications by others

    Parameters
    ----------
    verbose : bool, default=False
        Print to screen?
    '''
    from iwfm import file_test
    from iwfm.calib import read_overwrite_file, write_overwrite_file

    param_types = ['PKH', 'PS', 'PN', 'PV', 'PL', 'SCE', 'SCI']
    
    factors = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]               # factors for scaling parameters = 1.0 unless otherwise specified

    if verbose:
        print(' Program REAL2IWFM reformats the outputs of one or more  ')
        print(' output files from FAC2REALI into a node overwrite file that can ')
        print(' be read by IWFM.')

    overwrite_file = input('\n Name of existing overwrite file: ')

    file_test(overwrite_file)

    output_file = input(' Name of new overwrite file: ')

    nlay = int(input( 'Number of model layers: '))

    nnodes = int(input(' Number of nodes with parameter values: '))

    ctime = input(' Parameter time-step units: ')

    nwrite, factors, oldparvals_d, in_lines = read_overwrite_file(
            overwrite_file, nnodes, nlay, param_types, verbose)

    # read new parameter values
    parvals, parnodes = [], []
    for ptype in param_types:
        ans = input(f'\n Include data for parameter type {ptype}? [y/n] ').lower()

        pvals, pnodes = [], []
        if ans[0] == 'y':

            for layer in range(0, nlay):

                param_file = input(
                    f'\n Parameter value file for parameter type {ptype}, layer {layer+1}, or \'none\': ')

                layer_vals, layer_nodes = [], []
                if param_file == 'none':
                    layer_vals = [-1.0] * nnodes
                    pnodes.append(list(range(1,nnodes+1)))

                else:
                    file_test(param_file)
                    with open(param_file, encoding='utf-8') as f:
                        file_lines = f.read().splitlines()
                    for line in file_lines:
                        text = line.split()
                        layer_nodes.append(int(text[1]))
                        layer_vals.append(float(text[3]))
                    if verbose:
                        print(f' Read values for {len(file_lines)} nodes from {param_file}')

                pvals.append(layer_vals)
                pnodes.append(layer_nodes)

        else:
            for layer in range(0, nlay):
                pvals.append([-1] * nnodes)
                pnodes.append(list(range(1,nnodes+1)))

        parvals.append(pvals)
        parnodes.append(pnodes)

    write_overwrite_file(output_file, in_lines, parnodes, nlay, parvals, factors, ctime, verbose)

    if verbose:
        print(f'\n\n Created overwrite file {output_file}. ')
        print( ' All scaling factors from the original file have been preserved. ')
        print( ' Make sure these factors correctly account for the desired scaling.')

    return



if __name__ == "__main__":
    ''' Run real2iwfm() from command line '''
    from iwfm.debug import exe_time, parse_cli_flags

    verbose, debug = parse_cli_flags()

    exe_time()  # initialize timer
    real2iwfm(verbose=verbose)
    print('\n')
    exe_time()  # print elapsed time

