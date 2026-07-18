# sub_pp_elem_file.py
# Copies the old element file and replaces the contents with those of the new
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


'''Copy the old element file and replaces the contents with those of the new submodel, and writes out the new file.'''

def sub_pp_elem_file(elem_file, new_elem_file, elem_list, new_srs):
    '''Copy the old element file and replace the contents with those of the new model, and write out the new file.

    Parameters
    ----------
    elem_file : str
        name of existing preprocessor element file

    new_elem_file : str
        name of submodel preprocessor element file

    elem_list : list of ints
        list of submodel elements

    new_srs : list of ints
        list of submodel subregions

    Returns
    -------
    elem_nodes : list of lists of ints
        list of [element id, nodes and subregion] for each submodel element
    '''
    import iwfm
    from iwfm.file_utils import read_next_line_value

    comments = ['C','c','*','#']

    elems = []
    for e in elem_list:
        elems.append(e[0])

    iwfm.file_test(elem_file)
    with open(elem_file, encoding='utf-8') as f:
        elem_lines = f.read().splitlines()  # open and read input file

    # Skip comments and read NE line
    _, line_index = read_next_line_value(elem_lines, -1, column=0, skip_lines=0)
    elem_lines[line_index] = (' ' * 4 + str(len(elem_list))).ljust(35) + ' '.join(
        elem_lines[line_index].split()[1:]
    )  # indent 4 chars, pad to 35

    # Skip to NREGN line
    _, line_index = read_next_line_value(elem_lines, line_index, column=0, skip_lines=0)
    elem_lines[line_index] = (' ' * 4 + str(len(new_srs))).ljust(35) + ' '.join(
        elem_lines[line_index].split()[1:]
    )  # indent 4 chars, pad to 35

    # Skip to first subregion line
    _, line_index = read_next_line_value(elem_lines, line_index, column=0, skip_lines=0)

    for sr in range(0, len(new_srs)):
        elem_lines[line_index] = (' ' * 4 + 'Subregion ' + str(new_srs[sr])).ljust(25) + ' '.join(elem_lines[line_index].split()[2:])  # indent 4 chars, pad to 25
        # Skip to next subregion line
        _, line_index = read_next_line_value(elem_lines, line_index, column=0, skip_lines=0)
    # remove the remaining 'Subregion' lines
    while elem_lines[line_index][0] not in comments:
        del elem_lines[line_index]

    # Skip to element data section
    _, line_index = read_next_line_value(elem_lines, line_index, column=0, skip_lines=0)

    new_elem_lines = elem_lines[:line_index]

    elem_nodes = []
    for i in range(line_index, len(elem_lines)):
        if int(elem_lines[i].split()[0]) in elems:
            new_elem_lines.append(elem_lines[i])
            elem_nodes.append([int(x) for x in elem_lines[i].split()])

    new_elem_lines.append('')

    with open(new_elem_file, 'w', encoding='utf-8') as outfile:
        outfile.write('\n'.join(new_elem_lines))

    return elem_nodes
