# igsm_read_elements.py
# Read an IGSM pre-processor element file
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


def igsm_read_elements(elem_file):
    '''Read an IGSM Element file, and return a list of the nodes making up each element.

    Parameters
    ----------
    elem_file : str
        name of IGSM elements file

    Returns
    -------
    elem_nodes : list
        list of elements and nodes for each element

    elem_list : list
        list of elements
    '''
    import re
    import iwfm
    from iwfm.file_utils import read_next_line_value

    # -- read the Element file into array file_lines
    iwfm.file_test(elem_file)
    with open(elem_file, encoding='utf-8') as f:
        elem_lines = f.read().splitlines()  # open and read input file

    # skip comments and read number of elements
    elem_count_str, line_index = read_next_line_value(elem_lines, -1, column=0)
    elements = int(re.findall(r'\d+', elem_count_str)[0])

    # skip comments to first element data line
    _, line_index = read_next_line_value(elem_lines, line_index, column=0)

    elem_nodes, elem_list = [], []
    for i in range(0, elements):  # read element information
        l = elem_lines[line_index + i].split()
        this_elem = int(l.pop(0))
        nodes = [int(s) for s in l]
        if nodes[3] == 0:
            nodes.pop(3)  # remove empty node on triangles
        elem_nodes.append(nodes)
        elem_list.append(this_elem)
    return elem_nodes, elem_list
