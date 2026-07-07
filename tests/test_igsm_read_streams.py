#!/usr/bin/env python
# test_igsm_read_streams.py
# Unit tests for igsm_read_streams.py
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


def create_igsm_streams_file(nreach, nrtb, reaches_data):
    """Create properly structured IGSM Streams file for testing.

    IWFM File Format Convention:
    - Comment lines start with 'C', 'c', '*', or '#' in column 1
    - Data lines MUST start with whitespace (space or tab)

    Parameters
    ----------
    nreach : int
        Number of stream reaches
    nrtb : int
        Number of rating table data points
    reaches_data : list of tuples
        Each tuple: (reach_id, upstream_node, downstream_node, outflow_node, nodes_data, rating_elev)
        nodes_data: list of tuples (stream_node, gw_node, subregion)
        rating_elev: bottom elevation for rating table (int or float)

    Returns
    -------
    str
        File contents
    """
    # Header comments
    content = "C IGSM Stream Geometry Data File\n"
    content += "C\n"
    content += "C Stream reach and node information\n"
    content += "C\n"

    # Number of reaches and rating table points
    content += f"    {nreach}                         / NR\n"
    content += f"    {nrtb}                          / NRTB\n"
    content += "C\n"

    # Stream reaches and nodes
    for reach_id, upstream, downstream, outflow, nodes_data, rating_elev in reaches_data:
        content += f"C REACH {reach_id}\n"
        content += f"     {reach_id}       {upstream}        {downstream}       {outflow}\n"
        content += "C Stream  Groundwater  Subregion\n"

        for stream_node, gw_node, subregion in nodes_data:
            content += f"    {stream_node}\t{gw_node}\t{subregion}\n"

    content += "C\n"
    content += "C Stream node rating tables\n"
    content += "C\n"

    # Rating tables for each stream node
    for reach_id, upstream, downstream, outflow, nodes_data, rating_elev in reaches_data:
        for stream_node, gw_node, subregion in nodes_data:
            # Rating table header: stream_node, bottom_elev, initial_stage, initial_flow, initial_width
            # Use integer format for rating_elev to match real IGSM files
            elev_int = int(rating_elev)
            content += f"{stream_node}\t{elev_int}\t0.0\t0.0\t0.0\n"

            # Rating table data (nrtb-1 data lines, since nrtb includes the header)
            for i in range(nrtb - 1):
                stage = 10.0 + i * 5.0
                area = 100.0 + i * 50.0
                flow = 1000.0 + i * 500.0
                content += f"\t\t{stage}\t{area}\t{flow}\n"

    content += "C End of file\n"
    return content


