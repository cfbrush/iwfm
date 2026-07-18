# sub_rz_npc_file.py
# Copy the rootzone non-ponded crops main file and replace the contents 
# with those of the new submodel, write out the new file, and 
# process the other non-ponded crop files
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


def sub_rz_npc_file(old_filename, sim_files_new, elems, base_path=None, verbose=False):
    '''Copy the rootzone non-ponded crops main file and replace the contents with those of the new submodel, write out the new file, and process the other non-ponded crop files.

    Parameters
    ----------
    old_filename : str
        name of existing model non-ponded crops main file

    sim_files_new : SimulationFiles
        new submodel file names

    elems : list of ints
        list of existing model elements in submodel

    base_path : Path, optional
        base path for resolving relative file paths

    verbose : bool, default=False
        turn command-line output on or off

    Returns
    -------
    nothing
    '''
    import iwfm
    from iwfm.file_utils import read_next_line_value

    comments = ['C','c','*','#']

    # Use iwfm utility for file validation
    iwfm.file_test(old_filename)

    with open(old_filename, encoding='utf-8') as f:
        npc_lines = f.read().splitlines()
    npc_lines.append('')

    _, line_index = read_next_line_value(npc_lines, -1, column=0, skip_lines=0)  # skip initial comments
    ncrop = int(npc_lines[line_index].split()[0])                # number of crop types

    # non-ponded crop area file name
    _, line_index = read_next_line_value(npc_lines, line_index, column=0, skip_lines=1 + ncrop)  # skip factors
    nparea_file = npc_lines[line_index].split()[0]               # original crop area file name
    nparea_file = nparea_file.replace('\\', '/')                  # convert backslashes to forward slashes
    # Resolve relative path from simulation base directory if provided
    if base_path is not None:
        nparea_file = str(base_path / nparea_file)
    npc_lines[line_index] = '   ' + sim_files_new.npa_file + '		        / LUFLNP'

    # budget section
    _, line_index = read_next_line_value(npc_lines, line_index, column=0, skip_lines=0)  # skip comments
    nbud = int(npc_lines[line_index].split()[0])                 # number of crop budgets
    _, line_index = read_next_line_value(npc_lines, line_index, column=0, skip_lines=2 + nbud)  # skip budget section

    _, line_index = read_next_line_value(npc_lines, line_index, column=0, skip_lines=1)  # skip file name and factor
    _, line_index = read_next_line_value(npc_lines, line_index, column=0, skip_lines=ncrop - 1)  # skip crop root depths

    line_index = iwfm.sub_remove_items(npc_lines, line_index, elems)    # curve numbers

    line_index = iwfm.sub_remove_items(npc_lines, line_index, elems)    # crop ETc

    line_index = iwfm.sub_remove_items(npc_lines, line_index, elems)    # ag water supply requirement

    line_index = iwfm.sub_remove_items(npc_lines, line_index, elems)    # irrigation periods

    line_index = iwfm.sub_remove_items(npc_lines, line_index, elems, skip=1)    # minimum soil moisture

    line_index = iwfm.sub_remove_items(npc_lines, line_index, elems, skip=1)    # target soil moisture

    line_index = iwfm.sub_remove_items(npc_lines, line_index, elems)    # return flow fractions

    line_index = iwfm.sub_remove_items(npc_lines, line_index, elems)    # reuse fractions

    # initial conditions - process manually because end of file
    _, line_index = read_next_line_value(npc_lines, line_index, column=0, skip_lines=0)  # skip file name and comments
    # Check bounds before accessing - skip_ahead returns -1 at end of file
    if (line_index >= 0 and
        line_index < len(npc_lines) and
        npc_lines[line_index].strip() and
        int(npc_lines[line_index].split()[0]) > 0):
        # Loop while current line is not a comment and not empty
        while (line_index < len(npc_lines) and
               npc_lines[line_index] and
               npc_lines[line_index][0] not in comments):
            if int(npc_lines[line_index].split()[0]) not in elems:
                del npc_lines[line_index]
            else:
                line_index += 1

    npc_lines.append('')

    with open(sim_files_new.np_file, 'w', encoding='utf-8') as outfile:
        outfile.write('\n'.join(npc_lines))
    if verbose:
        print(f'      Wrote non-ponded crop file {sim_files_new.np_file}')


    # -- non-ponded crop area file --
    iwfm.sub_lu_file(nparea_file, sim_files_new.npa_file, elems, verbose=verbose)


    return

