# sub_pp_node_file.py
# Copies the old node file and replaces the contents with those of the new
# submodel, and writes out the new file
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


def sub_pp_node_file(node_file, new_node_file, node_list):
    '''Copy the original node file, replace the contents with those of the new model, and write out the new file.

    Parameters
    ----------
    node_file : str
        name of existing preprocessor node file

    new_node_file : str
        name of submodel preprocessor node file

    node_list : llist of ints
        list of submodel nodes

    Returns
    -------
    nothing
    '''
    import iwfm
    from iwfm.file_utils import read_next_line_value

    iwfm.file_test(node_file)
    with open(node_file, encoding='utf-8') as f:
        node_lines = f.read().splitlines()  # open and read input file

    # Skip comments and read ND line
    _, line_index = read_next_line_value(node_lines, -1, column=0, skip_lines=0)
    node_lines[line_index] = (' ' * 4 + str(len(node_list))).ljust(35) + ' '.join(
        node_lines[line_index].split()[1:])  # indent 4 chars, pad to 35

    # Skip FACT line and comments to node data section
    _, line_index = read_next_line_value(node_lines, line_index, column=0, skip_lines=1)

    new_node_lines = node_lines[:line_index]

    for i in range(line_index, len(node_lines)):
        if int(node_lines[i].split()[0]) in node_list:
            new_node_lines.append(node_lines[i])
    new_node_lines.append('')

    with open(new_node_file, 'w', encoding='utf-8') as outfile:
        outfile.write('\n'.join(new_node_lines))

    return
