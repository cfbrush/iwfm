# sub_pp_node_list.py
# Reads the element file and returns a list of the nodes in the submodel
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


'''Read the element file and returns a list of the nodes in the submodel.'''

def sub_pp_node_list(elem_file, elem_list):
    '''Read the element file and return a list of the nodes in the submodel.

    Parameters
    ----------
    elem_file : str
        existing model preprocessor element file name

    elem_list : list of ints
        list of existing model elements in submodel

    Returns
    -------
    node_list : list of ints
        list of existing model nodes in submodel
    '''
    import iwfm
    from iwfm.file_utils import read_next_line_value

    elems = []
    for e in elem_list:
        elems.append(int(e[0]))

    iwfm.file_test(elem_file)
    with open(elem_file, encoding='utf-8') as f:
        elem_lines = f.read().splitlines()  # open and read input file

    # Skip comments to NE line
    _, line_index = read_next_line_value(elem_lines, -1, column=0, skip_lines=0)
    # -- skip to number of subregions
    _, line_index = read_next_line_value(elem_lines, line_index, column=0, skip_lines=0)

    # get number of subregions
    subs = int(elem_lines[line_index][0:15])

    # -- skip to start of subregion list
    _, line_index = read_next_line_value(elem_lines, line_index, column=0, skip_lines=0)

    # -- skip the subregion lines to reach start of element list
    _, line_index = read_next_line_value(elem_lines, line_index, column=0, skip_lines=subs - 1)

    # -- get node list from element list
    node_list = []
    for i in range(line_index, len(elem_lines)):
        temp = [int(n) for n in elem_lines[i].split()]
        elem = temp[0]
        nodes = temp[1:5]
        if elem in elems:
            for node in nodes:
                if node not in node_list:
                    node_list.append(node)
    node_list.sort()
    # remove 0, it is not a node number, just indicates a triangular element
    if (node_list[0] == 0):
        node_list.pop(0)
    return node_list
