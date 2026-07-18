# iwfm_nearest_nodes.py
# Read a file with (x,y) locations and an IWFM node file, and write a file with
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


def iwfm_nearest_nodes(filename, node_set):
    '''Read a point file, calculate the nearest node and distance for each point, and write the results to the output file.

    Parameters
    ----------
    out_file : str
        output file name base

    node_set : list
        node IDs and x,y locations

    Returns
    -------
    number of points processed
    '''
    import iwfm

    output_filename = filename[0 : filename.find('.')] + '_nearest_nodes.out'
    with open(output_filename, 'w', encoding='utf-8') as output_file:
        with open(filename, 'r', encoding='utf-8') as input_file:
            lines = input_file.read().splitlines()  # open and read input file
            header = lines[0].split(',')
            output_file.write(f'{header[0]},NdNear,NdDist\n')
            for line_index in range(1, len(lines)):  # skip header line
                point = lines[line_index].split(',')
                nearest, dist = iwfm.iwfm_nearest_node([float(point[1]), float(point[2])], node_set)
                # write out
                output_file.write(f'{point[0]},{nearest[0]},{round(dist,2)}\n')

    return len(lines) - 1

if __name__ == '__main__':
    ' Run iwfm_nearest_nodes() from command line '
    import sys
    import iwfm.debug as idb
    import iwfm
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    if len(sys.argv) > 1:  # arguments are listed on the command line
        node_file  = sys.argv[1]
        point_file = sys.argv[2]
    else:  # ask for file names from terminal
        node_file  = input('IWFM Node file basename: ')
        point_file = input('Point file name (csv): ')

    iwfm.file_test(node_file)
    iwfm.file_test(point_file)

    idb.exe_time()  # initialize timer
    node_coord, node_list, factor = iwfm.iwfm_read_nodes(node_file)
    lines = iwfm_nearest_nodes(point_file, node_coord)
    print(f'  Wrote {lines} lines to output file')
    idb.exe_time()  # print elapsed time


