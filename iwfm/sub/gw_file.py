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
    have_bc = True
    if bc_file[0] == '/':
        bc_file = ''
        have_bc = False
        gw_lines[line_index] = '                                         / BCFL'
    else:
        bc_file = bc_file.replace('\\', '/')
        # Resolve relative path from simulation file directory
        bc_file = str(base_path / bc_file)
        gw_lines[line_index] = '   ' + sim_files_new.bc_file + '		        / BCFL'
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
        gw_lines[line_index] = '   ' + sim_files_new.drain_file + '		        / TDFL'
    gw_dict['drain_file'] = td_file

    # pumping file
    pump_file, line_index = read_next_line_value(gw_lines, line_index)
    have_pump = True
    if pump_file[0] == '/':
        pump_file = ''
        have_pump = False
        gw_lines[line_index] = '                                         / PUMPFL'
    else:
        pump_file = pump_file.replace('\\', '/')
        # Resolve relative path from simulation file directory
        pump_file = str(base_path / pump_file)
        gw_lines[line_index] = '   ' + sim_files_new.pump_file + '		        / PUMPFL'
    gw_dict['pump_file'] = pump_file

    # subsidence file
    subs_file, line_index = read_next_line_value(gw_lines, line_index)
    have_subs = True
    if subs_file[0] == '/':
        subs_file = ''
        have_subs = False
        gw_lines[line_index] = '                                         / SUBSFL'
    else:
        subs_file = subs_file.replace('\\', '/')
        # Resolve relative path from simulation file directory
        subs_file = str(base_path / subs_file)
        gw_lines[line_index] = '   ' + sim_files_new.sub_file + '		        / SUBSFL'
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
    # face flow hydrographs: ID IOUTFL IOUTFA IOUTFB NAME, where IOUTFA and
    # IOUTFB are the two groundwater nodes defining the element face
    nface_str, line_index = read_next_line_value(gw_lines, line_index)
    nface = int(nface_str)
    nface_line = line_index

    _, line_index = read_next_line_value(gw_lines, line_index)          # FCHYDOUTFL
    fchyd_line = line_index

    if nface > 0:
        _, line_index = read_next_line_value(gw_lines, line_index)      # first face line
        new_nface = 0
        for _ in range(nface):
            t = gw_lines[line_index].split()
            if int(t[2]) in nodes and int(t[3]) in nodes:
                new_nface += 1
                line_index += 1
            else:
                del gw_lines[line_index]
        gw_lines[nface_line] = '     ' + str(new_nface) + '                         / NOUTF'
        if new_nface == 0:
            gw_lines[fchyd_line] = '                                         / FCHYDOUTFL'
        _, line_index = read_next_line_value(gw_lines, line_index - 1)  # next data line
    else:
        _, line_index = read_next_line_value(gw_lines, line_index)      # next data line

    # -- parametric grid for groundwater parameters --
    pgroups = int(gw_lines[line_index].split()[0])              # parametric grid?
    pgroups_range_lines = []

    # skip factors (4 lines after NGROUP)
    _, line_index = read_next_line_value(gw_lines, line_index, skip_lines=4)

    if pgroups > 0:
        # carry the parametric grid(s) through unchanged, except the node
        # range spec, which must be rewritten to the submodel's nodes
        node_count = None
        layers = None
        for group in range(pgroups):
            if group > 0:
                # advance to this group's node range line
                _, line_index = read_next_line_value(gw_lines, line_index - 1)
            pgroups_range_lines.append(line_index)               # node range spec line
            ndp_str, line_index = read_next_line_value(gw_lines, line_index)
            ndp = int(ndp_str)
            nep_str, line_index = read_next_line_value(gw_lines, line_index)
            nep = int(nep_str)

            # skip NEP connectivity lines
            _, line_index = read_next_line_value(gw_lines, line_index, skip_lines=nep - 1)

            # first parametric node block: detect lines per block
            _, line_index = read_next_line_value(gw_lines, line_index)
            block = 1
            len1 = len(gw_lines[line_index].split('/')[0].split())
            while len(gw_lines[line_index + block].split('/')[0].split()) < len1:
                block += 1

            # skip remaining parametric node data (blocks are contiguous)
            line_index += ndp * block

        # rewrite each group's node range spec to the submodel node list
        sorted_nodes = sorted(nodes)
        range_parts = []
        start = prev = sorted_nodes[0]
        for n in sorted_nodes[1:]:
            if n == prev + 1:
                prev = n
                continue
            range_parts.append(f'{start}-{prev}' if start != prev else f'{start}')
            start = prev = n
        range_parts.append(f'{start}-{prev}' if start != prev else f'{start}')
        for rl in pgroups_range_lines:
            gw_lines[rl] = '    ' + ', '.join(range_parts)
    else:
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
    # skip FACTHP to get to initial head data. When NEBK == 0 the anomaly
    # skip above already left the cursor ON the FACTHP line; when NEBK > 0
    # the cursor is one past the last anomaly line and FACTHP is the next
    # data line.
    if nebk > 0:
        _, line_index = read_next_line_value(gw_lines, line_index, skip_lines=1)
    else:
        _, line_index = read_next_line_value(gw_lines, line_index - 1, skip_lines=1)
    if node_count is None:
        # parametric-grid file: count the initial condition lines directly
        line, node_count = line_index, 0
        while (line < len(gw_lines) and gw_lines[line].strip()
               and gw_lines[line][0] not in comments):
            line += 1
            node_count += 1
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
    if not have_td:
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
        print("Leaving sub_gw_file()")

    return
