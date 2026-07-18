# sub_remove_items.py
# Remove lines from IWFM input file block for components (elements, nodes, 
# stream nodes, etc) that are not in the submodel
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


def sub_remove_items(file_lines, line_index, items, skip=0):
    '''Remove lines for components (elements, nodes, stream nodes, etc) that are not in the submodel.

    Parameters
    ----------
    file_lines : list of strings
        each element is a line from the input file

    line_index : int
        starting line number for processing

    items : list of ints
        list of existing model compnents (elements, nodes, stream nodes, etc) in submodel

    skip : int, default=0
        number of lines to skip in addition to comments

    Returns
    -------
    line_index: int
        ending line number after processing
    '''
    from iwfm.file_utils import read_next_line_value

    comments = ['C','c','*','#']

    # Skip comments and additional lines
    _, line_index = read_next_line_value(file_lines, line_index - 1, column=0, skip_lines=skip)
    if int(file_lines[line_index].split()[0]) > 0:
        while file_lines[line_index][0] not in comments:
            if int(file_lines[line_index].split()[0]) not in items:
                del file_lines[line_index]
            else:
                line_index += 1
    else:
        line_index += 1

    return line_index
