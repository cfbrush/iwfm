# detaw_2_table.py
# Convert DETAW files to tables and write to text files
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


def detaw_2_table(dir_name, outfile_name, verbose=False):
    '''Convert DETAW files to tables and write to text files.

    Parameters
    ----------

    dir_name : str
        name of directory holding files

    outfile_name : str
        name of output file

    verbose : bool, default=False
     Turn command-line output on or off

    Returns
    -------
    nothing    

    '''
    import os
    import csv

    input_files = os.listdir(dir_name)

    with open(outfile_name, 'w', newline='', encoding='utf-8') as out_file:
        out_writer = csv.writer(out_file)

        header, data = 0, []
        for file_name in input_files:
            if file_name[0] != '.':
                file_name = os.path.join(dir_name, file_name)
                with open(file_name, encoding='utf-8') as f:
                    file_lines = f.read().splitlines()  # open and read input file
                if header == 0:  # first file so get header
                    header = 1
                    out_writer.writerow(file_lines[0].split(','))
                    out_writer.writerow(file_lines[1].split(','))
                temp = []
                for line in file_lines[2:]:
                    temp.append(line)
                data.append(temp)
        if verbose:
            print(f'  Read {len(data)} files each with {len(data[0])} data lines')

        for i in range(0, len(data[0])):
            for j in range(0, len(data)):
                temp = data[j][i].split(',')
                year = temp[0]
                temp.pop(0)  # remove year
                temp.insert(0, j + 1)  # add subarea number (adjusted for zero-indexing)
                if j == 0:
                    ins = year
                else:
                    ins = ' '
                temp.insert(0, ins)
                out_writer.writerow(temp)
    if verbose:
        print(f'  Wrote crop data to {outfile_name} ')
    return

if __name__ == '__main__':
    ' Run detaw_2_table() from command line '
    import sys
    import iwfm.debug as idb
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    if len(sys.argv) > 1:  # arguments are listed on the command line
        dir_name = sys.argv[1]
        outfile_name = sys.argv[2]
    else:  # ask for file names from terminal
        dir_name = input('Input directory name: ')
        outfile_name = input('Output file name: ')

    idb.exe_time()  # initialize timer
    detaw_2_table(dir_name, outfile_name, verbose=verbose)
    idb.exe_time()  # print elapsed time
