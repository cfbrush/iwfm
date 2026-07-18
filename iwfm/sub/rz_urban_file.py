# sub_rz_urban_file.py
# Copy the rootzone urban main file and replace the contents 
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


'''Copy the rootzone urban main file and replace the contents with those of the new submodel, write out the new file, and process the other non-ponded crop files.'''

def sub_rz_urban_file(old_filename, sim_files_new, elems, base_path=None, verbose=False):
    '''Copy the rootzone urban main file and replace the contents with those of the new submodel, write out the new file, and process the other urban files.

    Parameters
    ----------
    old_filename : str
        name of existing model urban main file

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
        ur_lines = f.read().splitlines()
    ur_lines.append('')

    _, line_index = read_next_line_value(ur_lines, -1, column=0, skip_lines=0)  # skip initial comments

    urarea_file = ur_lines[line_index].split()[0]                # original urban area file name
    urarea_file = urarea_file.replace('\\', '/')                  # convert backslashes to forward slashes
    # Resolve relative path from simulation base directory if provided
    if base_path is not None:
        urarea_file = str(base_path / urarea_file)
    ur_lines[line_index] =  '   ' + sim_files_new.ura_file + '		        / LUFLU'

    _, line_index = read_next_line_value(ur_lines, line_index, column=0, skip_lines=2)  # skip comments and two factors

    _, line_index = read_next_line_value(ur_lines, line_index, column=0, skip_lines=2)  # skip three file names

    line_index = iwfm.sub_remove_items(ur_lines, line_index, elems)    # curve numbers etc

    # initial conditions - process manually because end of file
    _, line_index = read_next_line_value(ur_lines, line_index - 1, column=0, skip_lines=0)  # skip file name and comments
    # Check bounds before accessing - skip_ahead returns -1 at end of file
    if (line_index >= 0 and
        line_index < len(ur_lines) and
        ur_lines[line_index].strip() and
        int(ur_lines[line_index].split()[0]) > 0):
        # Loop while current line is not a comment and not empty
        while (line_index < len(ur_lines) and
               ur_lines[line_index] and
               ur_lines[line_index][0] not in comments):
            if int(ur_lines[line_index].split()[0]) not in elems:
                del ur_lines[line_index]
            else:
                line_index += 1

    ur_lines.append('')

    with open(sim_files_new.ur_file, 'w', encoding='utf-8') as outfile:
        outfile.write('\n'.join(ur_lines))
    if verbose:
        print(f'      Wrote urban file {sim_files_new.ur_file}')


    # -- urban area file --
    iwfm.sub_lu_file(urarea_file, sim_files_new.ura_file, elems, verbose=verbose)


    return

