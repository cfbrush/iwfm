# dicu2table.py
# Read DICU file and write out to text file
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


def dicu2table(data_file, verbose=False):
    ''' dicu2table() - Read Delta Island Consumptive Use model file and write
        out to text file

    Parameters
    ----------
    data_file : str
        name of DICU model file
    
    verbose : bool, default=False
        True = command-line output on

    Returns
    -------
    nothing
    
    '''
    import iwfm

    # find the base name and extension
    data_file_base = data_file[0 : data_file.find('.')]
    data_file_ext = data_file[data_file.find('.') + 1 : len(data_file) + 1]

    if verbose:
        print(f'  Creating data table from {data_file}')

    with open(data_file, encoding='utf-8') as f:
        file_lines = f.read().splitlines() 

    # how many lines per data set?
    set_lines = 1
    while file_lines[set_lines][0] != '/':
        set_lines += 1
    set_data = set_lines - 5

    # how many data sets are in the file?
    sets = (len(file_lines) - 1) / set_lines

    # get the dates from the first data set
    months = {'JAN': '01','FEB': '02','MAR': '03','APR': '04',
        'MAY': '05','JUN': '06','JUL': '07','AUG': '08',
        'SEP': '09','OCT': '10','NOV': '11','DEC': '12'}

    dates = []
    for i in range(4, set_lines - 1):
        dates.append(
            months[file_lines[i][2:5]]
            + '/'
            + file_lines[i][0:2]
            + '/'
            + file_lines[i][5:9]
        )

    div_table, drain_table, seep_table = [], [], []
    div_table.append(dates)
    drain_table.append(dates)
    seep_table.append(dates)

    # cycle through the data sets
    line, site_info_div, site_info_drain, site_info_seep = (
        0,
        [['ID', 'Type', 'Units']],
        [['ID', 'Type', 'Units']],
        [['ID', 'Type', 'Units']],
    )
    while line < len(file_lines) - 1:
        # get the date set ID from the first line
        temp = file_lines[line].split('/')
        site, kind = temp[2], temp[3]
        line += 3
        temp = file_lines[line].split(' ')
        site_info = [site, kind, temp[1]]
        line += 1  # now points to first data line
        temp_values = []
        for set_line in range(0, set_data):
            temp = file_lines[line].split(' ')
            temp_values.append(temp[4])
            line += 1
        if kind == 'DRAIN-FLOW':
            drain_table.append(temp_values)
            site_info_drain.append(site_info)
        elif kind == 'DIV-FLOW':
            div_table.append(temp_values)
            site_info_div.append(site_info)
        elif kind == 'SEEP-FLOW':
            seep_table.append(temp_values)
            site_info_seep.append(site_info)
        else:
            raise ValueError(f'Flow data type {kind!r} not recognized')

        line += 1  # skip 'END DATA' line


    iwfm.write_flows(
        data_file_base,
        '_drainflow',
        drain_table,
        site_info_drain,
        verbose=verbose,
    )
    iwfm.write_flows(
        data_file_base,
        '_divflow',
        div_table,
        site_info_div,
        verbose=verbose,
    )
    iwfm.write_flows(
        data_file_base,
        '_seepflow',
        seep_table,
        site_info_seep,
        verbose=verbose,
    )
    return 
