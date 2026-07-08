# sub_rz_nv_file.py
# Copy the rootzone native and riparian main file and replace the contents 
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


def sub_rz_nv_file(old_filename, sim_files_new, elems, base_path=None, verbose=False):
    '''sub_rz_nv_file() - Copy the rootzone native and riparian main file
       and replace the contents with those of the new submodel, write out
       the new file, and process the other non-ponded crop files

    Parameters
    ----------
    old_filename : str
        name of existing model native and riparian main file

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
        nv_lines = f.read().splitlines()
    nv_lines.append('')

    _, line_index = read_next_line_value(nv_lines, -1, column=0, skip_lines=0)  # skip initial comments

    # native and riparian vegetation area file name
    nvarea_file = nv_lines[line_index].split()[0]               # original area file name
    nvarea_file = nvarea_file.replace('\\', '/')                  # convert backslashes to forward slashes
    # Resolve relative path from simulation base directory if provided
    if base_path is not None:
        nvarea_file = str(base_path / nvarea_file)
    nv_lines[line_index] = '   ' + sim_files_new.nva_file + '		        / LUFLNVRV'

    _, line_index = read_next_line_value(nv_lines, line_index, column=0, skip_lines=3)  # skip comments and three factors

    line_index = iwfm.sub_remove_items(nv_lines, line_index, elems)    # parameters

    # initial conditions - process manually because end of file
    _, line_index = read_next_line_value(nv_lines, line_index, column=0, skip_lines=0)  # skip file name and comments
    # Check bounds before accessing - skip_ahead returns -1 at end of file
    if (line_index >= 0 and
        line_index < len(nv_lines) and
        nv_lines[line_index].strip() and
        int(nv_lines[line_index].split()[0]) > 0):
        # Loop while current line is not a comment and not empty
        while (line_index < len(nv_lines) and
               nv_lines[line_index] and
               nv_lines[line_index][0] not in comments):
            if int(nv_lines[line_index].split()[0]) not in elems:
                del nv_lines[line_index]
            else:
                line_index += 1

    nv_lines.append('')

    with open(sim_files_new.nv_file, 'w', encoding='utf-8') as outfile:
        outfile.write('\n'.join(nv_lines))
    if verbose:
        print(f'      Wrote native and riparian file {sim_files_new.nv_file}')


    # -- native and riparian area file --
    iwfm.sub_lu_file(nvarea_file, sim_files_new.nva_file, elems, verbose=verbose)


    return

