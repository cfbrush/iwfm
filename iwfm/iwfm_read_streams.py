# iwfm_read_streams.py
# read IWFM preprocessor streams file
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


'''Read IWFM preprocessor streams file.'''

def iwfm_read_streams(stream_file, verbose=False):
    '''Read an IWFM Stream Geometry file and return a list of stream reaches, a dictionary of stream nodes, and the number of stream nodes.

    Parameters
    ----------
    stream_file : str
        IWFM Streams file name

    verbose : bool, default = False
        If True, print status messages.

    Returns
    -------
    reach_list : list
        information for each stream reach

    stnodes_dict : dictionary
        key = stream node ID, values = [groundwater node, reach, elevation]

    len(snodes_list) : int
        number of stream nodes

    rating_dict : dictionary
        key = stream node ID, values = rating table
    '''
    import iwfm
    from iwfm.file_utils import read_next_line_value

    if verbose: print(f"Entered iwfm_read_streams() with {stream_file}")

    comments = 'Cc*#'

    iwfm.file_test(stream_file)
    with open(stream_file, encoding='utf-8') as f:
        stream_lines = f.read().splitlines()
    stream_type = stream_lines[0][1:]

    nreach, stream_index = read_next_line_value(stream_lines, 0)
    nreach = int(nreach)

    if stream_type == '5.0':
        # v5.0 preprocessor stream files have no NRTB line or rating tables
        # (rating tables moved to the simulation stream file)
        rating = 0
    else:
        rating_str, stream_index = read_next_line_value(stream_lines, stream_index)
        rating = int(rating_str)

    # read in stream reaches
    reach_list, snodes_list = [], []
    for i in range(0, nreach):
        _, stream_index = read_next_line_value(stream_lines, stream_index)
        l = stream_lines[stream_index].split()

        reach = int(l.pop(0))

        # streams package versions 4.0, 4.1, 4.2, 5.0: ID NRD IDWN NAME
        if stream_type in ('4.0', '4.1', '4.2', '5.0'):
            snodes = int(l.pop(0))

        # older streams packages: ID IBUR IBDR IDWN NAME
        # (reach defined by upstream and downstream stream node numbers)
        else:
            up_node = int(l.pop(0))
            dn_node = int(l.pop(0))
            snodes = dn_node - up_node + 1

        oflow = int(l.pop(0))

        # read stream node information
        upper = None
        lower = None

        for j in range(0, snodes):
            _, stream_index = read_next_line_value(stream_lines, stream_index)
            l = stream_lines[stream_index].split()
            t = [int(l[0]), int(l[1]), reach]
            snodes_list.append(t)
            if j == 0:
                upper = int(l[0])
            else:
                lower = int(l[0])

        # Handle single-node stream reaches
        if snodes == 1:
            lower = upper

        reach_list.append([reach, upper, lower, oflow])

    rating_dict = {}
    if rating > 0:
        _, stream_index = read_next_line_value(stream_lines, stream_index, skip_lines=3)
        selev = []
        for i in range(0, len(snodes_list)):
            l = stream_lines[stream_index].split()
            snode = l[0]
            selev.append(float(l[1]))
            # read the rating table values for this stream node
            temp = [[l[2], l[3]]]
            stream_index += 1
            for t in range(0, rating - 1):
                if any((c in comments) for c in stream_lines[stream_index][0]):
                    stream_index += 1
                temp.append(stream_lines[stream_index].split())
                stream_index += 1
            rating_dict[snode] = temp   # key = stream node ID, values = rating table

            if i < len(snodes_list) - 1:  # stop at end
                _, stream_index = read_next_line_value(stream_lines, stream_index - 1)
    else:
        # no rating tables (v5.0): stream bottom elevations are not in this file
        selev = [0.0] * len(snodes_list)

    # put stream node info into a dictionary
    stnodes_dict, j = {}, 0
    for i, snode in enumerate(snodes_list):
        key, values = snode[0], [snode[1], snode[2], selev[i]]    # key = stream node ID, values = [groundwater node, reach, elevation]
        stnodes_dict[key] = values

    if verbose: print("Leaving iwfm_read_streams()")

    return reach_list, snodes_list, stnodes_dict, len(snodes_list), rating_dict
