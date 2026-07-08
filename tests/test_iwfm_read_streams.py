#!/usr/bin/env python
# test_iwfm_read_streams.py
# Unit tests for iwfm_read_streams.py
# Copyright (C) 2026 University of California
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

import pytest
import tempfile
import os


def create_iwfm_streams_file(stream_type, nreach, nrtb, reaches_data):
    """Create properly structured IWFM Streams file for testing.

    IWFM File Format Convention:
    - Comment lines start with 'C', 'c', '*', or '#' in column 1
    - Data lines MUST start with whitespace (space or tab)

    Parameters
    ----------
    stream_type : str
        Stream package version ('4.0', '4.1', '4.2', '5', or other)
    nreach : int
        Number of stream reaches
    nrtb : int
        Number of rating table data points
    reaches_data : list of tuples
        Each tuple: (reach_id, n_nodes, outflow_node, nodes_data)
        For stream type 5: (reach_id, upstream_node, downstream_node, outflow_node, nodes_data)
        nodes_data: list of tuples (stream_node, gw_node)

    Returns
    -------
    str
        File contents
    """
    # Header with stream type
    content = f"#{stream_type}\n"
    content += "C IWFM Stream Geometry Data File\n"
    content += "C\n"

    # Number of reaches and rating table points
    content += f"    {nreach}                         / NSREACH\n"
    content += f"    {nrtb}                          / NRATING\n"
    content += "C\n"

    # Stream reaches and nodes
    for reach_data in reaches_data:
        if stream_type in ['4.0', '4.1', '4.2']:
            reach_id, n_nodes, outflow, nodes_data = reach_data
            content += f"C REACH {reach_id}\n"
            content += f"     {reach_id}       {n_nodes}        {outflow}\n"
        elif stream_type == '5':
            reach_id, upstream, downstream, outflow, nodes_data = reach_data
            content += f"C REACH {reach_id}\n"
            content += f"     {reach_id}       {upstream}        {downstream}       {outflow}\n"
        else:  # old format
            reach_id, upstream, downstream, outflow, nodes_data = reach_data
            content += f"C REACH {reach_id}\n"
            content += f"     {reach_id}       {upstream}        {downstream}       {outflow}\n"

        content += "C Stream  Groundwater\n"
        for stream_node, gw_node in nodes_data:
            content += f"    {stream_node}\t{gw_node}\n"

    content += "C\n"
    content += "C Stream node rating tables (skip 3 data lines)\n"
    content += " \n"  # blank data line 1
    content += " \n"  # blank data line 2
    content += " \n"  # blank data line 3
    content += "C\n"

    # Rating tables for each stream node
    all_nodes = []
    for reach_data in reaches_data:
        if stream_type in ['4.0', '4.1', '4.2']:
            nodes_data = reach_data[3]
        else:
            nodes_data = reach_data[4]
        all_nodes.extend(nodes_data)

    for stream_node, gw_node in all_nodes:
        # Rating table header: stream_node, bottom_elev, initial_stage, initial_flow
        # The first rating entry uses positions [2] and [3] for initial stage and flow
        content += f"{stream_node}\t50.0\t1.0\t100.0\n"

        # Rating table data (nrtb-1 data lines)
        for i in range(nrtb - 1):
            stage = 10.0 + i * 5.0
            flow = 1000.0 + i * 500.0
            content += f"\t\t{stage}\t{flow}\n"

    content += "C End of file\n"
    return content


