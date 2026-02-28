# divshort2obs.py
# Convert Diversion Shortages from IWFM Stream Budget to the SMP file format for 
# use by PEST.
# Based on STACDEP2OBS.F90 by Matt Tonkin, SSPA with routines by John Doherty
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


def process_budget(budget_file, cwidth=12):
    """ process_budget() - Read IWFM Stream Budget file and process into
        a table of diversion shortage cols for each reach
        
        Parameters
        ----------        
        budget_file: str
            Name of IWFM Stream Nodes budget file

        Returns
        -------
        budget_lines, list
            Data from budget tables

        node_list, list
            List of node numbers for tables
    """
    import numpy as np

    with open(budget_file) as f:
        budget_lines = f.read().splitlines()

    # How many lines per table? ----------------------------------
    table_len, header_lines, dates = 0, [], []
    while budget_lines[table_len][0] != '-': # skip label lines
        table_len += 1
    table_len += 1                           # top of header
    while budget_lines[table_len][0] != '-': # read header lines
        header_lines.append(budget_lines[table_len])
        table_len += 1
    table_len += 1                           # skip line
    header_len = table_len                   # lines to skip when reading each table
    while len(budget_lines[table_len]) > 10:  # read times
        dates.append(budget_lines[table_len].split()[0].replace("_24:00",""))
        table_len += 1
    table_len += 2                           # padding at end of each table

    # Get reach numbers for tables --------------------------------
    reach_line, reach_list = 1, []           # first reach number, accumulator
    while reach_line < len(budget_lines) - 10:
        reach_list.append(int(budget_lines[reach_line].split()[-1][:-1]))
        reach_line += table_len              # skip to next one

    # Find Diversion Shortage Column Index ----------------------
    i, header_indexes = 0, []
    line = budget_lines[header_len + 3]     # get column widths
    while i < len(line):
        while i < len(line) and line[i] != ' ':
            i += 1
        header_indexes.append(i)
        while i < len(line) and line[i] == ' ':
            i += 1

    # find index of each instance of 'Shortage' 
    i, loc, hline = 0, [], budget_lines[4] # header line
    while i < len(hline):
        if hline[i:i+cwidth] == 'Shortage':
            loc= int(i)-4
        i += 1

    # Read budget tables' diversion shortage column ---------------------------
    budget_table, table_line = [], 0
    while table_line < len(budget_lines):
        table_line += header_len
        temp = []
        while  len(budget_lines[table_line]) > 1:
            t = float(budget_lines[table_line][loc:])
            temp.append(t)
            table_line += 1
        temp = np.array(temp)        # convert temp to numpy array
        budget_table.append(temp)
        table_line += 2 # skip empty lines

    return budget_table, reach_list, dates


def read_reaches(reach_file):
    """ read_reaches() - Read list of reaches and stream nodes
        
        Parameters
        ----------        
        reach_file: str
            Name of reach list file

        Returns
        -------
        reach_list: list
            Observation names and associates stream reaches
    """

    with open(reach_file) as f:
        reach_list = f.read().splitlines()

    reaches = []
    for line in reach_list[1:]: # skip header lines
        temp = line.split()
        reaches.append([temp[0],int(temp[1])])
    return reaches


def divshort2obs(budget_file, reach_file, nwidth=20):
    ''' divshort2obs() - Convert diversion shortages from IWFM Stream Budget 
        to the SMP file format for use by PEST. (Based on STACDEP2OBS.F90 by Matt 
        Tonkin, SSPA with routines by John Doherty.)

    Parameters
    ----------
    budget_table: list
        Numpy arrays of stream-groundwater flows (inside and outside model)for 
        each stream node

    dates: list
        Dates for budget rows
    
    reaches: list
        List of ouput reaches, containing [name, [reach nos]]

    nwidth: int, default = 20
        Width of name column

    Returns
    -------
    divshort : list 
        Diversion shortage values for each reach in smp format

    ins : list 
        Corresponding Pest instructions for smp file

    '''
    import iwfm 

    # read input files
    budget_table, reach_list, dates = process_budget(budget_file)

    reaches = read_reaches(reach_file)



    # dates to 'MM/DD/YYY'
    smp_dates, ins_dates = [], []
    for date in dates:       # convert date from text m/d/yy to mm/dd/yyyy
        temp = [int(i) for i in date.split('/')]
        smp_dates.append(f'{temp[0]:02d}/{temp[1]:02d}/{temp[2]}')  # format as MM/DD/YYYY
        temp = date.split('/')
        ins_dates.append(f'{temp[0].rjust(2, "0")}{temp[2]}')  # right-justify to 2 chars 

    divshort, ins = [], []
    for reach in reaches:
        reach_name = reach[0].ljust(nwidth)   # left-justify to nwidth chars
        reach_num = reach[1]-1

        # sum the reach values
        budget = budget_table[reach_num]

        for i in range(len(budget)):
            smp_out = f'{reach_name} {smp_dates[i]}  0:00:00   {budget[i]}' # smp format
            ins_out = f'l1  [{reach[0]}_{ins_dates[i]}]45:56'
            divshort.append(smp_out)
            ins.append(ins_out)

    return divshort, ins


if __name__ == "__main__":
    ''' Run divshort2obs() from command line '''

    import sys
    from iwfm import file_test
    from iwfm.debug import parse_cli_flags, exe_time

    verbose, debug = parse_cli_flags()
  
    if len(sys.argv) > 1:  # arguments are listed on the command line
        budget_file  = sys.argv[1]
        reach_file   = sys.argv[2]
        output_file  = sys.argv[3]
    else:                                                      # ask for file names from terminal
        budget_file   = input("Input Stream Budget file name: ")
        reach_file    = input("Stream file name: ")
        output_file   = input("Output SMP file name: ")

    file_test(budget_file)
    file_test(reach_file)

    exe_time()  # initialize timer

#    # read input files
#    budget_table, reach_list, dates = process_budget(budget_file)
#
#    reaches = read_reaches(reach_file)

    # process
    divshort, ins = divshort2obs(budget_file, reach_file)

    # write results to output smp file
    with open(output_file, 'w') as out_file:
        for item in divshort:
            out_file.write(f'{item}\n')

    # write results to output ins file
    outins_file = output_file.replace('.smp','.ins')
    with open(outins_file, 'w') as out_file:
        out_file.write(f'pif #\n')
        for item in ins:
            out_file.write(f'{item}\n')

    print(f'  Read {budget_file} and wrote {output_file} and {outins_file}.')  # update cli

    exe_time()  # print elapsed time

  