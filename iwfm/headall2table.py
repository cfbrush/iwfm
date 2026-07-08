# headall2table.py
# Read headall.out file and write results for one date toa table
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


def headall2table(heads_file, output_file, out_date):
    ''' headall2table() - Read IWFM headall.out file and write results
        for one date to a table

    Parameters
    ----------
    heads_file : str
        IWFM headall.out file name
    
    output_file : str
        name of output file
    
    out_date : str
        date to process, mm/dd/yyyy format

    Returns
    -------
    nothing

    '''
    import numpy as np
    import polars as pl

    date_parts = out_date.split('/')  # parse date components
    out_mon, out_day, out_year = int(date_parts[0]), int(date_parts[1]), int(date_parts[2])

    with open(heads_file, encoding='utf-8') as f:
        file_lines = f.read().splitlines()  # open and read input file

    start = 5  # skip the first 5 lines
    line = start
    nodes = file_lines[line].split()  # read line w/node nos
    nodes.pop(0)  # remove text
    nodes.pop(0)  # remove text

    data = []
    data.append(nodes)

    line += 1
    item = file_lines[line].split()  # read line w/date
    data.append(item)
    end_date = item.pop(0)  # remove the date
    
    while line < len(file_lines) - 1:
        line += 1
        layer = 1
        header = []
        header.append('Node')
        header.append('Layer ' + str(layer))
        while file_lines[line][0].isspace():  # get all the lines for this time step
            item = file_lines[line].split()
            data.append(item)
            layer += 1
            header.append('Layer ' + str(layer))
            line += 1
        # now check the date
        date_parts2 = end_date[0:10].split('/')  # parse date components
        m, d, y = int(date_parts2[0]), int(date_parts2[1]), int(date_parts2[2])
        if m == out_mon and d == out_day and y == out_year:
            out_table = np.transpose(np.asarray(data))
            df = pl.DataFrame(out_table, schema=header, orient='row')
            df.write_csv(output_file)
            return
        else:
            data = []
            data.append(nodes)
            item = file_lines[line].split()  # read line w/date
            data.append(item)
            end_date = item.pop(0)  # remove the date

    return


if __name__ == '__main__':
    ' Run headall2table() from command line '
    import sys
    import iwfm.debug as idb
    import iwfm
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    if len(sys.argv) > 1:  # arguments are listed on the command line
        heads_file = sys.argv[1]
        output_file = sys.argv[2]
        out_date = sys.argv[3]
    else:  # ask for file names from terminal
        heads_file  = input('IWFM Headall file name: ')
        output_file = input('Output file name: ')
        out_date    = input('Output date: ')

    iwfm.file_test(heads_file)

    idb.exe_time()  # initialize timer
    headall2table(heads_file, output_file, out_date)

    print(f'  Read {heads_file} and wrote {output_file}.')  # update cli
    idb.exe_time()  # print elapsed time
