# read_elements_csv.py
# Read elements from csv file
# Copyright (C) 2024 University of California
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

def read_elements_csv(elem_file_name):
    ''' read_elements_csv - Read elements from csv file

    Parameters
    ----------
    elem_file_name : str
        name of the file containing the elements

    Return
    ------
    elem_ids : list
        element ids

    elem_nodes : list
        list of node ids for each element
    
    '''
    import csv as csv

    elem_ids = []
    elem_nodes = []

    with open(elem_file_name, encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for line in csv_reader:
            if line_count > 0 and len(line) > 1:
                elem_nodes.append([int(n) for n in line])
                elem_ids.append(int(line[0]))
            line_count += 1

    return elem_ids, elem_nodes
