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


'''Copy the rootzone ponded crops main file and replace the contents with those of the new submodel, write out the new file, and process the other ponded crop files.'''

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

    # Use iwfm utility for file validation
    iwfm.file_test(old_filename)

    with open(old_filename, encoding='utf-8') as f:
        pc_lines = f.read().splitlines()
    pc_lines.append('')

    # -- locate the land-use area file entry by its LUFLP tag. The header
    #    preamble before it varies by model era (older files start with the
    #    area file; newer ones lead with crop counts and CCODE lines).
    line_index = None
    for i, line in enumerate(pc_lines):
        if line.strip() and line[0] not in 'Cc*#' and 'LUFLP' in line:
            line_index = i
            break
    if line_index is None:
        raise ValueError(f'{old_filename}: no LUFLP area-file entry found')

    area_file = pc_lines[line_index].split()[0]
    area_file = area_file.replace('\\', '/')
    if base_path is not None:
        area_file = str(base_path / area_file)
    pc_lines[line_index] = '   ' + sim_files_new.pca_file + '\t\t        / LUFLP'

    # -- element sections: the number of sections, their order, and where
    #    file-name/factor lines fall between them varies by model era, and
    #    any section may collapse to a single all-elements row (element ID
    #    0). Sweep by marker: header/file/factor lines carry an inline
    #    '/ TAG' comment, element rows do not.
    line_index += 1
    while line_index < len(pc_lines):
        line = pc_lines[line_index]
        if not line.strip() or line[0] in 'Cc*#':
            line_index += 1                       # comment or blank
        elif '/' in line:
            line_index += 1                       # file name or factor line
        else:
            element_id = int(line.split()[0])
            if element_id == 0 or element_id in elems:
                line_index += 1                   # all-elements row, or keep
            else:
                del pc_lines[line_index]

    pc_lines.append('')

    with open(sim_files_new.pc_file, 'w', encoding='utf-8') as outfile:
        outfile.write('\n'.join(pc_lines))
    if verbose:
        print(f'      Wrote ponded crop file {sim_files_new.pc_file}')

    # -- ponded crop area file --
    iwfm.sub_lu_file(area_file, sim_files_new.pca_file, elems, verbose=verbose)

    return



