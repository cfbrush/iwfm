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


'''Copy the rootzone non-ponded crops main file and replace the contents with those of the new submodel, write out the new file, and process the other non-ponded crop files.'''

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

    # -- element sections (curve numbers, ETc pointers, water supply
    #    requirement, irrigation periods, min/target soil moisture, return
    #    flow and re-use fractions, minimum percolation, initial conditions).
    #    The number of sections, their order, and where file-name/factor
    #    lines (MINSMFL, TRGSMFL, DPFL, ...) fall between them varies by
    #    model era, and any section may collapse to a single all-elements
    #    row (element ID 0). Sweep by marker instead of a fixed sequence:
    #    header/file/factor lines carry an inline '/ TAG' comment, element
    #    rows do not.
    while line_index < len(npc_lines):
        line = npc_lines[line_index]
        if not line.strip() or line[0] in 'Cc*#':
            line_index += 1                       # comment or blank
        elif '/' in line:
            line_index += 1                       # file name or factor line
        else:
            element_id = int(line.split()[0])
            if element_id == 0 or element_id in elems:
                line_index += 1                   # all-elements row, or keep
            else:
                del npc_lines[line_index]

    npc_lines.append('')

    with open(sim_files_new.np_file, 'w', encoding='utf-8') as outfile:
        outfile.write('\n'.join(npc_lines))
    if verbose:
        print(f'      Wrote non-ponded crop file {sim_files_new.np_file}')


    # -- non-ponded crop area file --
    iwfm.sub_lu_file(nparea_file, sim_files_new.npa_file, elems, verbose=verbose)


    return

