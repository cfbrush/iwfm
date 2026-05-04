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
    ''' nearest_node() - Find the nearest node to a point from the node array

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

if __name__ == '__main__':
    ' Run nearest_node() from command line '
    import sys
    import iwfm.debug as idb
    import iwfm
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    if len(sys.argv) > 1:  # arguments are listed on the command line
        node_file = sys.argv[1]
        well_file = sys.argv[2]
    else:  # ask for file names from terminal
        node_file = input('IWFM Node file name: ')
        well_file = input('Well file name: ')

    iwfm.file_test(node_file)
    iwfm.file_test(well_file)

    idb.exe_time()  # initialize timer
    node_coord, node_list, factor = iwfm.iwfm_read_nodes(node_file)
    # read list of points from well file
    # ** TODO: NEED TO ADD THIS PART **
    print(f'  ** NEED TO UPDATE nearest_node.py TO READ WELL FILE ')
    print(f'  ** EXITING')
    sys.exit()

    # Dead code - unreachable after sys.exit() and uses undefined variables (point, node_set)
    # cycle through points for nearest node
    # nearest = iwfm.nearest_node(point, node_set)
    #
    # idb.exe_time()  # print elapsed time
