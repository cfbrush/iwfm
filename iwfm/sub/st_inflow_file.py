# sub_st_inflow_file.py
# Copy the stream inflow file and replace the contents with those of the new
# submodel, and write out the new file
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


'''Copy the stream inflow file and replace the contents with those of the new submodel, and write out the new file.'''

def sub_st_inflow_file(old_filename, new_filename, snode_list, verbose=False):
    '''Read the original stream inflow file, determine which stream nodes are in the submodel, and write out a new file.

    Parameters
    ----------
    old_filename : str
        name of existing model element ppumping file

    new_filename : str
        name of new subnmodel element pumpgin file

    snode_list : list of ints
        list of existing model stream nodes in submodel

    verbose : bool, default=False
        turn command-line output on or off

    Returns
    -------
    nothing
    '''
    import iwfm
    from iwfm.file_utils import read_next_line_value

    # Check if inflow file exists using iwfm utility
    iwfm.file_test(old_filename)

    with open(old_filename, encoding='utf-8') as f:
        inflow_lines = f.read().splitlines()
    inflow_lines.append('')

    _, line_index = read_next_line_value(inflow_lines, -1, column=0, skip_lines=0)  # skip initial comments

    # -- inflows
    ninflows = int(inflow_lines[line_index].split()[0])             # number of inflows

    _, line_index = read_next_line_value(inflow_lines, line_index - 1, column=0, skip_lines=5)  # skip factors

    for j in range(0, ninflows):
        t = inflow_lines[line_index].split()
        if int(t[0]) not in snode_list:
            t[0] = '0'
            inflow_lines[line_index] = '\t' + ' '.join(t)
        line_index += 1


    inflow_lines.append('')

    with open(new_filename, 'w', encoding='utf-8') as outfile:
        outfile.write('\n'.join(inflow_lines))
    if verbose:
        print(f'      Wrote stream inflow file {new_filename}')

    return
