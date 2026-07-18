# sub_rz_pc_file.py
# Copy the rootzone ponded crops main file and replace the contents 
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


'''Copy the rootzone ponded crops main file and replace the contents with those of the new submodel, write out the new file, and process the other non-ponded crop files.'''

def sub_rz_pc_file(old_filename, sim_files_new, elems, base_path=None, verbose=False):
    '''Copy the rootzone ponded crops main file and replace the contents with those of the new submodel, write out the new file, and process the other ponded crop files.

    Parameters
    ----------
    old_filename : str
        name of existing model ponded crop main file

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
    ncrop = 5

    # Use iwfm utility for file validation
    iwfm.file_test(old_filename)

    with open(old_filename, encoding='utf-8') as f:
        pc_lines = f.read().splitlines()
    pc_lines.append('')

    _, line_index = read_next_line_value(pc_lines, -1, column=0, skip_lines=0)  # skip initial comments

    # ponded crop area file name
    parea_file = pc_lines[line_index].split()[0]               # original crop area file name
    parea_file = parea_file.replace('\\', '/')                  # convert backslashes to forward slashes
    # Resolve relative path from simulation base directory if provided
    if base_path is not None:
        parea_file = str(base_path / parea_file)
    pc_lines[line_index] = '   ' + sim_files_new.pca_file + '		        / LUFLP'

    # budget section
    _, line_index = read_next_line_value(pc_lines, line_index, column=0, skip_lines=0)  # skip comments
    nbud = int(pc_lines[line_index].split()[0])                     # number of crop budgets
    _, line_index = read_next_line_value(pc_lines, line_index, column=0, skip_lines=2 + nbud)  # skip budget section

    _, line_index = read_next_line_value(pc_lines, line_index, column=0, skip_lines=0)  # skip factor
    _, line_index = read_next_line_value(pc_lines, line_index, column=0, skip_lines=ncrop - 1)  # skip crop root depths

    line_index = iwfm.sub_remove_items(pc_lines, line_index, elems)    # curve numbers

    _, line_index = read_next_line_value(pc_lines, line_index - 1, column=0, skip_lines=0)  # skip comments

    line_index = iwfm.sub_remove_items(pc_lines, line_index, elems)    # crop ETc

    line_index = iwfm.sub_remove_items(pc_lines, line_index, elems)    # water supply requirement

    line_index = iwfm.sub_remove_items(pc_lines, line_index, elems)    # irrigation periods

    _, line_index = read_next_line_value(pc_lines, line_index - 1, column=0, skip_lines=2)  # skip comments and two file names

    line_index = iwfm.sub_remove_items(pc_lines, line_index, elems)    # ponding depths

    line_index = iwfm.sub_remove_items(pc_lines, line_index, elems)    # application depths

    line_index = iwfm.sub_remove_items(pc_lines, line_index, elems)    # return flow depths

    line_index = iwfm.sub_remove_items(pc_lines, line_index, elems)    # re-use flow depths

    # initial conditions - process manually because end of file
    _, line_index = read_next_line_value(pc_lines, line_index - 1, column=0, skip_lines=0)  # skip file name and comments
    # Check bounds before accessing - skip_ahead returns -1 at end of file
    if (line_index >= 0 and
        line_index < len(pc_lines) and
        pc_lines[line_index].strip() and
        int(pc_lines[line_index].split()[0]) > 0):
        # Loop while current line is not a comment and not empty
        while (line_index < len(pc_lines) and
               pc_lines[line_index] and
               pc_lines[line_index][0] not in comments):
            if int(pc_lines[line_index].split()[0]) not in elems:
                del pc_lines[line_index]
            else:
                line_index += 1

    pc_lines.append('')

    with open(sim_files_new.pc_file, 'w', encoding='utf-8') as outfile:
        outfile.write('\n'.join(pc_lines))
    if verbose:
        print(f'      Wrote ponded crop file {sim_files_new.pc_file}')

    # -- ponded crop area file --
    iwfm.sub_lu_file(parea_file, sim_files_new.pca_file, elems, verbose=verbose)

    return



