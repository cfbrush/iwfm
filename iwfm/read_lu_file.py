# read_lu_file.py
# Read IWFM land use file
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


'''Read IWFM land use file.'''

def read_lu_file(filename, skip=4):
    '''Read an IWFM land use file and return a list of acrage data.

    The list dimensions are (no. elements)x(no. land use types or crops)x(no. time steps)

    Parameters
    ----------
    filename : str
        IWFM lane use file name

    skip : int, default=4
        number of header rows to skip

    Returns
    -------
    table : list
        land use data

    dates : list
        DSS dates for each time step
    '''
    import iwfm

    comments = 'Cc*#'

    iwfm.file_test(filename)
    with open(filename, encoding='utf-8') as f:
        data = f.read().splitlines()

    # -- find the file line with the first element's data
    index = 0
    while any((c in comments) for c in data[index][0]):
        index += 1
    index += skip  # skip data spec rows
    while any((c in comments) for c in data[index][0]): 
        index += 1

    # -- compile the data from the file
    table, elems, dates, temp_elems, temp_table = [], [], [], [], []
    line = data[index].split()

    while index < len(data):
        line = data[index].split()
        # if first item is a date, then clean up and start a new table

        if '24:00' in line[0]:  # finish the last time period and start a new one
            date = line.pop(0)  # remove the date
            dates.append(date)
            if len(temp_table) > 0:  # temp_table is empty for the first time period
                table.append(temp_table)
                elems.append(temp_elems)
            temp_table, temp_elems = [], []
        elem = int(line.pop(0))
        temp_elems.append(elem)
        for j in range(0, len(line)):
            line[j] = float(line[j])
        temp_table.append(line)
        index += 1
    elems.append(temp_elems)  # for the last time period
    table.append(temp_table)  # for the last time period

    return table, dates, elems
