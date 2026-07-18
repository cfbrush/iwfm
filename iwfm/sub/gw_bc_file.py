# sub_gw_bc_file.py
# Copies the old groundwater boundary condition file and replaces the contents 
# with those of the new submodel, and writes out the new file
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


def sub_gw_bc_file(old_filename, sim_files_new, nodes, elems, bounding_poly, base_path=None, verbose=False):
    '''Read the original groundwater boundary conditions file, determine which boundary conditions are in the submodel, and write out a new file.

    Parameters
    ----------
    old_filename : str
        name of existing model boundary condition file

    sim_files_new : SimulationFiles
        new submodel file names

    nodes : list of ints
        list of existing model nodes in submodel

    elems : list of ints
        list of existing model elements in submodel

    bounding_poly : shapely.geometry Polygon
        submodel boundary form model nodes

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
    from pathlib import Path

    if verbose: print(f"Entered sub_gw_bc_file() with {old_filename}")

    if base_path is not None and not isinstance(base_path, Path):
        base_path = Path(base_path)

    iwfm.file_test(old_filename)
    with open(old_filename, encoding='utf-8') as f:
        bc_lines = f.read().splitlines()
    bc_lines.append('')

    # -- file names --
    # specified flow conditions file
    spfl_file, line_index = read_next_line_value(bc_lines, -1)
    have_spfl = True
    if spfl_file[0] == '/':
        have_spfl = False
    else:
        spfl_file = spfl_file.replace('\\', '/')
        if base_path is not None:
            spfl_file = str(base_path / spfl_file)
        bc_lines[line_index] = '   ' + sim_files_new.spfl_file + '		        / SPFLOWBCFL'

    # specified head conditions file
    sphd_file, line_index = read_next_line_value(bc_lines, line_index)
    have_sphd = True
    if sphd_file[0] == '/':
        have_sphd = False
    else:
        sphd_file = sphd_file.replace('\\', '/')
        if base_path is not None:
            sphd_file = str(base_path / sphd_file)
        bc_lines[line_index] = '   ' + sim_files_new.sphd_file + '		        / SPHEADBCFL'

    # general head boundary conditions file
    ghd_file, line_index = read_next_line_value(bc_lines, line_index)
    have_ghd = True
    if ghd_file[0] == '/':
        have_ghd = False
    else:
        ghd_file = ghd_file.replace('\\', '/')
        if base_path is not None:
            ghd_file = str(base_path / ghd_file)
        bc_lines[line_index] = '   ' + sim_files_new.ghd_file + '		        / GHBCFL'

    # constrained general head boundary conditions file
    cghd_file, line_index = read_next_line_value(bc_lines, line_index)
    have_cghd = True
    if cghd_file[0] == '/':
        have_cghd = False
    else:
        cghd_file = cghd_file.replace('\\', '/')
        # Resolve relative path from simulation base directory if provided
        if base_path is not None:
            cghd_file = str(base_path / cghd_file)
        bc_lines[line_index] = '   ' + sim_files_new.cghd_file + '		        / CONGHBCFL'

    # time-series boundary conditions file
    tsbc_file, line_index = read_next_line_value(bc_lines, line_index)
    if tsbc_file[0] != '/':
        tsbc_file = tsbc_file.replace('\\', ' ').split()[1]
        bc_lines[line_index] = '   ' + sim_files_new.tsbc_file + '		        / TSBCFL'

    # -- boundary flow node hydrographs --
    b_outnodes_str, line_index = read_next_line_value(bc_lines, line_index)
    b_outnodes = int(b_outnodes_str)
    b_outnodes_line = line_index
    b_outfile, line_index = read_next_line_value(bc_lines, line_index)

    if b_outnodes > 0:             # keep hydrograph nodes in the submodel
        _, line_index = read_next_line_value(bc_lines, line_index)
        new_outnodes = 0
        for _ in range(b_outnodes):
            if int(bc_lines[line_index].split()[0]) in nodes:
                new_outnodes += 1
                line_index += 1
            else:
                del bc_lines[line_index]
        parts = bc_lines[b_outnodes_line].split('/', 1)
        tail = '/ ' + parts[1].strip() if len(parts) > 1 else '/ NOUTB'
        bc_lines[b_outnodes_line] = ('     ' + str(new_outnodes)).ljust(30) + tail

    # --  specified flow bc file  --
    if have_spfl:                  # process specified flow bc file
        iwfm.sub_gw_bc_node_file(spfl_file, sim_files_new.spfl_file, nodes, verbose)

    # --  specified head bc file  --
    if have_sphd:                  # process specified head bc file
        iwfm.sub_gw_bc_node_file(sphd_file, sim_files_new.sphd_file, nodes, verbose)

    # --  general head bc file  --
    if have_ghd:                   # process general head bc file
        iwfm.sub_gw_bc_node_file(ghd_file, sim_files_new.ghd_file, nodes, verbose)

    # --  constrained general head bc file  --
    if have_cghd:                  # process constrained general head bc file
        iwfm.sub_gw_bc_cghd_file(cghd_file, sim_files_new.cghd_file, nodes, verbose)

    with open(sim_files_new.bc_file, 'w', encoding='utf-8') as outfile:
        outfile.write('\n'.join(bc_lines))

    if verbose:
        print(f'      Wrote boundary conditions file {sim_files_new.bc_file}')
        print("Leaving sub_gw_bc_file()")

    return
