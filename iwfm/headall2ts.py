# headall2ts.py
# Read headall.out file and write out a csv time series file for each layer
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


'''Read headall.out file and write out a csv time series file for each layer.'''

def headall2ts(input_file, output_file, verbose=False):
    '''Read an IWFM HeadAll.out file and write out as a time series with one csv file for each layer.

    Parameters
    ----------
    input_file : str
        IWFM headall.out file name

    output_file : str
        output csv file base name

    verbose : bool, default=False
        True = command-line output on

    Return
    ------
    layers : int
        number of model layers
    '''
    import iwfm

    data, layers, dates, nodes = iwfm.headall_read(input_file)
    iwfm.headall2csv(data, layers, dates, nodes, output_file, verbose=verbose)
    return layers


if __name__ == '__main__':
    ' Run headall2ts() from command line '
    import sys
    import iwfm.debug as idb
    import iwfm
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    if len(sys.argv) > 1:  # arguments are listed on the command line
        heads_file = sys.argv[1]
    else:  # ask for file names from terminal
        heads_file = input('IWFM Headall file name: ')

    iwfm.file_test(heads_file)

    output_file = heads_file.split('.')[0]

    idb.exe_time()  # initialize timer
    count = headall2ts(heads_file, output_file, verbose=verbose)

    print(f'  Wrote {count} output files.')
    idb.exe_time()  # print elapsed time
