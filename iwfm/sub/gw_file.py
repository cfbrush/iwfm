# sub_gw_file.py
# Copies the old groundwater main file and replaces the contents with those of the new
# submodel, and writes out the new file, then calls methods to modify the other 
# groundwater component files
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


def sub_gw_file(sim_files, sim_files_new, node_list, elem_list, bounding_poly, sim_base_path=None, verbose=False):
    '''sub_gw_file() - Read the original groundwater main file, determine
        which elements are in the submodel, and write out a new file, then
        modifies the other groundwater component files

    Parameters
    ----------
    sim_files : SimulationFiles
        existing model file names

    sim_files_new : SimulationFiles
        new submodel file names

    node_list : list of ints
        list of existing model nodes in submodel

    elem_list : list of ints
        list of existing model elements in submodel

    bounding_poly : shapely.geometry Polygon
        submodel boundary form model nodes

    sim_base_path : Path, optional
        base path for resolving relative file paths

    verbose : bool, default=False
        turn command-line output on or off

    Returns
    -------
    nothing

    '''
    import iwfm
    from iwfm.file_utils import read_next_line_value
    from shapely.geometry import Point
    from pathlib import Path
    import sys

    if verbose: print(f"Entered sub_gw_file() with {sim_files.gw_file}")

    comments = ['C', 'c', '*', '#']
    nodes = []
    for n in node_list:
        nodes.append(n)

    elems = []
    for e in elem_list:
        elems.append(int(e[0]))

    # Check if groundwater file exists
    if not sim_files.gw_file:
        raise ValueError(
            'Groundwater file path not specified in simulation files.\n'
            '    Check that the simulation input file specifies a groundwater file.'
        )

    gw_file_path = sim_files.gw_file
    iwfm.file_test(gw_file_path)

    # Determine base path for resolving relative file paths in groundwater file
    # Paths in groundwater file are relative to the simulation file's directory
    if sim_base_path is not None:
        base_path = sim_base_path if isinstance(sim_base_path, Path) else Path(sim_base_path)
    else:
        # Fall back to groundwater file's directory for backwards compatibility
        base_path = Path(gw_file_path).resolve().parent

    with open(gw_file_path, encoding='utf-8') as f:
        gw_lines = f.read().splitlines()
    gw_lines.append('')

    gw_dict = {}

    # -- file names --
    # boundary condition file
    bc_file, line_index = read_next_line_value(gw_lines, -1)
    bc_line = line_index   # if no boundary conditions in submodel, come back and remove file name
    have_bc = True
    if bc_file[0] == '/':
        bc_file = ''
        have_bc = False
        gw_lines[line_index] = '                                         / BCFL'
    else:
        bc_file = bc_file.replace('\\', '/')
        # Resolve relative path from simulation file directory
        bc_file = str(base_path / bc_file)
        gw_lines[line_index] = '   ' + sim_files_new.bc_file + '.dat		        / BCFL'
    gw_dict['bc_file'] = bc_file

    # tile drain file
    td_file, line_index = read_next_line_value(gw_lines, line_index)
    tile_line = line_index   # if no tile drains in submodel, come back and remove file name
    have_td = True
    if td_file[0] == '/':
        td_file = ''
        have_td = False
        gw_lines[line_index] = '                                         / TDFL'
    else:
        td_file = td_file.replace('\\', '/')
        # Resolve relative path from simulation file directory
        td_file = str(base_path / td_file)
        gw_lines[line_index] = '   ' + sim_files_new.drain_file + '.dat		        / TDFL'
    gw_dict['drain_file'] = td_file

    # pumping file
    pump_file, line_index = read_next_line_value(gw_lines, line_index)
    pump_line = line_index   # if no pumping in submodel, come back and remove file name
    have_pump = True
    if pump_file[0] == '/':
        pump_file = ''
        have_pump = False
        gw_lines[line_index] = '                                         / PUMPFL'
    else:
        pump_file = pump_file.replace('\\', '/')
        # Resolve relative path from simulation file directory
        pump_file = str(base_path / pump_file)
        gw_lines[line_index] = '   ' + sim_files_new.pump_file + '.dat		        / PUMPFL'
    gw_dict['pump_file'] = pump_file

    # subsidence file
    subs_file, line_index = read_next_line_value(gw_lines, line_index)
    subs_line = line_index   # if no subsidence in submodel, come back and remove file name
    have_subs = True
    if subs_file[0] == '/':
        subs_file = ''
        have_subs = False
        gw_lines[line_index] = '                                         / SUBSFL'
    else:
        subs_file = subs_file.replace('\\', '/')
        # Resolve relative path from simulation file directory
        subs_file = str(base_path / subs_file)
        gw_lines[line_index] = '   ' + sim_files_new.sub_file + '.dat		        / SUBSFL'
    gw_dict['subs_file'] = subs_file

    # -- hydrograph section --
    # skip 16 non-comment lines to get to NOUTH
    nhyds_str, line_index = read_next_line_value(gw_lines, line_index, skip_lines=16)
    nhyds = int(nhyds_str)
    hyds_line = line_index

    # skip 3 lines (NOUTH, FACTXY, GWHYDOUTFL) to get to hydrograph data
    _, line_index = read_next_line_value(gw_lines, line_index, skip_lines=2)

    # check each hydrographs and remove the hydrographs outside the submodel boundary
    new_hyds = 0
    for i in range(0, nhyds):
        t = gw_lines[line_index].split()
        point = Point(float(t[3]), float(t[4]))

        if not point.within(bounding_poly):
            del gw_lines[line_index]
        else:
            new_hyds += 1
            line_index += 1

    # update the number of hydrographs
    gw_lines[hyds_line] = '     ' + str(new_hyds) + '        / NOUTH'

    # -- element face flow section --
    # --  TODO:  element face flow section
    # skip element face flow section (2 lines: NOUTF, FCHYDOUTFL)
    _, line_index = read_next_line_value(gw_lines, line_index, skip_lines=2)

    # -- parametric grid for groundwater parameters --
    pgroups = int(gw_lines[line_index].split()[0])              # parametric grid?

    # skip factors (4 lines after NGROUP)
    _, line_index = read_next_line_value(gw_lines, line_index, skip_lines=4)

    # --  TODO:  if pgroups > 0,  skip parametric grid(s)

    # -- parameters for each model node --
    # first, determine the number of layers - 1st line has 6 items, others have 5 items
    layers, line = 1, line_index + 1
    while len(gw_lines[line].split()) < 6:
        layers += 1
        line += 1

    # count the number of nodes in the original model file
    line, node_count = line_index, 0  # starting point
    while gw_lines[line][0] not in comments:
        line += 1
        node_count += 1
    node_count = int(node_count / layers)

    # remove parameters for nodes that are not in the submodel
    for l in range(1, node_count + 1):
        if l not in nodes:
            for i in range(0, layers):  # remove <layers> lines
                del gw_lines[line_index]
        else:
            line_index += layers

    # -- hydraulic conductivity anomalies --
    # skip to nebk
    nebk_str, line_index = read_next_line_value(gw_lines, line_index)
    nebk = int(nebk_str)
    nebk_line = line_index

    # skip to hydraulic conductivity anomalies (2 lines: FACT, TUNITH)
    _, line_index = read_next_line_value(gw_lines, line_index, skip_lines=2)
    nebk_new = 0
    # remove lines that are not in submodel
    for l in range(0, nebk):
        if int(gw_lines[line_index].split()[1]) in elems:
            line_index += 1
            nebk_new += 1
        else:
            del gw_lines[line_index]
    gw_lines[nebk_line] = '     ' + str(nebk_new) + '                         / NEBK'

    # -- initial conditions --
    # skip 1 line (FACTHP) to get to initial head data
    _, line_index = read_next_line_value(gw_lines, line_index, skip_lines=1)
    # remove lines that are not in submodel
    for l in range(1, node_count + 1):
        if l not in nodes:
            del gw_lines[line_index]
        else:
            line_index += 1

    # -- boundary conditions file --
    if have_bc:
        iwfm.sub_gw_bc_file(bc_file, sim_files_new, nodes, elems, bounding_poly, base_path, verbose=verbose)

    # -- tile drain file --
    if have_td:
        have_td = iwfm.sub_gw_td_file(td_file, sim_files_new.drain_file, node_list, verbose=verbose)
    if have_td == False:
        gw_lines[tile_line] = '                                         / TDFL'

    # -- pumping files --
    if have_pump:
        iwfm.sub_gw_pump_file(pump_file, sim_files_new, elems, bounding_poly, base_path, verbose=verbose)

    # -- subsidence file --
    if have_subs:
        iwfm.sub_gw_subs_file(subs_file, sim_files_new.sub_file, node_list, bounding_poly, verbose=verbose)

    gw_lines.append('')

    with open(sim_files_new.gw_file, 'w', encoding='utf-8') as outfile:
        outfile.write('\n'.join(gw_lines))

    if verbose:
        print(f'  Wrote groundwater main file {sim_files_new.gw_file}')
        print(f"Leaving sub_gw_file()")

    return
