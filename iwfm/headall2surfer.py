# headall2surfer.py
# Read headall.out file and write out a surfer-formated file for all layers for
# the specified time steps
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

def headall2surfer(node_coords, data, dates, out_dates, output_base, verbose=False):
    '''Write out IWFM Headall.out data for one time step to a surfer-format file.

    Parameters
    ----------
    node_coords: list
        (x,y) coordinates of nodes

    data : list
        numpy array of floats, size nodes x layers

    dates : list
        list of simulated head dates

    out_dates: list
        dates for output

    output_base : str
        output surfer file base name

    verbose : bool, default=False
        True = command-line output on

    Return
    ------
    count : int
        Number of output files written
    '''
    import iwfm

    count = 0

    for i in range(0, len(dates)): 
        if dates[i] in out_dates:
            out_name = output_base + '_' +  dates[i].replace('/','_') + '.sfr'

            iwfm.write_2_surfer(out_name, node_coords, data[i], dates[i])
            count += 1
            if verbose: print(f'  Wrote heads for {dates[i]}')

    return count

if __name__ == '__main__':
    ' Run headall2surfer() from command line '
    import sys
    import os
    import iwfm.debug as idb
    import iwfm
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    args = sys.argv[1:]  # get command line arguments
    if len(sys.argv) > 1:  # arguments are listed on the command line
        heads_file, pre_file, output_root, out_dates_file = args
    else:  # ask for file names from terminal
        heads_file     = input('IWFM Headall file name: ')
        pre_file       = input('IWFM Preprocessor main file name: ')
        output_root    = input('Output file rootname: ')
        out_dates_file = input('Output dates file name: ')

    iwfm.file_test(heads_file)
    iwfm.file_test(pre_file)
    iwfm.file_test(out_dates_file)

    output_root = heads_file.split('.')[0]

    idb.exe_time()  # initialize timer

    data, layers, dates, nodes = iwfm.headall_read(heads_file)

    # read dates to create ooutput files for
    with open(out_dates_file, encoding='utf-8') as f:
        date_lines = f.read().splitlines() 
    out_dates = [line for line in date_lines]

    # get preprocessor file names
    pre_path, pre_proc = os.path.split(pre_file)
    pre_files, _ = iwfm.iwfm_read_preproc(pre_file)

    # read preprocessor node file
    node_file = os.path.join(pre_path, pre_files.node_file)
    iwfm.file_test(node_file)
    node_coords, node_list, factor = iwfm.iwfm_read_nodes(node_file)

    # multiply noode_coords X and Y by factor
    for i in range(0, len(node_coords)):
        node_coords[i][1] *= factor
        node_coords[i][2] *= factor

    count = headall2surfer(node_coords, data, dates, out_dates, output_root)

    print(f'  Wrote {count} surfer output files.')

    idb.exe_time()  # print elapsed time
