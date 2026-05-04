# gw_hyd_monthly.py
# Reduce daily IWFM groundwater hydrograph to monthly
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


def gw_hyd_monthly(gwhyd_file):
    ''' gw_hyd_monthly() - Reduce daily IWFM groundwater hydrograph to monthly

    Parameters
    ----------
    gwhyd_file : str
        IWFM groundwater hydrograph file name
    
    
    Return
    ------
    nothong
    
    '''
    
    import iwfm

    # create outname 
    out_name = gwhyd_file.split('.')[0] + '_monthly.' + gwhyd_file.split('.')[1]
    
    # Read groundwater hydrograph file
    iwfm.file_test(gwhyd_file)
    with open(gwhyd_file) as f:
        gwhyd_lines = f.read().splitlines()

    # Skip header lines to reach first data line
    from iwfm.file_utils import read_next_line_value
    _, line_index = read_next_line_value(gwhyd_lines, -1, skip_lines=0)
    start_index = line_index
    start_len = len(gwhyd_lines) - start_index  # Count of data lines

    out_lines = []
    for line in gwhyd_lines[:line_index]:
        out_lines.append(line)
    out_lines.append(gwhyd_lines[line_index])
    line_index += 1

    test_str = gwhyd_lines[line_index][:2]
    while line_index < len(gwhyd_lines):
        if gwhyd_lines[line_index][:2] != test_str:
            out_lines.append(gwhyd_lines[line_index-1])
            test_str = gwhyd_lines[line_index][:2]
        line_index += 1

    out_lines.append(gwhyd_lines[len(gwhyd_lines)-1])     # add last line
    out_lines.append('')                                 # add blank line at end

    with open(out_name, 'w') as outfile:                  # write monthly file
        outfile.write('\n'.join(out_lines))

    return out_name, start_len, len(out_lines) - start_index


if __name__ == '__main__':
    ' Run gw_hyd_reduce() from command line '
    import sys
    import iwfm
    import iwfm.debug as idb
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    args = sys.argv

    if len(args) > 1:  # arguments are listed on the command line
        gwhyd_file = args[1]   # IWFM Groundwater hydrograph file name

    else:  # get everything form the command line
        gwhyd_file = input('IWFM Groundwater hydrograph file name: ')

    # test that the input file exists
    iwfm.file_test(gwhyd_file)

    idb.exe_time()  # initialize timer
    outname, start_len, no_lines = gw_hyd_monthly(gwhyd_file)
    print(f'  Reduced {gwhyd_file} from {start_len:,} to {no_lines:,} lines and wrote to {outname}')  # update cli
    idb.exe_time()  # print elapsed time
