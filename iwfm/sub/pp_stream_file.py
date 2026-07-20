# sub_pp_stream_file.py
# Copies the old stream file and replaces the contents with those of the new
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


'''Copy the old stream file and replaces the contents with those of the new submodel, and write out the new file.'''

def sub_pp_stream_file(stream_file, new_stream_file, snode_dict, reach_info,
    rattab_dict, rating_header, stream_aq):
    '''Copy the original stream specification file and replace the contents with those of the new model, and write out the new file.

    Parameters
    ----------
    stream_file : str
        name of existing preprocessor node file

    new_stream_file : str
        name of submodel preprocessor node file

    snode_dict : ints
        dictionary of existing model stream nodes in submodel

    reach_info : str
        reach info line for reaches in submodel

    rattab_dict : dict
        rating tables for stream nodes in submodel

    rating_header : str
        header info for rating tables including factors

    stream_aq : str
        stream-aquifer section of stream preprocessor file

    Returns
    -------
    nothing
    '''
    import iwfm
    from iwfm.file_utils import read_next_line_value

    iwfm.file_test(stream_file)
    with open(stream_file, encoding='utf-8') as f:
        stream_lines = f.read().splitlines()

    stream_type = stream_lines[0][1:]

    # Skip comments to NRH line
    _, line_index = read_next_line_value(stream_lines, -1, column=0, skip_lines=0)
    sub_stream_lines = stream_lines[:line_index]

    # -- number of stream reaches
    sub_stream_lines.append(
        (' ' * 4 + str(len(reach_info))).ljust(35)  # indent 4 chars, pad to 35
        + ' '.join(stream_lines[line_index].split()[1:])
    )

    # -- number of points in each rating table (not present in v5.0 files)
    if stream_type != '5.0':
        # use the original NRTB line for its description text
        _, nrtb_index = read_next_line_value(stream_lines, line_index, column=0, skip_lines=0)
        rattab_sns = [*rattab_dict]
        sub_stream_lines.append(
            (' ' * 4 + str(len(rattab_dict[rattab_sns[0]]))).ljust(35)  # indent 4 chars, pad to 35
            + ' '.join(stream_lines[nrtb_index].split()[1:])
        )

    # -- write stream reach and rating table information
    if stream_type == '4.0':
        sub_stream_lines = add_streams_40(sub_stream_lines, reach_info, snode_dict, rattab_dict,
            rating_header, stream_aq)
    elif stream_type == '4.1':
        sub_stream_lines = add_streams_41(sub_stream_lines, reach_info, snode_dict, rattab_dict,
            rating_header, stream_aq)
    elif stream_type == '4.2':
        sub_stream_lines = add_streams_42( sub_stream_lines, reach_info, snode_dict, rattab_dict,
            rating_header, stream_aq)
    elif stream_type == '5.0':
        sub_stream_lines = add_streams_50(sub_stream_lines, reach_info, snode_dict, stream_aq)
    else:
        exit_now(stream_type)

    sub_stream_lines.append('')
    # -- write new stream specification file
    with open(new_stream_file, 'w', encoding='utf-8') as outfile:
        outfile.write('\n'.join(sub_stream_lines))

    return


def add_streams_42(sub_stream_lines, reach_info, snode_dict, rattab_dict, rating_header, stream_aq):
    '''Add the reach and rating table info in the format of stream file type 4.2.

    Parameters
    ----------
    sub_stream_lines : list
        sumbodel stream file being assembled

    reach_info : list
        one entry per reach as [id, nrd, idwn, name, [stream_node_ids]]:
        id (int) reach number; nrd (int) count of stream nodes in the reach;
        idwn (int) outflow stream node (0 = leaves model, -nlk = into lake);
        name (str) reach name; followed by the list of stream node ids that
        make up the reach.

    snode_dict : dictionary
        key = stream node ID, values = groundwater node

    rattab_dict : dictionary
        key = stream node ID, values = rating table contents

    rating_header : list of strings
        rating table comments and flags/constants from original streams file

    stream_aq : list of strings
        stream-aquifer section of original streams file

    Returns
    -------
    sub_stream_lines : list
        the input list with the new model's reach descriptions, rating
        tables, and stream-aquifer section appended in stream-file v4.2
        format. Ready to be written out as the submodel stream file.
    '''
    return _add_streams(sub_stream_lines, reach_info, snode_dict, rattab_dict,
                        rating_header, stream_aq,
                        reaches_header_42, reach_header_42, snodes_header_42)


def add_streams_40(sub_stream_lines, reach_info, snode_dict, rattab_dict, rating_header, stream_aq):
    '''Add the reach and rating table info in the format of stream file type 4.0.

    Same layout as 4.2 (one groundwater node per stream node; BOTR/HRTB/QRTB rating rows carried verbatim).

    Parameters and return value are the same as :func:`add_streams_42`.
    '''
    return _add_streams(sub_stream_lines, reach_info, snode_dict, rattab_dict,
                        rating_header, stream_aq,
                        reaches_header_40, reach_header_42, snodes_header_42)


def add_streams_41(sub_stream_lines, reach_info, snode_dict, rattab_dict, rating_header, stream_aq):
    '''Add the reach and rating table info in the format of stream file type 4.1.

    Same layout as 4.2 except rating table rows carry an extra wetted-perimeter column (WPTB), which passes through verbatim.

    Parameters and return value are the same as :func:`add_streams_42`.
    '''
    return _add_streams(sub_stream_lines, reach_info, snode_dict, rattab_dict,
                        rating_header, stream_aq,
                        reaches_header_41, reach_header_42, snodes_header_42)


