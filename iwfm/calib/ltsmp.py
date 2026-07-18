# ltsmp.py
# Read a PEST SMP file, and log-transform the observation values
# Copyright (C) 2018-2026 University of California
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


import iwfm


def ltsmp(input_file, output_file, zero_offset=36.0, neg_val=0.001):
    '''Read a PEST SMP-format file, log-transform the observation values, and write to a SMP-format file.

    Parameters
    ----------
    input_file : str
        SMP-format input file name

    output_file : str
        output file name

    zero_offset : int or float
        number to add to zero values

    neg_val : int or float
        number to replace negative values

    Returns
    -------
    nothing
    '''

    with open(input_file, encoding='utf-8') as f:
        file_lines = f.read().splitlines()          # open and read input file

    out_lines = []
    for line in file_lines:
        length = len(line)
        i = len(line) - 1
        while line[i] == ' ':
          i -= 1
        while line[i] != ' ':
          i -= 1
        while line[i] == ' ':
          i -= 1
        i += 1
        head = line[0:i]
        q = float(line[i:])
        out = f'{head}               {iwfm.logtrans(q, zero_offset, neg_val):.4f}'
        out_lines.append(out.ljust(length))  # left-justify to length chars
    
    with open(output_file, 'w', encoding='utf-8') as out_file:
        for i in range(0,len(out_lines)):
            out_file.write(f'{out_lines[i]}\n')


if __name__ == "__main__":
    ''' Run ltsmp() from command line '''
    import sys
    import iwfm
    import iwfm.debug as idb
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()
  
    if len(sys.argv) > 1:  # arguments are listed on the command line
        input_file  = sys.argv[1]
        output_file = sys.argv[2]
        zero_offset = float(sys.argv[3])
        neg_val     = float(sys.argv[4])
    else:                                                      # ask for file names from terminal
        input_file   = input("Input SMP file name: ")
        output_file  = input("Output SMP file name: ")
        zero_offset  = float(input("Value to add to zero: "))
        neg_val      = float(input("Value to replace negative no.: "))

    iwfm.file_test(input_file)
    iwfm.file_validate_path(output_file)

    idb.exe_time()  # initialize timer
    ltsmp(input_file, output_file, zero_offset, neg_val)

    print(f'  Read {input_file} and wrote {output_file}.')  # update cli
    idb.exe_time()  # print elapsed time

  