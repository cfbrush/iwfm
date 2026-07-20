# get_stream_list_42.py
# Reads part of the stream specification file for file type 4.2
# and returns stream reach and rating table info
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


'''Read part of the stream specification file for file type 4.2 and return stream reach and rating table info.'''

def get_stream_list_42(stream_lines, line_index, nreach, nrate):
    '''Read part of the stream specification file for file type 4.2 and return stream reach and rating table info.

    Parameters
    ----------
    stream_lines : list of strings
        contents of stream specification file

    line_index : int
        current item in stream_lines

    nreach : int
        number of stream reaches

    nrate : int
        number of points in each stream node rating table

    Returns
    -------
    snode_ids : list
        list of model stream nodes

    snode_dict : dictionary
        keys = stream node IDs, values = associated groundwater nodes

    reach_info : list
        reach info lines for reaches in model

    rattab_dict : dictionary
        keys = stream node IDs, values = rating tables

    rating_header : str
        header info for rating tables including factors

    stream_aq : str
        stream-aquifer section of stream preprocessor file
    '''
    from iwfm.file_utils import read_next_line_value

    def is_comment(line):
        return len(line) == 0 or line[0] in 'Cc*#'

    reach_info, snode_ids, rating_header, stream_aq = [], [], [], []

    # -- first section, reaches
    snode_dict = {}
    for _ in range(nreach):
        # Read reach info line using file_utils
        _, line_index = read_next_line_value(stream_lines, line_index, column=0)
        info = stream_lines[line_index].split()  # -- get reach information

        snodes_temp, gwnodes_temp = [], []
        nnodes = int(info[1])

        for _ in range(nnodes):
            # Read stream node line using file_utils
            _, line_index = read_next_line_value(stream_lines, line_index, column=0)
            temp = stream_lines[line_index].split()
            snode_id = int(temp[0])
            gwnode_id = int(temp[1])
            snodes_temp.append(snode_id)
            gwnodes_temp.append(gwnode_id)
            snode_ids.append(snode_id)
            snode_dict[snode_id] = gwnode_id

        reach_info.append(
            [
                int(info[0]),
                int(info[1]),
                int(info[2]),
                ' '.join(info[3:]),
                snodes_temp,
                gwnodes_temp,
            ]
        )

    # -- second section, rating table factors: comments, then the three
    #    factor lines (FACTLT, FACTQ, TUNIT), then comments
    line_index += 1
    while is_comment(stream_lines[line_index]):
        rating_header.append(stream_lines[line_index])
        line_index += 1

    for _ in range(3):
        rating_header.append(stream_lines[line_index])
        line_index += 1

    while is_comment(stream_lines[line_index]):
        rating_header.append(stream_lines[line_index])
        line_index += 1

    # -- read in the rating tables for each stream node
    rattab_dict = {}
    line_index -= 1  # back up one before starting
    for sn in snode_ids:
        rt_temp = []
        for _ in range(nrate):
            # Read rating table line using file_utils
            _, line_index = read_next_line_value(stream_lines, line_index, column=0)
            rt_temp.append(stream_lines[line_index])
        rattab_dict[sn] = rt_temp

    # -- copy the last section, partial stream-aquifer interaction, to a list
    line_index += 1
    while line_index < len(stream_lines):
        stream_aq.append(stream_lines[line_index])
        line_index += 1

    return snode_ids, snode_dict, reach_info, rattab_dict, rating_header, stream_aq
