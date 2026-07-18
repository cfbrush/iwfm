# sub_gw_subs_file.py
# Copies the groundwater subsidence file and replace the contents with those of the new
# submodel, and writes out the new file
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


'''Copy the groundwater subsidence file and replace the contents with those of the new submodel, and writes out the new file.'''

def sub_gw_subs_file(old_filename, new_filename, node_list, bounding_poly, verbose=False):
    '''Read the original groundwater subsidence file, determine which nodes are in the submodel, and write out a new file.

    Parameters
    ----------
    old_filename : str
        name of existing model subsidence file

    new_filename : str
        name of new submodel subsidence file

    node_list : list of ints
        list of existing model nodes in submodel

    bounding_poly : shapely Polygon
        submodel area

    verbose : bool, default=False
        turn command-line output on or off

    Returns
    -------
    nothing
    '''
    import iwfm
    from iwfm.file_utils import read_next_line_value
    from shapely.geometry import Point

    if verbose: print(f"Entered sub_gw_subs_file() with {old_filename}")

    nodes = list(node_list)

    iwfm.file_test(old_filename)
    with open(old_filename, encoding='utf-8') as f:
        subs_lines = f.read().splitlines()
    subs_lines.append('')

    # Skip initial comments and file names/factors (5 data lines), then read nouts
    nouts_str, line_index = read_next_line_value(subs_lines, -1, column=0, skip_lines=5)
    nouts = int(nouts_str)

    new_nouts, nouts_line = 0, line_index

    # Skip factors (3 data lines) to reach hydrograph locations
    _, line_index = read_next_line_value(subs_lines, line_index - 1, skip_lines=3)

    # remove hydrographs that are not in the submodel
    keep_hyd = []
    for l in range(0, nouts):
        t = subs_lines[line_index].split()
        id = int(t[0])
        point = Point(float(t[3]), float(t[4]))
        if not point.within(bounding_poly):
            del subs_lines[line_index]
        else:
            new_nouts += 1
            keep_hyd.append(id)
            line_index += 1
        _, line_index = read_next_line_value(subs_lines, line_index - 1, skip_lines=0)       # skip comments to next section

    subs_lines[nouts_line] = '         ' + str(new_nouts) + '                       / NOUTS'

    # -- subsidence parameters
    # -- parametric grid for subsidence parameters --
    pgroups = int(subs_lines[line_index].split()[0])              # parametric grid?
    # skip factors (1 data line after pgroups line)
    _, line_index = read_next_line_value(subs_lines, line_index, column=0, skip_lines=1)

    if pgroups > 0:
        # carry the parametric grid(s) through unchanged, except the node
        # range spec, which must be rewritten to the submodel's nodes
        range_lines = []
        for group in range(pgroups):
            if group > 0:
                # advance to this group's node range line
                _, line_index = read_next_line_value(subs_lines, line_index - 1)
            range_lines.append(line_index)                       # node range spec line
            ndp_str, line_index = read_next_line_value(subs_lines, line_index)
            ndp = int(ndp_str)
            nep_str, line_index = read_next_line_value(subs_lines, line_index)
            nep = int(nep_str)

            # skip NEP connectivity lines
            _, line_index = read_next_line_value(subs_lines, line_index, skip_lines=nep - 1)

            # first parametric node block: detect lines per block
            _, line_index = read_next_line_value(subs_lines, line_index)
            block = 1
            len1 = len(subs_lines[line_index].split('/')[0].split())
            while (line_index + block < len(subs_lines) and
                   len(subs_lines[line_index + block].split('/')[0].split()) < len1):
                block += 1

            # skip remaining parametric node data (blocks are contiguous)
            line_index += ndp * block

        # rewrite each group's node range spec to the submodel node list
        sorted_nodes = sorted(set(int(n) for n in nodes))
        range_parts = []
        start = prev = sorted_nodes[0]
        for n in sorted_nodes[1:]:
            if n == prev + 1:
                prev = n
                continue
            range_parts.append(f'{start}-{prev}' if start != prev else f'{start}')
            start = prev = n
        range_parts.append(f'{start}-{prev}' if start != prev else f'{start}')
        for rl in range_lines:
            subs_lines[rl] = '    ' + ', '.join(range_parts)
    else:
        # -- parameters for each model node --
        # first, determine the number of layers - 1st line has 6 items, others have 5 items
        layers, line = 1, line_index + 1
        while len(subs_lines[line].split()) < 6:
            layers += 1
            line += 1

        # count the number of nodes in the original model file
        line, node_count = line_index, 0 # starting point
        while len(subs_lines[line]) > 0:
            line += 1
            node_count += 1
        node_count = int(node_count / layers)

        # remove parameters for nodes that are not in the submodel
        for l in range(1,node_count + 1):
            t = subs_lines[line_index].split()
            if (int(t[0]) not in nodes):
                for i in range(0,layers):  # remove <layers> lines
                    del subs_lines[line_index]
            else:
                line_index += layers

    subs_lines.append('')

    with open(new_filename, 'w', encoding='utf-8') as outfile:
        outfile.write('\n'.join(subs_lines))

    if verbose:
        print(f'      Wrote subsidence file {new_filename}')
        print("Leaving sub_gw_subs_file()")

    return