class TestIwfmReadStreams:
    """Tests for iwfm_read_streams function"""

    def test_stream_type_4_2_single_reach(self):
        """Test reading stream type 4.2 with single reach"""
        reaches_data = [
            (1, 3, 0, [(1, 100), (2, 101), (3, 102)])
        ]
        content = create_iwfm_streams_file('4.2', 1, 5, reaches_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_streams import iwfm_read_streams

            reach_list, snodes_list, stnodes_dict, n_snodes, rating_dict = iwfm_read_streams(temp_file)

            # Verify one reach
            assert len(reach_list) == 1
            assert reach_list[0][0] == 1  # reach ID
            assert reach_list[0][1] == 1  # upper node
            assert reach_list[0][2] == 3  # lower node
            assert reach_list[0][3] == 0  # outflow

            # Verify stream nodes
            assert n_snodes == 3
            assert len(snodes_list) == 3
            assert len(stnodes_dict) == 3

            # Verify stnodes_dict structure: key=stream_node, values=[gw_node, reach, elevation]
            assert stnodes_dict[1][0] == 100  # GW node
            assert stnodes_dict[1][1] == 1    # Reach
            assert stnodes_dict[1][2] == 50.0  # Elevation

            # Verify rating tables exist
            assert len(rating_dict) == 3
            assert '1' in rating_dict
            assert len(rating_dict['1']) == 5  # nrtb entries

        finally:
            os.unlink(temp_file)

    def test_stream_type_4_2_multiple_reaches(self):
        """Test reading stream type 4.2 with multiple reaches"""
        reaches_data = [
            (1, 2, 3, [(1, 100), (2, 101)]),
            (2, 2, 0, [(3, 200), (4, 201)])
        ]
        content = create_iwfm_streams_file('4.2', 2, 5, reaches_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_streams import iwfm_read_streams

            reach_list, snodes_list, stnodes_dict, n_snodes, rating_dict = iwfm_read_streams(temp_file)

            # Verify two reaches
            assert len(reach_list) == 2
            assert reach_list[0] == [1, 1, 2, 3]  # Reach 1 flows to node 3
            assert reach_list[1] == [2, 3, 4, 0]  # Reach 2 flows out

            # Verify 4 stream nodes total
            assert n_snodes == 4
            assert len(snodes_list) == 4

            # Verify reach assignments
            assert stnodes_dict[1][1] == 1  # Node 1 in reach 1
            assert stnodes_dict[2][1] == 1  # Node 2 in reach 1
            assert stnodes_dict[3][1] == 2  # Node 3 in reach 2
            assert stnodes_dict[4][1] == 2  # Node 4 in reach 2

        finally:
            os.unlink(temp_file)

    def test_stream_type_5_format(self):
        """Test reading stream type 5 format (with upstream/downstream nodes)"""
        reaches_data = [
            (1, 1, 3, 0, [(1, 100), (2, 101), (3, 102)])
        ]
        content = create_iwfm_streams_file('5', 1, 5, reaches_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_streams import iwfm_read_streams

            reach_list, snodes_list, stnodes_dict, n_snodes, rating_dict = iwfm_read_streams(temp_file)

            # Verify reach
            assert len(reach_list) == 1
            assert reach_list[0][0] == 1  # reach ID
            assert reach_list[0][1] == 1  # upper node
            assert reach_list[0][2] == 3  # lower node

            # Verify nodes
            assert n_snodes == 3

        finally:
            os.unlink(temp_file)

    def test_stream_type_4_0_format(self):
        """Test reading stream type 4.0 format"""
        reaches_data = [
            (1, 2, 0, [(1, 100), (2, 101)])
        ]
        content = create_iwfm_streams_file('4.0', 1, 5, reaches_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_streams import iwfm_read_streams

            reach_list, snodes_list, stnodes_dict, n_snodes, rating_dict = iwfm_read_streams(temp_file)

            # Verify basic structure
            assert len(reach_list) == 1
            assert n_snodes == 2
            assert len(stnodes_dict) == 2

        finally:
            os.unlink(temp_file)

    def test_single_node_reach(self):
        """Test reach with single stream node"""
        reaches_data = [
            (1, 1, 0, [(1, 100)])
        ]
        content = create_iwfm_streams_file('4.2', 1, 5, reaches_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_streams import iwfm_read_streams

            reach_list, snodes_list, stnodes_dict, n_snodes, rating_dict = iwfm_read_streams(temp_file)

            # Verify single node reach (upper = lower)
            assert reach_list[0][1] == 1  # upper
            assert reach_list[0][2] == 1  # lower (same as upper for single node)

        finally:
            os.unlink(temp_file)

    def test_reach_connectivity(self):
        """Test reach connectivity (upstream/downstream relationships)"""
        reaches_data = [
            (1, 2, 5, [(1, 100), (2, 101)]),
            (2, 2, 5, [(3, 200), (4, 201)]),
            (3, 3, 0, [(5, 300), (6, 301), (7, 302)])
        ]
        content = create_iwfm_streams_file('4.2', 3, 5, reaches_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_streams import iwfm_read_streams

            reach_list, snodes_list, stnodes_dict, n_snodes, rating_dict = iwfm_read_streams(temp_file)

            # Verify connectivity
            assert reach_list[0][3] == 5  # Reach 1 flows to node 5
            assert reach_list[1][3] == 5  # Reach 2 flows to node 5
            assert reach_list[2][3] == 0  # Reach 3 flows out

            # Verify node 5 is the confluence
            assert stnodes_dict[5][1] == 3  # Node 5 belongs to reach 3

        finally:
            os.unlink(temp_file)

    def test_rating_table_structure(self):
        """Test that rating tables are correctly read"""
        reaches_data = [
            (1, 2, 0, [(1, 100), (2, 101)])
        ]
        content = create_iwfm_streams_file('4.2', 1, 6, reaches_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_streams import iwfm_read_streams

            reach_list, snodes_list, stnodes_dict, n_snodes, rating_dict = iwfm_read_streams(temp_file)

            # Verify rating dict has entries for all nodes
            assert '1' in rating_dict
            assert '2' in rating_dict

            # Verify rating table has correct number of entries (nrtb)
            assert len(rating_dict['1']) == 6
            assert len(rating_dict['2']) == 6

            # Verify rating table data structure
            # First entry is [initial_stage, initial_flow]
            assert len(rating_dict['1'][0]) == 2
            # Subsequent entries are [stage, flow]
            assert len(rating_dict['1'][1]) == 2

        finally:
            os.unlink(temp_file)

    def test_comment_lines_skipped(self):
        """Test that comment lines are properly skipped"""
        # Create file with extra comment lines
        content = "#4.2\n"
        content += "C Comment with C\n"
        content += "c Comment with lowercase c\n"
        content += "* Comment with asterisk\n"
        content += "# Comment with hash\n"
        content += "    2                         / NSREACH\n"
        content += "    5                          / NRATING\n"
        content += "C More comments\n"
        content += "C REACH 1\n"
        content += "     1       2        3\n"
        content += "    1\t100\n"
        content += "    2\t101\n"
        content += "C REACH 2\n"
        content += "     2       1        0\n"
        content += "    3\t200\n"
        content += "C Rating tables (skip 3 data lines)\n"
        content += " \n"  # blank data line 1
        content += " \n"  # blank data line 2
        content += " \n"  # blank data line 3
        content += "C\n"
        for node in [1, 2, 3]:
            content += f"{node}\t50.0\t1.0\t100.0\n"
            for i in range(4):  # nrtb=5, so 4 data lines
                content += f"\t\t{10.0 + i*5.0}\t{1000.0 + i*500.0}\n"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_streams import iwfm_read_streams

            reach_list, snodes_list, stnodes_dict, n_snodes, rating_dict = iwfm_read_streams(temp_file)

            # Verify data was read correctly despite comment lines
            assert len(reach_list) == 2
            assert n_snodes == 3

        finally:
            os.unlink(temp_file)

    def test_return_structure(self):
        """Test that function returns correct tuple structure"""
        reaches_data = [
            (1, 2, 0, [(1, 150), (2, 151)])
        ]
        content = create_iwfm_streams_file('4.2', 1, 5, reaches_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_streams import iwfm_read_streams

            result = iwfm_read_streams(temp_file)

            # Verify return is tuple of 5 elements
            assert isinstance(result, tuple)
            assert len(result) == 5

            reach_list, snodes_list, stnodes_dict, n_snodes, rating_dict = result

            # Verify types
            assert isinstance(reach_list, list)
            assert isinstance(snodes_list, list)
            assert isinstance(stnodes_dict, dict)
            assert isinstance(n_snodes, int)
            assert isinstance(rating_dict, dict)

        finally:
            os.unlink(temp_file)

    def test_snodes_list_structure(self):
        """Test that snodes_list has correct structure"""
        reaches_data = [
            (1, 3, 0, [(1, 100), (2, 101), (3, 102)])
        ]
        content = create_iwfm_streams_file('4.2', 1, 5, reaches_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_streams import iwfm_read_streams

            reach_list, snodes_list, stnodes_dict, n_snodes, rating_dict = iwfm_read_streams(temp_file)

            # Verify snodes_list structure: each element is [stream_node, gw_node, reach]
            assert len(snodes_list) == 3
            for snode in snodes_list:
                assert len(snode) == 3
                assert isinstance(snode[0], int)  # stream node
                assert isinstance(snode[1], int)  # gw node
                assert isinstance(snode[2], int)  # reach

            # Verify specific values
            assert snodes_list[0] == [1, 100, 1]
            assert snodes_list[1] == [2, 101, 1]
            assert snodes_list[2] == [3, 102, 1]

        finally:
            os.unlink(temp_file)

    def test_stnodes_dict_structure(self):
        """Test that stnodes_dict has correct structure"""
        reaches_data = [
            (1, 2, 0, [(1, 150), (2, 151)])
        ]
        content = create_iwfm_streams_file('4.2', 1, 5, reaches_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_streams import iwfm_read_streams

            reach_list, snodes_list, stnodes_dict, n_snodes, rating_dict = iwfm_read_streams(temp_file)

            # Verify dict structure: key=stream_node, value=[gw_node, reach, elevation]
            for stream_node in [1, 2]:
                assert stream_node in stnodes_dict
                assert len(stnodes_dict[stream_node]) == 3

            # Verify specific values
            assert stnodes_dict[1] == [150, 1, 50.0]
            assert stnodes_dict[2] == [151, 1, 50.0]

        finally:
            os.unlink(temp_file)

    def test_reach_list_structure(self):
        """Test that reach_list has correct structure"""
        reaches_data = [
            (5, 6, 0, [(1, 100), (2, 101), (3, 102), (4, 103), (5, 104), (6, 105)])
        ]
        content = create_iwfm_streams_file('4.2', 1, 5, reaches_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_streams import iwfm_read_streams

            reach_list, snodes_list, stnodes_dict, n_snodes, rating_dict = iwfm_read_streams(temp_file)

            # Verify reach list structure: [reach, upper, lower, oflow]
            assert len(reach_list) == 1
            assert len(reach_list[0]) == 4
            assert reach_list[0] == [5, 1, 6, 0]

        finally:
            os.unlink(temp_file)

    def test_zero_groundwater_nodes(self):
        """Test stream nodes with zero groundwater node (not connected to GW)"""
        reaches_data = [
            (1, 3, 0, [(1, 0), (2, 101), (3, 0)])
        ]
        content = create_iwfm_streams_file('4.2', 1, 5, reaches_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_streams import iwfm_read_streams

            reach_list, snodes_list, stnodes_dict, n_snodes, rating_dict = iwfm_read_streams(temp_file)

            # Verify nodes with zero GW connection
            assert stnodes_dict[1][0] == 0    # No GW node
            assert stnodes_dict[2][0] == 101  # Has GW node
            assert stnodes_dict[3][0] == 0    # No GW node

        finally:
            os.unlink(temp_file)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])


class TestIwfmReadStreamsVersions:
    """Version handling for the preprocessor stream spec reader."""

    def _spec_4x(self, version):
        return (
            f"#{version}\n"
            "C stream spec\n"
            "     1                          / NRH\n"
            "     2                          / NRTB\n"
            "\t1\t2\t0\tOnly Creek\n"
            "\t1\t101\n"
            "\t2\t102\n"
            "C rating tables\n"
            "     1.0                         / FACTLT\n"
            "     60.0                        / FACTQ\n"
            "     1min                        / TUNIT\n"
            "\t1\t100.0\t0.0\t0.0\n"
            "\t\t2.0\t50.0\n"
            "\t2\t95.0\t0.0\t0.0\n"
            "\t\t2.0\t60.0\n"
        )

    def test_version_42(self, tmp_path):
        import iwfm
        f = tmp_path / 's.dat'
        f.write_text(self._spec_4x('4.2'))
        reach_list, snodes_list, stnodes_dict, n, rating_dict = iwfm.iwfm_read_streams(str(f))
        assert n == 2
        assert reach_list == [[1, 1, 2, 0]]
        assert stnodes_dict[1] == [101, 1, 100.0]
        assert len(rating_dict) == 2

    def test_version_50_no_rating_tables(self, tmp_path):
        import iwfm
        content = (
            "#5.0\n"
            "C v5.0 stream spec\n"
            "     2                          / NRH\n"
            "\t1\t2\t3\tUpper Creek\n"
            "\t1\t101\n"
            "\t2\t102\n"
            "\t2\t2\t0\tLower Creek\n"
            "\t3\t103\n"
            "\t4\t104\n"
            "     0                           / NSTRPINT\n"
        )
        f = tmp_path / 's50.dat'
        f.write_text(content)
        reach_list, snodes_list, stnodes_dict, n, rating_dict = iwfm.iwfm_read_streams(str(f))
        assert n == 4
        assert reach_list == [[1, 1, 2, 3], [2, 3, 4, 0]]
        assert rating_dict == {}
        assert stnodes_dict[3] == [103, 2, 0.0]