def add_streams_50(sub_stream_lines, reach_info, snode_dict, stream_aq):
    '''Add the reach info in the format of stream file type 5.0.

    Version 5.0 preprocessor files carry no rating tables (those moved to the simulation stream file).

    Parameters and return value are the same as :func:`add_streams_42`,
    without the rating-table arguments.
    '''
    return _add_streams(sub_stream_lines, reach_info, snode_dict, {}, [],
                        stream_aq,
                        reaches_header_40, reach_header_42, snodes_header_42)


def _add_streams(sub_stream_lines, reach_info, snode_dict, rattab_dict,
                 rating_header, stream_aq, reaches_header, reach_header,
                 snodes_header):
    '''Shared engine: append reach descriptions, rating tables (if any), and the stream-aquifer section to the submodel stream file lines.



    '''

    # -- write stream reaches
    for s in reaches_header:
        sub_stream_lines.append(s)

    for r in reach_info:
        sub_stream_lines.append('C     REACH   ' + str(r[0]))
        for s in reach_header:
            sub_stream_lines.append(s)
        # write reach information
        sub_stream_lines.append(
            '\t' + str(r[0]) + '\t' + str(r[1]) + '\t' + str(r[2]) + '\t' + r[3]
        )
        for s in snodes_header:
            sub_stream_lines.append(s)
        # write reach stream nodes
        for sn in r[4]:
            sub_stream_lines.append('\t' + str(sn) + '\t' + str(snode_dict[sn]))
        sub_stream_lines.append(
            'C-------------------------------------------------------------------------------'
        )

    # -- write rating tables
    for s in rating_header:
        sub_stream_lines.append(s)

    rattab_sns = [*rattab_dict]
    for sn in rattab_sns:
        for s in rattab_dict[sn]:
            sub_stream_lines.append(s)

    # -- write stream-aquifer section
    for s in stream_aq:
        sub_stream_lines.append(s)

    return sub_stream_lines


reaches_header_42 = [
    'C*******************************************************************************',
    'C                      Description of Stream Reaches',
    'C',
    'C   The following lists the stream nodes and corresponding groundwater',
    'C   nodes for each stream reach modeled in IWFM.',
    'C',
    'C   ID;    Reach number',
    'C   IBUR;  First upstream stream node of the reach',
    'C   IBDR;  Last downstream node of the reach',
    'C   IDWN;  Stream node into which the reach flows into',
    'C              0: If stream flow leaves the modeled area',
    'C           -nlk: If stream flows into lake number nlk',
    'C   NAME;  Name of the reach (maximum 20 characters)',
    'C',
    'C   In addition, for each stream node within the reach the corresponding',
    'C   groundwater nodes is listed.',
    'C',
    'C   IRV;   Stream node',
    'C   IGW;   Corresponding groundwater node(s) (can be more than one for wide streams)',
    'C           * Note: For wide streams with more than one corresponding groundwater nodes,',
    'C                    the groundwater node that is closest to the middle of the channel',
    'C                    cross-section must be listed first.',
    'C',
    'C-------------------------------------------------------------------------------',
]

reaches_header_40 = [
    'C*******************************************************************************',
    'C                      Description of Stream Reaches',
    'C',
    'C   The following lists the stream nodes and corresponding groundwater',
    'C   nodes for each stream reach modeled in IWFM.',
    'C',
    'C   ID;    Reach number',
    'C   NRD;   Number of stream nodes in reach',
    'C   IDWN;  Stream node into which the reach flows into',
    'C              0: If stream flow leaves the modeled area',
    'C           -nlk: If stream flows into lake number nlk',
    'C   NAME;  Name of the reach (maximum 20 characters)',
    'C',
    'C   In addition, for each stream node within the reach the corresponding',
    'C   groundwater node is listed.',
    'C',
    'C   IRV;   Stream node',
    'C   IGW;   Corresponding groundwater node',
    'C',
    'C-------------------------------------------------------------------------------',
]

reaches_header_41 = [
    'C*******************************************************************************',
    'C                      Description of Stream Reaches',
    'C',
    'C   The following lists the stream nodes and corresponding groundwater',
    'C   nodes for each stream reach modeled in IWFM.',
    'C',
    'C   ID;    Reach number',
    'C   NRD;   Number of stream nodes in reach',
    'C   IDWN;  Stream node into which the reach flows into',
    'C              0: If stream flow leaves the modeled area',
    'C           -nlk: If stream flows into lake number nlk',
    'C   NAME;  Name of the reach (maximum 20 characters)',
    'C',
    'C   In addition, for each stream node within the reach the corresponding',
    'C   groundwater node is listed.',
    'C',
    'C   IRV;   Stream node',
    'C   IGW;   Corresponding groundwater node',
    'C',
    'C-------------------------------------------------------------------------------',
]

reach_header_42 = [
    'C	Reach	Number	Outflow	Reach',
    'C	Node	Nodes	Node	Name',
    'C	ID	NRD	IDWN	NAME',
    'C-------------------------------------------------------------------------------',
]

snodes_header_42 = [
    'C-------------------------------------------------------------------------------',
    'C	Stream	Groundwater',
    'C    node  node',
    'C	IRV	IGW',
    'C-------------------------------------------------------------------------------',
]


def exit_now(stream_type):
    raise NotImplementedError(
        f'sub_pp_stream_file(): no method to write stream specification type '
        f'{stream_type!r}'
    )
