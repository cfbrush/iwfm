# sub_pp_strat_file.py
# Copies the old strat file and replaces the contents with those of the new
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


'''Copy the original stratigraphy file and replace the contents with those of the new submodel, and write out the new file.'''

def sub_pp_strat_file(strat_file, new_strat_file, node_list):
    '''Copy the original stratigraphy file and replace the contents with those of the new submodel, and write out the new file.

    Parameters
    ----------
    strat_file : str
        name of existing preprocessor stratigraphy file

    new_strat_file : str
        name of submodel preprocessor stratigraphy file

    node_list : list of ints
        list of submodel nodes

    Returns
    -------
    nothing
    '''
    import iwfm
    from iwfm.file_utils import read_next_line_value

    iwfm.file_test(strat_file)
    with open(strat_file, encoding='utf-8') as f:
        strat_lines = f.read().splitlines() 

    while len(strat_lines[-1]) < 2:
        strat_lines.pop()

    # Skip comments to NL line
    _, line_index = read_next_line_value(strat_lines, -1, column=0, skip_lines=0)

    # Skip FACT line and comments to reach node data
    _, line_index = read_next_line_value(strat_lines, line_index, column=0, skip_lines=1)
    new_strat_lines = strat_lines[:line_index]

    for i in range(line_index, len(strat_lines)):
        if int(strat_lines[i].split()[0]) in node_list:
            new_strat_lines.append(strat_lines[i])

    new_strat_lines.append('')

    with open(new_strat_file, 'w', encoding='utf-8') as outfile:
        outfile.write('\n'.join(new_strat_lines))

    return
