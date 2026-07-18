# get_heads_4_date.py
# Read headall.out file and return heads for a specific date
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

import iwfm
import numpy as np


def get_heads_4_date(heads_file, out_date, start=5):
    '''Read headall.out file and return heads for a specific date.

    Parameters
    ----------
    heads_file : str
        name of IWFM headall.out file

    out_date : str
        date in MM/DD/YYYY format

    start : int, default=5
        number of header lines to skip

    Returns
    -------
    out_table : numpy.ndarray or None
        2D array of head values, or None if date not found
    nodes : list
        List of node names
    header : list
        List of header labels (Node + Layer labels)
    '''
    date_parts = out_date.split('/')  # parse date components
    out_mon, out_day, out_year = int(date_parts[0]), int(date_parts[1]), int(date_parts[2])

    iwfm.file_test(heads_file)
    with open(heads_file, encoding='utf-8') as f:
        file_lines = f.read().splitlines()  # open and read input file

    line_index = start
    nodes = file_lines[line_index].split()  # read line w/node nos
    nodes.pop(0)  # remove "Node" text

    data = []

    line_index += 1
    item = file_lines[line_index].split()  # read line w/date
    data.append(item)
    end_date = item.pop(0)  # remove the date

    while True:
        # Read all layer lines for this timestep
        layer = 1
        header = []
        header.append('Node')
        header.append('Layer ' + str(layer))

        line_index += 1
        while line_index < len(file_lines) and file_lines[line_index] and file_lines[line_index][0].isspace():  # get all the lines for this time step
            item = file_lines[line_index].split()
            data.append(item)
            layer += 1
            header.append('Layer ' + str(layer))
            line_index += 1

        # now check the date
        date_parts2 = end_date[0:10].split('/')  # parse date components
        m, d, y = int(date_parts2[0]), int(date_parts2[1]), int(date_parts2[2])
        if m == out_mon and d == out_day and y == out_year:
            out_table = np.asarray(data)
            return out_table, nodes, header

        # Date doesn't match, try next timestep
        if line_index >= len(file_lines):
            break

        data = []
        item = file_lines[line_index].split()  # read line w/date
        data.append(item)
        end_date = item.pop(0)  # remove the date

    return None
