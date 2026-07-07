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
    '''sub_gw_bc_file() - Read the original groundwater boundary conditions file,
        determine which boundary conditions are in the submodel, and write out a new
        file

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

    if verbose: print(f"Entered sub_gw_bc_file() with {old_filename}")

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
        spfl_file = spfl_file.replace('\\', ' ').split()[1]
        bc_lines[line_index] = '   ' + sim_files_new.spfl_file + '.dat		        / SPFLOWBCFL'

    # specified head conditions file
    sphd_file, line_index = read_next_line_value(bc_lines, line_index)
    have_sphd = True
    if sphd_file[0] == '/':
        have_sphd = False
    else:
        sphd_file = sphd_file.replace('\\', ' ').split()[1]
        bc_lines[line_index] = '   ' + sim_files_new.sphd_file + '.dat		        / SPHEADBCFL'

    # general head boundary conditions file
    ghd_file, line_index = read_next_line_value(bc_lines, line_index)
    have_ghd = True
    if ghd_file[0] == '/':
        have_ghd = False
    else:
        ghd_file = ghd_file.replace('\\', ' ').split()[1]
        bc_lines[line_index] = '   ' + sim_files_new.ghd_file + '.dat		        / GHBCFL'

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
        bc_lines[line_index] = '   ' + sim_files_new.cghd_file + '.dat		        / CONGHBCFL'

    # time-series boundary conditions file
    tsbc_file, line_index = read_next_line_value(bc_lines, line_index)
    have_tsbc = True
    if tsbc_file[0] == '/':
        have_tsbc = False
    else:
        tsbc_file = tsbc_file.replace('\\', ' ').split()[1]
        bc_lines[line_index] = '   ' + sim_files_new.tsbc_file + '.dat		        / TSBCFL'

    # -- boundary flow node hydrographs --
    b_outnodes_str, line_index = read_next_line_value(bc_lines, line_index)
    b_outnodes = int(b_outnodes_str)
    b_outfile, line_index = read_next_line_value(bc_lines, line_index)
    # -- TODO: if b_outnodes > 0: reduce hydrograph nodes to those in submodel

    # --  specified flow bc file  --
    #if have_spfl:   TODO          # process specified flow bc file

    # --  specified head bc file  --
    #if have_sphd:   TODO          # process specified head bc file

    # --  general head bc file  --
    #if have_ghd:    TODO          # process general head bc file

    # --  constrained general head bc file  --
    if have_cghd:                  # process constrained general head bc file
        iwfm.sub_gw_bc_cghd_file(cghd_file, sim_files_new.cghd_file, nodes, verbose)

    with open(sim_files_new.bc_file, 'w', encoding='utf-8') as outfile:
        outfile.write('\n'.join(bc_lines))

    if verbose:
        print(f'      Wrote boundary conditions file {sim_files_new.bc_file}')
        print(f"Leaving sub_gw_bc_file()")

    return
