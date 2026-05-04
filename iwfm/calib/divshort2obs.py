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
    """ read_reaches() - Read group definitions of stream reaches.

        File format (e.g. ``stgwgroups.in``):

            maxpergroup  <N>
            numrchgroup <M>
            groupname<sep>num_per_group<sep>reach_nums...
            <name><sep><num_per_group><sep><reach_num>[<sep><reach_num>...]
            ...

        The first three lines are header/control and are skipped. Each
        subsequent data line names a group and lists ``num_per_group`` stream
        reach numbers belonging to it. Within a data line the separators
        between reach numbers can be tabs, spaces, OR commas (or any mix);
        ``num_per_group`` controls how many of the trailing tokens are read.

        Parameters
        ----------
        reach_file: str
            Path to the reach groups file (e.g. stgwgroups.in)

        Returns
        -------
        reaches: list
            One entry per group, ``[name, [reach_num, ...]]``. Reach numbers
            are 1-based integers as they appear in the budget file.

        Raises
        ------
        FileNotFoundError
            If ``reach_file`` does not exist (raised by ``open``).
        ValueError
            If a data line's ``num_per_group`` token cannot be parsed as
            ``int``, or if any reach number token cannot be parsed.
    """
    with open(reach_file) as f:
        lines = f.read().splitlines()

    reaches = []
    for line in lines[3:]:
        if not line.strip():
            continue
        # Treat tabs, spaces, and commas all as separators so the file
        # can mix delimiters (e.g. "Sacr_1\t4\t55,56,58\t66").
        tokens = line.replace(',', ' ').split()
        if len(tokens) < 2:
            continue
        name = tokens[0]
        num_per_group = int(tokens[1])
        reach_nums = [int(x) for x in tokens[2:2 + num_per_group]]
        reaches.append([name, reach_nums])
    return reaches


def format_divshort_smp(budget_table, dates, reaches, nwidth=20):
    """ format_divshort_smp() - Format already-parsed budget data into SMP
        diversion-shortage rows and matching PEST INS instructions.

        This is the pure formatting half of :func:`divshort2obs`, exposed so
        callers (and unit tests) can drive it without reading files.

        Parameters
        ----------
        budget_table: list
            One numpy array per stream reach. ``budget_table[n - 1]`` is the
            diversion-shortage time series for the 1-based reach number ``n``.
        dates: list
            Dates corresponding to each row of ``budget_table[i]``, formatted
            as 'M/D/YYYY' or 'MM/DD/YYYY'.
        reaches: list
            Group definitions: ``[[name, [reach_num, ...]], ...]``. When a
            group has multiple reach numbers, their values are summed.
        nwidth: int, default=20
            Width of the name column in SMP output.

        Returns
        -------
        divshort: list
            SMP-format diversion shortage rows.
        ins: list
            Matching PEST INS instructions for the SMP file.

        Raises
        ------
        IndexError
            If a group's ``reach_nums`` references a 1-based reach number
            that exceeds ``len(budget_table)``. Pre-filter your groups
            against the budget reach count to avoid this.
        ValueError
            If a date in ``dates`` does not match the expected
            ``M/D/YYYY`` or ``MM/DD/YYYY`` format.
    """
    smp_dates, ins_dates = [], []
    for date in dates:
        temp = [int(i) for i in date.split('/')]
        smp_dates.append(f'{temp[0]:02d}/{temp[1]:02d}/{temp[2]}')
        temp = date.split('/')
        ins_dates.append(f'{temp[0].rjust(2, "0")}{temp[2]}')

    divshort, ins = [], []
    for reach in reaches:
        reach_name_field = reach[0].ljust(nwidth)
        reach_nums = reach[1]
        # Sum the diversion shortage across all reaches in the group.
        # Use `+` (not `+=`) so we never mutate the caller's arrays.
        budget = budget_table[reach_nums[0] - 1]
        for n in reach_nums[1:]:
            budget = budget + budget_table[n - 1]
        for i in range(len(budget)):
            smp_out = f'{reach_name_field} {smp_dates[i]}  0:00:00   {budget[i]}'
            ins_out = f'l1  [{reach[0]}_{ins_dates[i]}]45:56'
            divshort.append(smp_out)
            ins.append(ins_out)
    return divshort, ins


def divshort2obs(budget_file, reach_file, nwidth=20):
    ''' divshort2obs() - Convert diversion shortages from IWFM Stream Budget
        to the SMP file format for use by PEST. (Based on STACDEP2OBS.F90 by
        Matt Tonkin, SSPA with routines by John Doherty.)

        Reads ``budget_file`` and ``reach_file``, then delegates the SMP/INS
        formatting to :func:`format_divshort_smp`. Use that helper directly if
        you already have parsed budget data.

    Parameters
    ----------
    budget_file: str
        Path to the IWFM stream budget output file (e.g.
        ``C2VSimCG_Streams_Budget.bud``).

    reach_file: str
        Path to the reach groups file (e.g. ``stgwgroups.in``). See
        :func:`read_reaches` for format details.

    nwidth: int, default=20
        Width of the name column in SMP output.

    Returns
    -------
    divshort : list
        Diversion shortage values for each group in SMP format.

    ins : list
        Corresponding PEST instructions for the SMP file.

    Raises
    ------
    FileNotFoundError
        If ``reach_file`` does not exist.
    IndexError
        If any group references a reach number beyond the budget file's
        reach count (propagated from :func:`format_divshort_smp`).
    ValueError
        If the budget or reach file is malformed (numeric tokens fail
        to parse).

    '''
    budget_table, _reach_list, dates = process_budget(budget_file)
    reaches = read_reaches(reach_file)
    return format_divshort_smp(budget_table, dates, reaches, nwidth=nwidth)


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

  