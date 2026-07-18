# stacdep2obs.py
# Convert IWFM Stream Reach Budget to the SMP file format for 
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
    '''Read IWFM Stream Reach budget file and process into a table of individual stream reach stream-groundwater flows.

    Parameters
    ----------        
    budget_file: str
        Name of IWFM Stream Nodes budget file

    cwidth : int, default = 12
            Width of column in budget file

    Returns
    -------
    budget_table, list
        Stream-groundwater flows for each reach

    run_stacdep2obs.sh, list
        List of reach names

    dates, list
        List of dates for budget_table
    '''
    import numpy as np

    with open(budget_file, encoding='utf-8') as f:
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

    # Find Stream-Groundwater Column Indexes ----------------------
    i, header_indexes = 0, []
    line = budget_lines[header_len + 3]     # get column widths
    while i < len(line):
        while i < len(line) and line[i] != ' ':
            i += 1
        header_indexes.append(i)
        while i < len(line) and line[i] == ' ':
            i += 1
    # find index of each instance of 'Gain from GW' 
    i, loc, hline = 0, [], budget_lines[3] # header line
    while i < len(hline):
        if hline[i:i+cwidth] == 'Gain from GW':
            loc.append(i)
        i += 1
    stac_cols = []
    for item in loc:
        i = 0
        while header_indexes[i] < item:
            i += 1
        stac_cols.append(i)

    # Read budget tables' stream-gw column ---------------------------
    budget_table, table_line = [], 0
    while table_line < len(budget_lines):
        table_line += header_len
        temp = []
        while  len(budget_lines[table_line]) > 1:
            t, t1 = budget_lines[table_line].split(), 0
            for i in stac_cols:
                t1 += float(t[i])    # add inside and outside columns
            temp.append(t1)
            table_line += 1
        temp = np.array(temp)        # convert temp to numpy array
        budget_table.append(temp)
        table_line += 2 # skip empty lines

    return budget_table, reach_list, dates


def format_stacdep_smp(budget_table, dates, reaches, nwidth=20):
    '''Format already-parsed budget data into SMP stream-depletion rows and matching PEST INS instructions.

    This is the pure formatting half of :func:`stacdep2obs`, exposed so
    callers (and unit tests) can drive it without reading files.

    Parameters
    ----------
    budget_table: list
        One numpy array per stream reach. ``budget_table[n - 1]`` is the
        stream-groundwater (inside + outside model) time series for the
        1-based reach number ``n``.
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
    stacdep: list
        SMP-format stream-depletion rows.
    ins: list
        Matching PEST INS instructions for the SMP file.

    Raises
    ------
    IndexError
        If a group's ``reach_nums`` references a 1-based reach number
        that exceeds ``len(budget_table)``.
    ValueError
        If a date in ``dates`` does not match the expected
        ``M/D/YYYY`` or ``MM/DD/YYYY`` format.
    '''
    smp_dates, ins_dates = [], []
    for date in dates:
        temp = [int(i) for i in date.split('/')]
        smp_dates.append(f'{temp[0]:02d}/{temp[1]:02d}/{temp[2]}')
        temp = date.split('/')
        ins_dates.append(f'{temp[0]}{temp[2]}')

    stacdep, ins = [], []
    for reach in reaches:
        reach_name_field = reach[0].ljust(nwidth)
        reach_nums = reach[1]
        # Sum across all reaches in the group. Use `+` (not `+=`) so we never
        # mutate the caller's arrays.
        budget = budget_table[reach_nums[0] - 1]
        for n in reach_nums[1:]:
            budget = budget + budget_table[n - 1]
        for i in range(len(budget)):
            smp_out = f'{reach_name_field} {smp_dates[i]}  0:00:00   {budget[i]}'
            ins_out = f'l1  [{reach[0]}_{ins_dates[i]}]41:56'
            stacdep.append(smp_out)
            ins.append(ins_out)
    return stacdep, ins


def stacdep2obs(budget_file, reach_file, nwidth=20):
    '''Convert stream-groundwater flows from IWFM Stream Budget to the SMP file format for use by PEST.

    (Based on STACDEP2OBS.F90 by Matt Tonkin, SSPA with routines by John Doherty.)

        Reads ``budget_file`` and ``reach_file``, then delegates the SMP/INS
        formatting to :func:`format_stacdep_smp`. Use that helper directly if
        you already have parsed budget data.

    Parameters
    ----------
    budget_file: str
        Path to the IWFM stream budget output file (e.g.
        ``C2VSimCG_Streams_Budget.bud``).

    reach_file: str
        Path to the reach groups file (e.g. ``stgwgroups.in``). See
        :func:`iwfm.calib.divshort2obs.read_reaches` for format details.

    nwidth: int, default=20
        Width of the name column in SMP output.

    Returns
    -------
    stacdep : list
        Stream-depletion observation values for each group in SMP format.

    ins : list
        Corresponding PEST instructions for the SMP file.

    Raises
    ------
    FileNotFoundError
        If ``reach_file`` does not exist.
    IndexError
        If any group references a reach number beyond the budget file's
        reach count (propagated from :func:`format_stacdep_smp`).
    ValueError
        If the budget or reach file is malformed (numeric tokens fail
        to parse).
    '''
    from iwfm.calib.divshort2obs import read_reaches

    budget_table, _reach_list, dates = process_budget(budget_file)
    reaches = read_reaches(reach_file)
    return format_stacdep_smp(budget_table, dates, reaches, nwidth=nwidth)


if __name__ == "__main__":
    ''' Run stacdep2obs() from command line '''

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
        reach_file    = input("Reach list file name.: ")
        output_file   = input("Output SMP file name: ")

    file_test(budget_file)
    file_test(reach_file)

    outins_file = output_file.replace('.smp','.ins')

    exe_time()  # initialize timer

    # read input files and process
    stacdep, ins = stacdep2obs(budget_file, reach_file)

    # write results to output smp file
    with open(output_file, 'w', encoding='utf-8') as out_file:
        for item in stacdep:
            out_file.write(f'{item}\n')

    # write results to output ins file
    with open(outins_file, 'w', encoding='utf-8') as out_file:
        out_file.write('pif #\n')
        for item in ins:
            out_file.write(f'{item}\n')

    print(f'\n  Read {budget_file} and wrote {output_file} and {outins_file}.')  # update cli

    exe_time()  # print elapsed time

  