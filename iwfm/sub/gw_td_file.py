# sub_gw_td_file.py
# Copies the groundwater tile drain file and replaces the contents with those of the new
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


def sub_gw_td_file(old_filename, new_filename, node_list, verbose=False):
    '''sub_gw_td_file() - Read the original tile drain main file, determine
        which components are in the submodel, and write out a new file

    Parameters
    ----------
    old_filename : str
        name of existing model tile drain file

    new_filename : str
        name of new submodel tile drain file

    node_list : list of ints
        list of existing model nodes in submodel

    verbose : bool, default=False
        turn command-line output on or off

    Returns
    -------
    ntd > 0 : bool
        True if there are any tile drains in the submodel, False otherwise

    '''
    import iwfm
    from iwfm.file_utils import read_next_line_value, skip_to_next_line

    if verbose: print(f"Entered sub_gw_td_file() with {old_filename}")

    nodes = list(node_list)

    iwfm.file_test(old_filename)
    with open(old_filename, encoding='utf-8') as f:
        td_lines = f.read().splitlines()
    td_lines.append('')

    # -- tile drains
    # Skip initial comments and read ntd (number of tile drains)
    ntd_str, line_index = read_next_line_value(td_lines, -1, column=0, skip_lines=0)
    ntd = int(ntd_str)
    ntd_line = line_index

    # Skip factors (4 data lines) to reach tile drain data
    line_index = skip_to_next_line(td_lines, line_index - 1, skip_lines=4)
    new_ntd = 0

    # remove tile drains nodes that are not in the submodel
    td_keep = []
    if ntd > 0:
        for l in range(0,ntd):
            t = td_lines[line_index].split()
            if (int(t[1]) not in nodes):
                del td_lines[line_index]
            else:
                td_keep.append(int(t[1]))
                new_ntd += 1
                line_index += 1
        line_index = skip_to_next_line(td_lines, line_index - 1, skip_lines=0)       # skip comments to next section

    td_lines[ntd_line] = '         ' + str(new_ntd) + '                       / NTD'

    # -- subsurface irrigation
    nsi = int(td_lines[line_index].split()[0])                  # number of subsurface irrigation nodes
    nsi_line = line_index

    # Skip factors (4 data lines) to reach subsurface irrigation data
    _, line_index = read_next_line_value(td_lines, line_index, column=0, skip_lines=3)
    new_nsi = 0

    # remove subsurface irrigation for nodes that are not in the submodel
    if nsi > 0:
        for l in range(0,nsi):
            t = td_lines[line_index].split()
            if (int(t[1]) not in nodes):
                del td_lines[line_index]
            else:
                new_nsi += 1
                line_index += 1
        line_index = skip_to_next_line(td_lines, line_index - 1, skip_lines=0)       # skip comments to next section

    td_lines[nsi_line] = '         ' + str(new_nsi) + '                       / NSI'

    # -- tile drain hydrographs
    nhyd = int(td_lines[line_index].split()[0])                    # number of hydrographs
    nhyd_line = line_index

    # Skip factors (4 data lines) to reach hydrograph data
    line_index = skip_to_next_line(td_lines, line_index - 1, skip_lines=4)
    new_nhyd = 0

    # remove hydrographs for tile drains that are not in the submodel
    if nhyd > 0:
        for l in range(0,nhyd):
            t = td_lines[line_index].split()
            if (int(t[1]) not in td_keep):
                del td_lines[line_index]
            else:
                new_nhyd += 1
                line_index += 1

    td_lines[nhyd_line] = '         ' + str(new_nhyd) + '                       / NOUTTD'

    td_lines.append('')

    with open(new_filename, 'w', encoding='utf-8') as outfile:
        outfile.write('\n'.join(td_lines))

    if verbose:
        print(f'      Wrote tile drain file {new_filename}')
        print("Leaving sub_gw_td_file()")

    return ntd > 0
