# sub_rootzone_file.py
# Copies the old Simulation rootzone main file and replaces the contents with 
# those of the new submodel, and writes out the new file, then calls methods 
# to modify the other Simulation rootzone component files
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


def sub_rootzone_file(sim_files, sim_files_new, elem_list, sub_snodes, base_path=None, verbose=False):
    '''sub_rootzone_file() - Read the original Simulation rootzone main file,
        determine which elements are in the submodel, and writes out a new file,
        then modify the other Simulation rootzone component files

    Parameters
    ----------
    sim_files : SimulationFiles
        existing model file names

    sim_files_new : SimulationFiles
        new submodel file names

    elem_list : list of ints
        list of existing model elements in submodel

    sub_snodes : list of ints
        submodel stream nodes

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

    elems = []
    for e in elem_list:
        elems.append(int(e[0]))

    # Use iwfm utility for file validation
    iwfm.file_test(sim_files.root_file)

    with open(sim_files.root_file, encoding='utf-8') as f:
        rz_lines = f.read().splitlines()

    # Skip initial comments and 4 factor lines
    _, line_index = read_next_line_value(rz_lines, 0, column=0, skip_lines=4)

    rz_dict = {}

    # non-ponded crop file name
    npc_file = rz_lines[line_index].split()[0]                   # rootzone non-ponded crop file
    if npc_file[0] == '/':
        npc_file = ''
        have_npc = False
    else:
        have_npc = True
        npc_file = npc_file.replace('\\', '/')
        # Resolve relative path from simulation base directory if provided
        if base_path is not None:
            npc_file = str(base_path / npc_file)
        rz_lines[line_index] = '   ' + sim_files_new.np_file + '		        / AGNPFL'
    rz_dict['np_file'] = npc_file

    # ponded crop file name
    _, line_index = read_next_line_value(rz_lines, line_index, column=0, skip_lines=0)
    pc_file = rz_lines[line_index].split()[0]                   # ponded crop file
    have_pc = True
    if pc_file[0] == '/':
        pc_file = ''
        have_pc = False
        rz_lines[line_index] = '                                         / PFL'
    else:
        pc_file = pc_file.replace('\\', '/')
        # Resolve relative path from simulation base directory if provided
        if base_path is not None:
            pc_file = str(base_path / pc_file)
        rz_lines[line_index] = '   ' + sim_files_new.pc_file + '		        / PFL'
    rz_dict['pc_file'] = pc_file

    # urban file name
    _, line_index = read_next_line_value(rz_lines, line_index, column=0, skip_lines=0)
    urban_file = rz_lines[line_index].split()[0]                 # urban file
    urban_line = line_index
    have_urban = True
    if urban_file[0] == '/':
        urban_file = ''
        have_urban = False
        rz_lines[line_index] = '                                         / URBFL'
    else:
        urban_file = urban_file.replace('\\', '/')
        # Resolve relative path from simulation base directory if provided
        if base_path is not None:
            urban_file = str(base_path / urban_file)
        rz_lines[line_index] = '   ' + sim_files_new.ur_file + '		        / URBFL'
    rz_dict['ur_file'] = urban_file

    # native veg file
    _, line_index = read_next_line_value(rz_lines, line_index, column=0, skip_lines=0)
    nv_file = rz_lines[line_index].split()[0]           # native veg file
    have_nv = True
    if nv_file[0] == '/':
        nv_file = ''
        have_nv = False
        rz_lines[line_index] = '                                         / NVRVFL'
    else:
        nv_file = nv_file.replace('\\', '/')
        # Resolve relative path from simulation base directory if provided
        if base_path is not None:
            nv_file = str(base_path / nv_file)
        rz_lines[line_index] = '   ' + sim_files_new.nv_file + '		        / NVRVFL'
    rz_dict['nv_file'] = nv_file

    # skip input lines and comments to soil parameters section
    _, line_index = read_next_line_value(rz_lines, line_index, column=0, skip_lines=13)

    # remove elements not in submodel, modify stream node of elements in submodel
    while line_index < len(rz_lines):
        t = rz_lines[line_index].split()
        if int(t[0]) in elems:
            if int(t[10]) == 1:  # runoff flows to a stream node
                if int(t[11]) not in sub_snodes:
                    t[10] = 0    # change to export
                    rz_lines[line_index] = '\t'.join(t)
            line_index += 1
        else:
            del rz_lines[line_index]

    # -- non-ponded crop files --
    if have_npc:
        iwfm.sub_rz_npc_file(npc_file, sim_files_new, elems, base_path, verbose=verbose)

    # -- ponded crop files --
    if have_pc:
        iwfm.sub_rz_pc_file(pc_file, sim_files_new, elems, base_path, verbose=verbose)

    # -- urban files --
    if have_urban:
        iwfm.sub_rz_urban_file(urban_file, sim_files_new, elems, base_path, verbose=verbose)

    # -- native & riparian files --
    if have_nv:
        iwfm.sub_rz_nv_file(nv_file, sim_files_new, elems, base_path, verbose=verbose)

    # -- write out rootzone main file --
    with open(sim_files_new.root_file, 'w', encoding='utf-8') as outfile:
        outfile.write('\n'.join(rz_lines))
    if verbose:
        print(f'  Wrote rootzone main file {sim_files_new.root_file}')

    return

