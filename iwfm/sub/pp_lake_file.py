# sub_pp_lake_file.py
# Copies the old lake file and replaces the contents with those of the new
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


def sub_pp_lake_file(lake_file, new_lake_file, lake_info):
    '''Copy the old lake file and replace the contents with those of the new model, and write out the new IWFM lake file.

    Parameters
    ----------
    lake_file : str
        name of existing preprocessor node file

    new_lake_file : str
        name of submodel preprocessor node file

    lake_info : list
        info describing of each lake in the submodel

    Returns
    -------
    nothing
    '''
    import iwfm
    from iwfm.file_utils import read_next_line_value

    iwfm.file_test(lake_file)
    with open(lake_file, encoding='utf-8') as f:
        lake_lines = f.read().splitlines()  # open and read input file

    # Skip comments and read NLAKE line
    _, line_index = read_next_line_value(lake_lines, -1, column=0, skip_lines=0)
    lake_lines[line_index] = (' ' * 4 + str(len(lake_info))).ljust(35) + ' '.join(
        lake_lines[line_index].split()[1:]
    )  # indent 4 chars, pad to 35

    # Skip to lake data section
    _, line_index = read_next_line_value(lake_lines, line_index, column=0, skip_lines=0)

    new_lake_lines = lake_lines[:line_index]

    for i in range(0, len(lake_info)):
        new_lake_lines.append(
            '\t'
            + '\t'.join(lake_info[i][0:4])
            + '\t'
            + str(lake_info[i][5][0])
            + '\t'
            + lake_info[i][4]
        )

        for j in range(1, len(lake_info[i][5])):
            new_lake_lines.append('\t\t\t\t\t' + str(lake_info[i][5][j]))

    new_lake_lines.append('')

    with open(new_lake_file, 'w', encoding='utf-8') as outfile:
        outfile.write('\n'.join(new_lake_lines))

    return
