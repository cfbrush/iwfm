# get_stream_list_50.py
# Reads part of the stream specification file for file type 5.0
# and returns stream reach info
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


'''Read part of the stream specification file for file type 5.0 and return stream reach info.'''

def get_stream_list_50(stream_lines, line_index, nreach):
    '''Read part of the stream specification file for file type 5.0 and return stream reach info.

    Version 5.0 stream specification files contain only NRH, the reach
    descriptions, and the partial stream-aquifer interaction section —
    rating tables (and NRTB) moved to the simulation stream file. The
    returned rattab_dict and rating_header are therefore empty.

    Parameters
    ----------
    stream_lines : list of strings
        contents of stream specification file

    line_index : int
        current item in stream_lines (the NRH line)

    nreach : int
        number of stream reaches

    Returns
    -------
    snode_ids : list
        list of model stream nodes

    snode_dict : dictionary
        keys = stream node IDs, values = associated groundwater nodes

    reach_info : list
        reach info lines for reaches in model

    rattab_dict : dictionary
        empty (no rating tables in v5.0 preprocessor files)

    rating_header : list
        empty (no rating tables in v5.0 preprocessor files)

    stream_aq : list of strings
        stream-aquifer section of stream preprocessor file
    '''
    from iwfm.file_utils import read_next_line_value

    reach_info, snode_ids, stream_aq = [], [], []

    # -- first section, reaches
    snode_dict = {}
    for _ in range(nreach):
        _, line_index = read_next_line_value(stream_lines, line_index, column=0)
        info = stream_lines[line_index].split()

        snodes_temp, gwnodes_temp = [], []
        nnodes = int(info[1])

        for _ in range(nnodes):
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

    # -- copy the last section, partial stream-aquifer interaction, to a list
    line_index += 1
    while line_index < len(stream_lines):
        stream_aq.append(stream_lines[line_index])
        line_index += 1

    return snode_ids, snode_dict, reach_info, {}, [], stream_aq
