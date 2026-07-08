# sub_gw_pump_well_file.py
# Copies the old well pumping file and replaces the contents with those 
# of the new submodel, and writes out the new file
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


def sub_gw_pump_well_file(old_filename, new_filename, elems, bounding_poly, verbose=False):
    '''sub_gw_pump_well_file() - Copies the old well pumping file and replaces the
        contents with those of the new submodel, and writes out the new file

    Parameters
    ----------
    old_filename : str
        name of existing model well pumping file

    new_filename : str
        name of new submodel well pumping file

    elems : list of ints
        list of existing model elements in submodel

    bounding_poly : shapely Polygon
        submodel area

    verbose : bool, default=False
        turn command-line output on or off

    Returns
    -------
    new_nwells > 0 : bool
        True if any wells in submodel, False otherwise

    '''
    import iwfm
    from iwfm.file_utils import read_next_line_value
    from shapely.geometry import Point

    if verbose: print(f"Entered sub_gw_pump_well_file() with {old_filename}")

    # Check if well file exists using iwfm utility
    iwfm.file_test(old_filename)

    with open(old_filename, encoding='utf-8') as f:
        well_lines = f.read().splitlines()
    well_lines.append('')

    # Skip initial comments and read nwells (number of wells)
    nwells_str, line_index = read_next_line_value(well_lines, -1, column=0, skip_lines=0)
    nwells = int(nwells_str)
    new_nwells, nwells_line = 0, line_index

    # Skip factors (4 data lines) to reach well location data
    _, line_index = read_next_line_value(well_lines, line_index, column=0, skip_lines=3)

    keep_wells = []
    for l in range(0, nwells):
        t = well_lines[line_index].split()
        id = int(t[0])
        point = Point(float(t[1]), float(t[2]))
        if not point.within(bounding_poly):
            del well_lines[line_index]
        else:
            keep_wells.append(id)
            new_nwells += 1
            line_index += 1

    well_lines[nwells_line] = '         ' + str(new_nwells) + '                       / NWELL'
    # Skip comments to well pumping characteristics section
    _, line_index = read_next_line_value(well_lines, line_index - 1, skip_lines=0)

    for l in range(0, nwells):
        t = well_lines[line_index].split()
        if int(t[0]) not in keep_wells:
            del well_lines[line_index]
        else:
            line_index += 1

    # -- delivery element groups
    # Skip comments and read ngrp (number of element groups)
    ngrp_str, line_index = read_next_line_value(well_lines, line_index - 1, column=0, skip_lines=0)
    ngrp = int(ngrp_str)
    new_ngrp, ngrp_line = 0, line_index

    # cycle through element groups, eliminating those outside the submodel area
    # and reducing those partially inside the submodel area
    # Skip to first group (1 data line after ngrp)
    if ngrp > 0:
        _, line_index = read_next_line_value(well_lines, line_index, column=0, skip_lines=0)
    for id in range(0, ngrp):
        grp_line, ielems = line_index, []

        # Parse element group line with error checking
        line_data = well_lines[line_index].split()
        if len(line_data) < 3:
            raise ValueError(
                'Malformed well file while processing element groups\n'
                f'    File: {old_filename}\n'
                f'    Processing group {id + 1} of {ngrp}\n'
                f'    Current line {line_index + 1}: "{well_lines[line_index]}"\n'
                '\n    Expected format for group header line:\n'
                '      group_id num_elements first_element [additional_data]\n'
                f'    Found {len(line_data)} value(s) but expected at least 3\n'
                '\n    Well file format:\n'
                '      - Each group starts with: <ID> <NELEM> <first_element>\n'
                '      - Followed by NELEM-1 lines with one element ID each\n'
                '\n    This error may occur if:\n'
                '      1. The number of element groups (NGRP) is wrong\n'
                '      2. The number of elements (NELEM) in a previous group was incorrect\n'
                '      3. There is a bug in the line deletion logic when filtering groups\n'
                '\n    Please verify:\n'
                '      - The NGRP value matches the actual number of groups in the file\n'
                '      - Each group header has the correct NELEM value\n'
                f'      - Check the format around line {line_index + 1} in the original file'
            )

        grp_id, nelem, ielem, *z = [int(e) for e in line_data]
        if ielem in elems:  # keep the item
            ielems.append(ielem)
        line_index += 1
        for j in range(1, nelem):
            ielem = int(well_lines[line_index].split()[0])
            if ielem in elems:  # keep the item
                ielems.append(ielem)
            line_index += 1
        # after reading all ielem in group
        if len(ielems) == 0:   # delete the lines for this element group
            for j in range(grp_line, line_index):
                del well_lines[grp_line]
            line_index = grp_line
        elif len(ielems) > 0:
            new_ngrp += 1
            well_lines[ngrp_line] = '\t' + str(new_ngrp)
            well_lines[grp_line] = str(id+1) + '\t' + str(len(ielems)) + '\t' + str(ielems[0])
            if len(ielems) > 1:
                for j in range(1,len(ielems)):
                    well_lines[grp_line + j] = '\t\t' + str(ielems[j])
            if len(ielems) < nelem:
                # Delete extra lines - always delete at the same position since list shrinks
                for j in range(len(ielems), nelem):
                    del well_lines[grp_line + len(ielems)]
            # line_index was pointing past the old group, adjust to point past the new smaller group
            # The new group has len(ielems) total lines (1 header + len(ielems)-1 element lines)
            line_index = grp_line + len(ielems)

    well_lines[ngrp_line] = '         ' + str(new_ngrp) + '                       / NGRP'
    well_lines.append('')

    # -- write out the submodel well specification file
    with open(new_filename, 'w', encoding='utf-8') as outfile:
        outfile.write('\n'.join(well_lines))

    if verbose:
        print(f'      Wrote well specification file {new_filename}')
        print("Leaving sub_gw_pump_well_file()")

    return new_nwells > 0

