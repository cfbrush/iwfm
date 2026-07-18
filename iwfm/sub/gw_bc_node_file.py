# sub_gw_bc_node_file.py
# Copies a groundwater boundary-condition sub-file (specified flow,
# specified head, or general head), keeps the boundary conditions at
# submodel nodes, and writes out the new file
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


def sub_gw_bc_node_file(old_filename, new_filename, nodes, verbose=False):
    '''Read a groundwater boundary-condition sub-file (specified flow, specified head, or general head), keep the boundary conditions at submodel nodes, and write out a new file.

    The file layout shared by these BC types is: a count of boundary
    conditions (first data line), one or more single-value factor/unit
    lines, then one data line per boundary condition starting with the
    groundwater node number. The number of factor lines varies by BC
    type, so the BC table is located as the first data line with more
    than one value column.

    Parameters
    ----------
    old_filename : str
        name of existing model boundary condition sub-file

    new_filename : str
        name of new submodel boundary condition sub-file

    nodes : list of ints
        list of existing model nodes in submodel

    verbose : bool, default=False
        turn command-line output on or off

    Returns
    -------
    new_nbc : int
        number of boundary conditions in new file
    '''
    import iwfm
    from iwfm.file_utils import read_next_line_value

    if verbose: print(f"Entered sub_gw_bc_node_file() with {old_filename}")

    iwfm.file_test(old_filename)
    with open(old_filename, encoding='utf-8') as f:
        bc_lines = f.read().splitlines()
    bc_lines.append('')

    # skip initial comments to get the boundary condition count
    nbc_str, nbc_line = read_next_line_value(bc_lines, -1)
    nbc = int(nbc_str)

    # skip single-value factor/unit lines; the BC table starts at the
    # first data line with more than one value column
    line_index = nbc_line
    while True:
        _, line_index = read_next_line_value(bc_lines, line_index)
        if len(bc_lines[line_index].split('/')[0].split()) > 1:
            break

    # remove lines for nodes that are not in the submodel
    new_nbc = 0
    for _ in range(nbc):
        if int(bc_lines[line_index].split()[0]) not in nodes:
            del bc_lines[line_index]
        else:
            line_index += 1
            new_nbc += 1

    # rewrite the count, preserving the original description text
    parts = bc_lines[nbc_line].split('/', 1)
    tail = '/ ' + parts[1].strip() if len(parts) > 1 else '/ NBC'
    bc_lines[nbc_line] = ('     ' + str(new_nbc)).ljust(30) + tail

    with open(new_filename, 'w', encoding='utf-8') as outfile:
        outfile.write('\n'.join(bc_lines))

    if verbose:
        print(f'      Wrote boundary condition file {new_filename}')
        print("Leaving sub_gw_bc_node_file()")

    return new_nbc
