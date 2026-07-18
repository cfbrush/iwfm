# ltbud.py
# Read an IWFM Budget-format output file, and log-transform the values
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


def ltbud(budget_file, output_file, zero_offset=2.0, neg_val=1.0e-7):
    '''Read an IWFM Budget-format output file and log-transform the values.

    Parameters
    ----------
    budget_file : str
        IWFM Budget-format input file name

    output_file : str
        output file name

    zero_offset : int or float
        number to add to zero values

    neg_val : int or float
        number to replace negative values

    Returns
    -------
    nothing

    TOTO: Add error code for too few budget tables
    '''

    import iwfm

    with open(budget_file, encoding='utf-8') as f:
        file_lines = f.read().splitlines()                # open and read input file

    # -- Get the Budget file header and footer lengths, number of budget tables
    header, footer, table, line, width, i = 0, 0, 1, 0, 0, 16
    while not file_lines[line][0].isdigit():                          # reads to end of header
        header += 1                                                   # to get header length
        line   += 1
    line += 1

    while file_lines[line][i + width].isspace():                      # count spaces
        width += 1
    while not file_lines[line][i + width].isspace():                  # count digits, decimal etc
        width += 1
    
    while file_lines[line][0].isdigit():                              # reads to end of dates
        table += 1                                                    # to get table length
        line  += 1
    line += 1

    if line + 5 < len(file_lines):    # budget file contains more than one table
        while len(file_lines[line])==0 or not file_lines[line][0].isdigit():     # reads to end of next header
            footer += 1
            line   += 1
    footer = footer + 1 - header                                      # to get footer length
    tables = round(len(file_lines)/(header + table + footer))         # number of tables in budget file

    # -- Step through the Budget file, one table at a time
    line = 0                                                          # reset line to top of budget_table
    for t in range(0,tables):                                         # cycle through the tables
        line += header                                                # skip the header lines
        for j in range(0,table):                                      # each line in the table
            outstr = file_lines[line][:16]                            # DSS date
  
            items  = file_lines[line].split()
            for item in items[1:]:                                    # skip the date
                val = float(item)                                     # convert string to float
                outval = round(iwfm.logtrans(val,zero_offset,neg_val),3)   # log-transform
                strval = str(outval)  # convert to string
                while len(strval) < width:
                    strval = ' ' + strval                              # pad with leading spaces
                outstr += strval                                       # add to outstr
  
            file_lines[line] = outstr                                  # replace
            line += 1
        line += footer

    # -- write output file
    with open(output_file, 'w', encoding='utf-8') as out_file:
        for i in range(0,len(file_lines)):
            out_file.write("{}\n".format(file_lines[i]))

if __name__ == "__main__":
    ''' Run ltsmp() from command line '''
    import sys
    import iwfm
    import iwfm.debug as idb
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    if len(sys.argv) > 1:    # arguments are listed on the command line
        budget_file = sys.argv[1]
        output_file = sys.argv[2]
        zero_offset = float(sys.argv[3])
        neg_val     = float(sys.argv[4])
    else:                    # ask for file names from terminal
        budget_file = input("Input [Z]Budget file name: ")
        output_file = input("Output [Z]Budget file name: ")
        zero_offset = float(input("Value to add to zero: "))
        neg_val     = float(input("Value to replace negative no.: "))

    iwfm.file_test(budget_file)  # test for input file
    iwfm.file_validate_path(output_file)

    idb.exe_time()  # initialize timer
    ltbud(budget_file, output_file, zero_offset, neg_val)

    print(f'  Read {budget_file} and wrote {output_file}.')  # update cli
    idb.exe_time()  # print elapsed time
