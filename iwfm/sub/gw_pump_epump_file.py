# sub_gw_pump_epump_file.py
# Copies the old element pumping file and replaces the contents with those 
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


def sub_gw_pump_epump_file(old_filename, new_filename, elems, verbose=False):
    '''sub_gw_pump_epump_file() - Copies the old element pumping file and replaces
        the contents with those of the new submodel, and writes out the new file

    Parameters
    ----------
    old_filename : str
        name of existing model element pumping file

    new_filename : str
        name of new submodel element pumping file

    elems : list of ints
        list of existing model elements in submodel

    verbose : bool, default=False
        turn command-line output on or off

    Returns
    -------
    bool : new_nsink > 0
        True if there are any wells

    '''
    import iwfm
    from iwfm.file_utils import read_next_line_value

    if verbose: print(f"Entered sub_gw_pump_epump_file() with {old_filename}")

    iwfm.file_test(old_filename)
    with open(old_filename, encoding='utf-8') as f:
        epump_lines = f.read().splitlines()
    epump_lines.append('')

    # skip initial comments to get NSINK
    nsink_str, line_index = read_next_line_value(epump_lines, -1)
    if not nsink_str:
        raise ValueError(f"{old_filename} line {line_index}: Expected number of element pumping specs (NSINK), got empty line")
    nsink = int(nsink_str)

    new_nsink, nsink_line = 0, line_index

    # skip to first pumping spec
    _, line_index = read_next_line_value(epump_lines, line_index)

    for l in range(0, nsink):
        parts = epump_lines[line_index].split()
        if not parts:
            raise ValueError(f"{old_filename} line {line_index}: Expected element ID in pumping spec {l}, got empty line")
        if int(parts[0]) not in elems:
            del epump_lines[line_index]
        else:
            line_index += 1
            new_nsink += 1

    epump_lines[nsink_line] = '     ' + str(new_nsink) + '                       / NSINK'

    # element groups - collect them first, then write filtered groups
    ngrp_str, line_index = read_next_line_value(epump_lines, line_index - 1)
    if not ngrp_str:
        raise ValueError(f"{old_filename} line {line_index}: Expected number of element groups (NGRP), got empty line")
    ngrp = int(ngrp_str)
    ngrp_line = line_index

    # Read all element groups
    filtered_groups = []

    # Only process groups if there are any
    if ngrp > 0:
        # skip to first group
        _, line_index = read_next_line_value(epump_lines, line_index)
        group_start_line = line_index
    else:
        # No groups, set group_start_line to current position
        group_start_line = line_index + 1

    for id in range(0, ngrp):
        parts = epump_lines[line_index].split()
        if len(parts) < 3:
            raise ValueError(f"{old_filename} line {line_index}: Expected element group header (grp_id nelem first_elem), got only {len(parts)} values")
        grp_id, nelem, first_elem = int(parts[0]), int(parts[1]), int(parts[2])
        ielems = []

        # Check if first element is in submodel
        if first_elem in elems:
            ielems.append(first_elem)

        line_index += 1

        # Read remaining nelem-1 elements from continuation lines
        for j in range(1, nelem):
            parts = epump_lines[line_index].split()
            if not parts:
                raise ValueError(f"{old_filename} line {line_index}: Expected element ID in group {grp_id}, got empty line")
            ielem = int(parts[0])
            if ielem in elems:
                ielems.append(ielem)
            line_index += 1

        # Store filtered group if it has any elements
        if len(ielems) > 0:
            filtered_groups.append((grp_id, ielems))

    # Delete all original group lines
    total_group_lines = line_index - group_start_line
    for i in range(total_group_lines):
        del epump_lines[group_start_line]

    # Write filtered groups back
    new_lines = []
    for grp_id, ielems in filtered_groups:
        # First line: grp_id, nelem, first_elem
        new_lines.append(str(grp_id) + '\t' + str(len(ielems)) + '\t' + str(ielems[0]))
        # Continuation lines: remaining elements
        for i in range(1, len(ielems)):
            new_lines.append('\t\t' + str(ielems[i]))

    # Insert filtered groups
    for i, line in enumerate(new_lines):
        epump_lines.insert(group_start_line + i, line)

    # Update NGRP count
    epump_lines[ngrp_line] = '     ' + str(len(filtered_groups)) + '                  / NGRP'

    epump_lines.append('')

    with open(new_filename, 'w', encoding='utf-8') as outfile:
        outfile.write('\n'.join(epump_lines))

    if verbose:
        print(f'      Wrote element pumping file {new_filename}')
        print(f"Leaving sub_gw_pump_epump_file()")

    return new_nsink > 0
