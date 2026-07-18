# read_nodes_csv.py
# Read nodes from csv file
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

'''Read nodes from csv file.'''

def read_nodes_csv(node_file_name):
    '''Read nodes from csv file.

    Parameters
    ----------
    node_file_name : str
        name of the file containing the nodes

    Return
    ------
    node_ids : list
        node ids

    node_dict : dictionary
        Key = node id, Value = [x, y]
    '''
    import csv as csv

    node_ids = []
    node_coord_dict = {}

    with open(node_file_name, encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for line in csv_reader:
            if len(line) < 3:   # skip empty lines, usually at end of file
                break
            if line_count > 0:
                node_id, x, y = int(line[0]), float(line[1]), float(line[2])
                node_coord_dict[node_id] = [x, y]
                node_ids.append(node_id)
            line_count += 1

    return node_ids, node_coord_dict