class TestIgsmReadStreams:
    """Tests for igsm_read_streams function"""

    def test_single_reach_single_node(self):
        """Test reading single reach with single stream node"""
        reaches_data = [
            (1, 1, 1, 0, [(1, 100, 1)], 50.0)
        ]
        content = create_igsm_streams_file(1, 5, reaches_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.igsm_read_streams import igsm_read_streams

            reach_list, stnodes_dict, n_snodes = igsm_read_streams(temp_file)

            # Verify one reach
            assert len(reach_list) == 1
            assert reach_list[0] == [1, 1, 1, 0]  # [reach, upper, lower, oflow]

            # Verify one stream node
            assert n_snodes == 1
            assert len(stnodes_dict) == 1

            # Verify stream node 1: [GW_node, subregion, reach, bottom_elev]
            assert stnodes_dict[1][0] == 100  # GW node
            assert stnodes_dict[1][1] == 1    # Subregion
            assert stnodes_dict[1][2] == 1    # Reach
            assert stnodes_dict[1][3] == 50.0  # Bottom elevation (converted to float)

        finally:
            os.unlink(temp_file)

    def test_single_reach_multiple_nodes(self):
        """Test reading single reach with multiple stream nodes"""
        reaches_data = [
            (1, 1, 5, 0, [
                (1, 100, 1),
                (2, 101, 1),
                (3, 102, 1),
                (4, 103, 1),
                (5, 104, 1)
            ], 50.0)
        ]
        content = create_igsm_streams_file(1, 5, reaches_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.igsm_read_streams import igsm_read_streams

            reach_list, stnodes_dict, n_snodes = igsm_read_streams(temp_file)

            # Verify reach
            assert len(reach_list) == 1
            assert reach_list[0] == [1, 1, 5, 0]

            # Verify 5 stream nodes
            assert n_snodes == 5
            assert len(stnodes_dict) == 5

            # Verify stream nodes
            for i in range(1, 6):
                assert stnodes_dict[i][0] == 99 + i  # GW node
                assert stnodes_dict[i][1] == 1        # Subregion
                assert stnodes_dict[i][2] == 1        # Reach

        finally:
            os.unlink(temp_file)

    def test_multiple_reaches(self):
        """Test reading multiple stream reaches"""
        reaches_data = [
            (1, 1, 3, 4, [
                (1, 100, 1),
                (2, 101, 1),
                (3, 102, 1)
            ], 50.0),
            (2, 4, 6, 0, [
                (4, 200, 2),
                (5, 201, 2),
                (6, 202, 2)
            ], 45.0)
        ]
        content = create_igsm_streams_file(2, 5, reaches_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.igsm_read_streams import igsm_read_streams

            reach_list, stnodes_dict, n_snodes = igsm_read_streams(temp_file)

            # Verify two reaches
            assert len(reach_list) == 2
            assert reach_list[0] == [1, 1, 3, 4]  # Reach 1 flows to node 4
            assert reach_list[1] == [2, 4, 6, 0]  # Reach 2 flows to node 0 (outlet)

            # Verify 6 stream nodes total
            assert n_snodes == 6

            # Verify reach 1 nodes
            assert stnodes_dict[1][2] == 1  # Reach 1
            assert stnodes_dict[2][2] == 1
            assert stnodes_dict[3][2] == 1

            # Verify reach 2 nodes
            assert stnodes_dict[4][2] == 2  # Reach 2
            assert stnodes_dict[5][2] == 2
            assert stnodes_dict[6][2] == 2

        finally:
            os.unlink(temp_file)

    def test_reach_connectivity(self):
        """Test reach connectivity (upstream/downstream relationships)"""
        reaches_data = [
            (1, 1, 2, 5, [(1, 100, 1), (2, 101, 1)], 60.0),
            (2, 3, 4, 5, [(3, 200, 2), (4, 201, 2)], 55.0),
            (3, 5, 7, 0, [(5, 300, 3), (6, 301, 3), (7, 302, 3)], 50.0)
        ]
        content = create_igsm_streams_file(3, 5, reaches_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.igsm_read_streams import igsm_read_streams

            reach_list, stnodes_dict, n_snodes = igsm_read_streams(temp_file)

            # Verify connectivity
            assert reach_list[0][3] == 5  # Reach 1 flows to node 5
            assert reach_list[1][3] == 5  # Reach 2 flows to node 5
            assert reach_list[2][3] == 0  # Reach 3 flows out

            # Verify node 5 is the confluence
            assert stnodes_dict[5][2] == 3  # Node 5 belongs to reach 3

        finally:
            os.unlink(temp_file)

    def test_different_subregions(self):
        """Test stream nodes in different subregions"""
        reaches_data = [
            (1, 1, 5, 0, [
                (1, 100, 1),
                (2, 101, 1),
                (3, 102, 2),
                (4, 103, 3),
                (5, 104, 4)
            ], 50.0)
        ]
        content = create_igsm_streams_file(1, 5, reaches_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.igsm_read_streams import igsm_read_streams

            reach_list, stnodes_dict, n_snodes = igsm_read_streams(temp_file)

            # Verify different subregions
            assert stnodes_dict[1][1] == 1  # Subregion 1
            assert stnodes_dict[2][1] == 1  # Subregion 1
            assert stnodes_dict[3][1] == 2  # Subregion 2
            assert stnodes_dict[4][1] == 3  # Subregion 3
            assert stnodes_dict[5][1] == 4  # Subregion 4

        finally:
            os.unlink(temp_file)

    def test_zero_groundwater_nodes(self):
        """Test stream nodes with zero groundwater node (not connected to GW)"""
        reaches_data = [
            (1, 1, 3, 0, [
                (1, 0, 0),    # No GW connection (reservoir/boundary)
                (2, 101, 1),  # Normal connection
                (3, 0, 0)     # No GW connection
            ], 50.0)
        ]
        content = create_igsm_streams_file(1, 5, reaches_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.igsm_read_streams import igsm_read_streams

            reach_list, stnodes_dict, n_snodes = igsm_read_streams(temp_file)

            # Verify nodes with zero GW connection
            assert stnodes_dict[1][0] == 0  # No GW node
            assert stnodes_dict[2][0] == 101  # Has GW node
            assert stnodes_dict[3][0] == 0  # No GW node

        finally:
            os.unlink(temp_file)

    def test_rating_table_elevations(self):
        """Test that rating table elevations are correctly read"""
        reaches_data = [
            (1, 1, 3, 0, [
                (1, 100, 1),
                (2, 101, 1),
                (3, 102, 1)
            ], 55.5)  # Different elevation for each reach
        ]
        content = create_igsm_streams_file(1, 5, reaches_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.igsm_read_streams import igsm_read_streams

            reach_list, stnodes_dict, n_snodes = igsm_read_streams(temp_file)

            # Verify bottom elevations (4th element in dict values)
            # Input was 55.5, gets converted to int(55) in file, then to float(55.0) when read
            assert stnodes_dict[1][3] == 55.0
            assert stnodes_dict[2][3] == 55.0
            assert stnodes_dict[3][3] == 55.0

        finally:
            os.unlink(temp_file)

    def test_comment_lines_skipped(self):
        """Test that comment lines are properly skipped"""
        # Create file with extra comment lines
        content = "C Comment with C\n"
        content += "c Comment with lowercase c\n"
        content += "* Comment with asterisk\n"
        content += "# Comment with hash\n"
        content += "    2                         / NR\n"
        content += "    5                          / NRTB\n"
        content += "C More comments\n"
        content += "C REACH 1\n"
        content += "     1       1        2       3\n"
        content += "    1\t100\t1\n"
        content += "    2\t101\t1\n"
        content += "C REACH 2\n"
        content += "     2       3        3       0\n"
        content += "    3\t200\t2\n"
        content += "C Rating tables\n"
        for node in [1, 2, 3]:
            content += f"{node}\t50\t0.0\t0.0\t0.0\n"  # Use int for bottom_elev
            for i in range(4):  # nrtb=5, so 4 data lines (nrtb-1)
                content += f"\t\t{10.0 + i*5.0}\t{100.0 + i*50.0}\t{1000.0 + i*500.0}\n"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.igsm_read_streams import igsm_read_streams

            reach_list, stnodes_dict, n_snodes = igsm_read_streams(temp_file)

            # Verify data was read correctly despite comment lines
            assert len(reach_list) == 2
            assert n_snodes == 3

        finally:
            os.unlink(temp_file)

    def test_stnodes_dict_structure(self):
        """Test that stnodes_dict has correct structure"""
        reaches_data = [
            (1, 1, 2, 0, [
                (1, 150, 5),
                (2, 151, 5)
            ], 75.5)
        ]
        content = create_igsm_streams_file(1, 5, reaches_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.igsm_read_streams import igsm_read_streams

            reach_list, stnodes_dict, n_snodes = igsm_read_streams(temp_file)

            # Verify dict structure: key=stream_node, value=[GW_node, subregion, reach, bottom_elev]
            for stream_node in [1, 2]:
                assert len(stnodes_dict[stream_node]) == 4

            # Verify specific values (bottom_elev is float)
            assert stnodes_dict[1] == [150, 5, 1, 75.0]
            assert stnodes_dict[2] == [151, 5, 1, 75.0]

        finally:
            os.unlink(temp_file)

    def test_reach_list_structure(self):
        """Test that reach_list has correct structure"""
        # Stream nodes must be sequential starting from 1
        reaches_data = [
            (5, 1, 6, 0, [
                (1, 100, 1),
                (2, 101, 1),
                (3, 102, 1),
                (4, 103, 1),
                (5, 104, 1),
                (6, 105, 1)
            ], 50.0)
        ]
        content = create_igsm_streams_file(1, 5, reaches_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.igsm_read_streams import igsm_read_streams

            reach_list, stnodes_dict, n_snodes = igsm_read_streams(temp_file)

            # Verify reach list structure: [reach, upper, lower, oflow]
            assert len(reach_list) == 1
            assert len(reach_list[0]) == 4
            assert reach_list[0] == [5, 1, 6, 0]

        finally:
            os.unlink(temp_file)

    def test_real_file_format(self):
        """Test with format matching real IGSM file"""
        # Simulating real file with reach 4 from SCFSTRM.DAT
        # Stream nodes must be sequential (1-28)
        reaches_data = [
            (4, 1, 28, 0, [
                (1, 1750, 1),
                (2, 1780, 1),
                (3, 1808, 1),
                (4, 1809, 1),
                (5, 1810, 1),
                (6, 1811, 1),
                (7, 1812, 1),
                (8, 1813, 1),
                (9, 1838, 1),
                (10, 1855, 2),
                (11, 1856, 2),
                (12, 1857, 2),
                (13, 1858, 2),
                (14, 1844, 2),
                (15, 1845, 2),
                (16, 1846, 2),
                (17, 1847, 3),
                (18, 1848, 3),
                (19, 1849, 4),
                (20, 1828, 4),
                (21, 1829, 4),
                (22, 1830, 4),
                (23, 1831, 4),
                (24, 1850, 4),
                (25, 1851, 4),
                (26, 1852, 4),
                (27, 1853, 4),
                (28, 1854, 4)
            ], 100.0)
        ]
        content = create_igsm_streams_file(1, 5, reaches_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.igsm_read_streams import igsm_read_streams

            reach_list, stnodes_dict, n_snodes = igsm_read_streams(temp_file)

            # Verify reach
            assert reach_list[0] == [4, 1, 28, 0]
            assert n_snodes == 28

            # Verify specific nodes
            assert stnodes_dict[1][0] == 1750
            assert stnodes_dict[1][1] == 1
            assert stnodes_dict[28][0] == 1854
            assert stnodes_dict[28][1] == 4

        finally:
            os.unlink(temp_file)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])


# -----------------------------------------------------------------------------
# Error-path tests
# -----------------------------------------------------------------------------

def test_igsm_read_streams_missing_file_exits(tmp_path):
    """Calling with a nonexistent path bails out via iwfm.file_test() → sys.exit()."""
    import pytest
    from iwfm.igsm_read_streams import igsm_read_streams

    bogus = str(tmp_path / "does_not_exist.dat")
    with pytest.raises(FileNotFoundError):
        igsm_read_streams(bogus)


def test_igsm_read_streams_empty_file_raises(tmp_path):
    """An empty stream file should fail the parser (not silently return empty)."""
    import pytest
    from iwfm.igsm_read_streams import igsm_read_streams

    empty = tmp_path / "empty.dat"
    empty.write_text("")
    with pytest.raises((IndexError, ValueError)):
        igsm_read_streams(str(empty))
