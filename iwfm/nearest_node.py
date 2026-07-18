# nearest_node.py
# Read IWFM well file and return nearest IWFM node to an (x,y) location
# the nearest node to each (x,y) point
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


def nearest_node(point, node_set):
    '''Find the nearest node to a point from the node array.

    Parameters
    ----------
    point : tuple
        (x,y) point

    node_set : list
        list of [node_id, x, y] entries

    Returns
    -------
    nearest : int
        node id of the nearest node, or -1 if node_set is empty
    '''
    import math

    dist, nearest = 9.9e30, -1
    for j in range(0, len(node_set)):
        line = node_set[j]
        pt = [line[1], line[2]]
        # Compute distance between each pair of the two collections of inputs.
        new_dist = math.hypot(point[0] - pt[0], point[1] - pt[1])  # Euclidean distance
        if dist > new_dist:
            dist, nearest = new_dist, line[0]
    return nearest

def read_well_points(well_file):
    '''Read well locations from a text file.

    Accepts comma- or whitespace-separated lines of ``ID  X  Y`` (extra
    columns ignored). Comment lines starting with C, c, * or # and a
    non-numeric header line are skipped.

    Parameters
    ----------
    well_file : str
        well location file name

    Returns
    -------
    wells : list
        [well_id (str), x (float), y (float)] per well
    '''
    wells = []
    with open(well_file, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line[0] in 'Cc*#':
                continue
            parts = line.replace(',', ' ').split()
            if len(parts) < 3:
                continue
            try:
                wells.append([parts[0], float(parts[1]), float(parts[2])])
            except ValueError:
                continue  # header or other non-numeric line
    return wells


if __name__ == '__main__':
    ' Run nearest_node() from command line '
    import math
    import sys
    import iwfm.debug as idb
    import iwfm
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    if len(sys.argv) > 1:  # arguments are listed on the command line
        node_file = sys.argv[1]
        well_file = sys.argv[2]
        out_file = sys.argv[3] if len(sys.argv) > 3 else well_file.rsplit('.', 1)[0] + '_nodes.csv'
    else:  # ask for file names from terminal
        node_file = input('IWFM Node file name: ')
        well_file = input('Well file name (ID, X, Y): ')
        out_file = input('Output file name: ')

    iwfm.file_test(node_file)
    iwfm.file_test(well_file)

    idb.exe_time()  # initialize timer
    node_coord, node_list, factor = iwfm.iwfm_read_nodes(node_file)
    node_set = [[n[0], n[1] * factor, n[2] * factor] for n in node_coord]
    node_xy = {n[0]: (n[1], n[2]) for n in node_set}

    wells = read_well_points(well_file)
    if not wells:
        print(f'  No well locations found in {well_file}')
        sys.exit(1)

    with open(out_file, 'w', encoding='utf-8') as f:
        f.write('WellID,X,Y,NearestNode,Distance\n')
        for well_id, x, y in wells:
            nearest = nearest_node((x, y), node_set)
            nx, ny = node_xy[nearest]
            distance = math.hypot(x - nx, y - ny)
            f.write(f'{well_id},{x},{y},{nearest},{distance:.2f}\n')

    print(f'  Wrote nearest nodes for {len(wells)} wells to {out_file}')
    idb.exe_time()  # print elapsed time
