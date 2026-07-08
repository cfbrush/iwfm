#!/usr/bin/env python
# test_sub_pp_streams.py
# Unit tests for sub_pp_streams.py
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
from pathlib import Path

import iwfm


def create_stream_spec_file_42_content(nreach, nrate, reaches_data, rating_factors=None, stream_aq_lines=None):
    """Create properly structured IWFM stream specification file content (v4.2) for testing.

    This function creates a mock stream specification file following the IWFM v4.2 format.
    Comment lines have 'C', 'c', '*' or '#' in first text column.
    Data lines begin with whitespace. Uses '/' = end of record marker.

    Parameters
    ----------
    nreach : int
        Number of stream reaches
    nrate : int
        Number of points in rating table for each stream node
    reaches_data : list of tuples
        Each tuple: (reach_id, nnodes, outflow_dest, name, nodes_data)
        nodes_data: list of tuples (snode_id, gwnode_id)
    rating_factors : list of str, optional
        Rating table factor lines (FACTLT, FACTQ, TUNIT)
    stream_aq_lines : list of str, optional
        Stream-aquifer interaction section lines

    Returns
    -------
    str
        File content as string with Windows line endings
    """
    lines = []

    # Header with version (first line after '#' is the version)
    lines.append("#4.2")
    lines.append("C Stream Specification File - Version 4.2")

    # NREACH section
    lines.append("C Number of stream reaches")
    lines.append(f"     {nreach}                        / NRH")

    # NRATE section
    lines.append("C Number of rating table points")
    lines.append(f"     {nrate}                         / NRTB")

    # Reach section
    lines.append("C Stream reach definitions")
    for reach_id, nnodes, outflow, name, nodes_data in reaches_data:
        # Reach header: ID, NRD, IDWN, NAME
        lines.append(f"     {reach_id}        {nnodes}         {outflow}     {name}")
        # Stream nodes in reach: IRV, IGW
        for snode_id, gwnode_id in nodes_data:
            lines.append(f"     {snode_id}       {gwnode_id}")

    # Rating table factors section (with comments and data)
    lines.append("C Rating table factors")
    if rating_factors:
        lines.extend(rating_factors)
    else:
        lines.append("     1.0                         / FACTLT")
        lines.append("     60.0                        / FACTQ")
        lines.append("     1min                        / TUNIT")

    lines.append("C Rating tables for each stream node")

    # Rating tables - one table per stream node
    # Collect all stream node IDs in order
    snode_list = []
    for _, _, _, _, nodes_data in reaches_data:
        for snode_id, _ in nodes_data:
            snode_list.append(snode_id)

    # Create rating table for each stream node
    # Format: first line has snode_id, bottom_elev, stage, flow
    # Subsequent lines have stage, flow only (with leading whitespace)
    for idx, snode_id in enumerate(snode_list):
        bottom_elev = 300.0 + idx * 10.0
        for i in range(nrate):
            stage = 0.0 + i * 1.5
            flow = 0.0 + i * 100.0
            if i == 0:
                # First line includes snode_id and bottom elevation
                lines.append(f"	{snode_id}	{bottom_elev:.2f}	{stage:.3f}		{flow:.2f}")
            else:
                # Continuation lines
                lines.append(f"			{stage:.3f}		{flow:.2f}")

    # Stream-aquifer interaction section (optional)
    if stream_aq_lines:
        lines.extend(stream_aq_lines)
    else:
        lines.append("C Stream-aquifer interaction section")
        lines.append("     1.0    / FACTKH")

    # Join with Windows line endings
    return "\r\n".join(lines)


# ============================================================================
# Tests for sub_pp_streams with file format version 4.2
# ============================================================================

class TestSubPPStreamsBasic:
    """Basic tests for sub_pp_streams function."""

    def test_single_reach_all_nodes_in_submodel(self, tmp_path):
        """Test with single reach where all nodes are in the submodel."""
        # Create test data: 1 reach with 3 stream nodes
        reaches_data = [
            (1, 3, 0, "Test_Reach", [(1, 100), (2, 101), (3, 102)])
        ]

        content = create_stream_spec_file_42_content(
            nreach=1,
            nrate=3,
            reaches_data=reaches_data
        )

        # Write to temp file
        stream_file = tmp_path / "test_streams.dat"
        stream_file.write_text(content)

        # Node list includes all groundwater nodes from the reach
        node_list = [100, 101, 102]

        result = iwfm.sub_pp_streams(str(stream_file), node_list)

        sub_reach_info, snode_dict, sub_rattab_dict, rating_header, stream_aq, sub_snodes = result

        # All 3 stream nodes should be in submodel
        assert len(sub_snodes) == 3
        assert 1 in sub_snodes
        assert 2 in sub_snodes
        assert 3 in sub_snodes

        # Verify snode_dict maps stream nodes to gw nodes
        assert snode_dict[1] == 100
        assert snode_dict[2] == 101
        assert snode_dict[3] == 102

        # Verify reach info is included
        assert len(sub_reach_info) == 1
        assert sub_reach_info[0][0] == 1  # reach_id

        # Verify rating tables are included for all nodes
        assert len(sub_rattab_dict) == 3

    def test_single_reach_partial_nodes_in_submodel(self, tmp_path):
        """Test with single reach where only some nodes are in the submodel."""
        # Create test data: 1 reach with 5 stream nodes
        reaches_data = [
            (1, 5, 0, "Test_Reach", [(1, 100), (2, 101), (3, 102), (4, 103), (5, 104)])
        ]

        content = create_stream_spec_file_42_content(
            nreach=1,
            nrate=3,
            reaches_data=reaches_data
        )

        stream_file = tmp_path / "test_streams.dat"
        stream_file.write_text(content)

        # Node list only includes 2 of the 5 groundwater nodes
        node_list = [101, 103]

        result = iwfm.sub_pp_streams(str(stream_file), node_list)

        sub_reach_info, snode_dict, sub_rattab_dict, rating_header, stream_aq, sub_snodes = result

        # Only 2 stream nodes should be in submodel
        assert len(sub_snodes) == 2
        assert 2 in sub_snodes  # maps to gw node 101
        assert 4 in sub_snodes  # maps to gw node 103
        assert 1 not in sub_snodes
        assert 3 not in sub_snodes
        assert 5 not in sub_snodes

        # Verify rating tables only for included nodes
        assert len(sub_rattab_dict) == 2
        assert 2 in sub_rattab_dict
        assert 4 in sub_rattab_dict

    def test_single_reach_no_nodes_in_submodel(self, tmp_path):
        """Test with single reach where no nodes are in the submodel."""
        reaches_data = [
            (1, 3, 0, "Test_Reach", [(1, 100), (2, 101), (3, 102)])
        ]

        content = create_stream_spec_file_42_content(
            nreach=1,
            nrate=3,
            reaches_data=reaches_data
        )

        stream_file = tmp_path / "test_streams.dat"
        stream_file.write_text(content)

        # Node list does not include any groundwater nodes from the reach
        node_list = [200, 201, 202]

        result = iwfm.sub_pp_streams(str(stream_file), node_list)

        sub_reach_info, snode_dict, sub_rattab_dict, rating_header, stream_aq, sub_snodes = result

        # No stream nodes should be in submodel
        assert len(sub_snodes) == 0
        assert len(sub_reach_info) == 0
        assert len(sub_rattab_dict) == 0


class TestSubPPStreamsMultipleReaches:
    """Tests for sub_pp_streams with multiple reaches."""

    def test_multiple_reaches_all_included(self, tmp_path):
        """Test with multiple reaches where all are in the submodel."""
        reaches_data = [
            (1, 2, 4, "Reach_1", [(1, 100), (2, 101)]),
            (2, 2, 0, "Reach_2", [(3, 102), (4, 103)])
        ]

        content = create_stream_spec_file_42_content(
            nreach=2,
            nrate=3,
            reaches_data=reaches_data
        )

        stream_file = tmp_path / "test_streams.dat"
        stream_file.write_text(content)

        # Include all groundwater nodes
        node_list = [100, 101, 102, 103]

        result = iwfm.sub_pp_streams(str(stream_file), node_list)

        sub_reach_info, snode_dict, sub_rattab_dict, rating_header, stream_aq, sub_snodes = result

        # All 4 stream nodes should be included
        assert len(sub_snodes) == 4

        # Both reaches should be in submodel
        assert len(sub_reach_info) == 2

        # Verify rating tables for all nodes
        assert len(sub_rattab_dict) == 4

    def test_multiple_reaches_some_excluded(self, tmp_path):
        """Test with multiple reaches where only some are in the submodel."""
        reaches_data = [
            (1, 2, 4, "Reach_1", [(1, 100), (2, 101)]),
            (2, 2, 6, "Reach_2", [(3, 200), (4, 201)]),  # Different gw nodes
            (3, 2, 0, "Reach_3", [(5, 102), (6, 103)])
        ]

        content = create_stream_spec_file_42_content(
            nreach=3,
            nrate=3,
            reaches_data=reaches_data
        )

        stream_file = tmp_path / "test_streams.dat"
        stream_file.write_text(content)

        # Include only gw nodes from reaches 1 and 3
        node_list = [100, 101, 102, 103]

        result = iwfm.sub_pp_streams(str(stream_file), node_list)

        sub_reach_info, snode_dict, sub_rattab_dict, rating_header, stream_aq, sub_snodes = result

        # Only 4 stream nodes from reaches 1 and 3 should be included
        assert len(sub_snodes) == 4
        assert 1 in sub_snodes
        assert 2 in sub_snodes
        assert 5 in sub_snodes
        assert 6 in sub_snodes
        assert 3 not in sub_snodes  # From excluded reach 2
        assert 4 not in sub_snodes  # From excluded reach 2

        # Only 2 reaches should be in submodel (reaches 1 and 3)
        assert len(sub_reach_info) == 2
        reach_ids = [r[0] for r in sub_reach_info]
        assert 1 in reach_ids
        assert 3 in reach_ids
        assert 2 not in reach_ids

    def test_multiple_reaches_partial_nodes_in_reach(self, tmp_path):
        """Test with multiple reaches where a reach is partially included."""
        reaches_data = [
            (1, 4, 0, "Long_Reach", [(1, 100), (2, 101), (3, 200), (4, 201)])
        ]

        content = create_stream_spec_file_42_content(
            nreach=1,
            nrate=3,
            reaches_data=reaches_data
        )

        stream_file = tmp_path / "test_streams.dat"
        stream_file.write_text(content)

        # Include only first 2 gw nodes
        node_list = [100, 101]

        result = iwfm.sub_pp_streams(str(stream_file), node_list)

        sub_reach_info, snode_dict, sub_rattab_dict, rating_header, stream_aq, sub_snodes = result

        # Only 2 stream nodes should be included
        assert len(sub_snodes) == 2

        # Reach should be included with partial nodes
        assert len(sub_reach_info) == 1
        assert len(sub_reach_info[0][4]) == 2  # Only 2 stream nodes in reach


class TestSubPPStreamsReturnValues:
    """Tests for verifying return value structure of sub_pp_streams."""

    def test_return_values_structure(self, tmp_path):
        """Test that return values have correct structure."""
        reaches_data = [
            (1, 2, 0, "Test_Reach", [(1, 100), (2, 101)])
        ]

        content = create_stream_spec_file_42_content(
            nreach=1,
            nrate=4,
            reaches_data=reaches_data
        )

        stream_file = tmp_path / "test_streams.dat"
        stream_file.write_text(content)

        node_list = [100, 101]

        result = iwfm.sub_pp_streams(str(stream_file), node_list)

        # Should return 6 values
        assert len(result) == 6

        sub_reach_info, snode_dict, sub_rattab_dict, rating_header, stream_aq, sub_snodes = result

        # Verify types
        assert isinstance(sub_reach_info, list)
        assert isinstance(snode_dict, dict)
        assert isinstance(sub_rattab_dict, dict)
        assert isinstance(rating_header, list)
        assert isinstance(stream_aq, list)
        assert isinstance(sub_snodes, list)

    def test_reach_info_structure(self, tmp_path):
        """Test that reach_info entries have correct structure."""
        reaches_data = [
            (5, 3, 99, "Named_Reach", [(10, 500), (11, 501), (12, 502)])
        ]

        content = create_stream_spec_file_42_content(
            nreach=1,
            nrate=3,
            reaches_data=reaches_data
        )

        stream_file = tmp_path / "test_streams.dat"
        stream_file.write_text(content)

        node_list = [500, 501, 502]

        result = iwfm.sub_pp_streams(str(stream_file), node_list)

        sub_reach_info = result[0]

        # Verify reach info structure
        assert len(sub_reach_info) == 1
        reach = sub_reach_info[0]

        # Structure: [reach_id, nnodes, outflow, name, snodes]
        assert len(reach) >= 5
        assert reach[0] == 5  # reach_id
        # nnodes in submodel should be 3
        assert len(reach[4]) == 3  # snodes list

    def test_rating_table_structure(self, tmp_path):
        """Test that rating tables have correct number of entries."""
        nrate = 5
        reaches_data = [
            (1, 2, 0, "Test", [(1, 100), (2, 101)])
        ]

        content = create_stream_spec_file_42_content(
            nreach=1,
            nrate=nrate,
            reaches_data=reaches_data
        )

        stream_file = tmp_path / "test_streams.dat"
        stream_file.write_text(content)

        node_list = [100, 101]

        result = iwfm.sub_pp_streams(str(stream_file), node_list)

        sub_rattab_dict = result[2]

        # Each rating table should have nrate entries
        for snode, rattab in sub_rattab_dict.items():
            assert len(rattab) == nrate

    def test_rating_header_captured(self, tmp_path):
        """Test that rating header is captured correctly."""
        rating_factors = [
            "     2.5                         / FACTLT",
            "     30.0                        / FACTQ",
            "     1DAY                        / TUNIT"
        ]

        reaches_data = [
            (1, 1, 0, "Test", [(1, 100)])
        ]

        content = create_stream_spec_file_42_content(
            nreach=1,
            nrate=3,
            reaches_data=reaches_data,
            rating_factors=rating_factors
        )

        stream_file = tmp_path / "test_streams.dat"
        stream_file.write_text(content)

        node_list = [100]

        result = iwfm.sub_pp_streams(str(stream_file), node_list)

        rating_header = result[3]

        # Should capture rating table factor lines
        assert len(rating_header) > 0


class TestSubPPStreamsEdgeCases:
    """Edge case tests for sub_pp_streams."""

    def test_empty_node_list(self, tmp_path):
        """Test with empty node list."""
        reaches_data = [
            (1, 2, 0, "Test", [(1, 100), (2, 101)])
        ]

        content = create_stream_spec_file_42_content(
            nreach=1,
            nrate=3,
            reaches_data=reaches_data
        )

        stream_file = tmp_path / "test_streams.dat"
        stream_file.write_text(content)

        node_list = []

        result = iwfm.sub_pp_streams(str(stream_file), node_list)

        sub_reach_info, snode_dict, sub_rattab_dict, rating_header, stream_aq, sub_snodes = result

        # No nodes in submodel
        assert len(sub_snodes) == 0
        assert len(sub_reach_info) == 0
        assert len(sub_rattab_dict) == 0

    def test_node_list_as_strings(self, tmp_path):
        """Test that node_list items are converted to integers."""
        reaches_data = [
            (1, 2, 0, "Test", [(1, 100), (2, 101)])
        ]

        content = create_stream_spec_file_42_content(
            nreach=1,
            nrate=3,
            reaches_data=reaches_data
        )

        stream_file = tmp_path / "test_streams.dat"
        stream_file.write_text(content)

        # Pass node list as strings
        node_list = ['100', '101']

        result = iwfm.sub_pp_streams(str(stream_file), node_list)

        sub_snodes = result[5]

        # Should still work correctly
        assert len(sub_snodes) == 2

    def test_negative_outflow_to_lake(self, tmp_path):
        """Test reach with negative outflow (flows to lake)."""
        reaches_data = [
            (1, 2, -5, "Lake_Reach", [(1, 100), (2, 101)])  # -5 = flows to lake 5
        ]

        content = create_stream_spec_file_42_content(
            nreach=1,
            nrate=3,
            reaches_data=reaches_data
        )

        stream_file = tmp_path / "test_streams.dat"
        stream_file.write_text(content)

        node_list = [100, 101]

        result = iwfm.sub_pp_streams(str(stream_file), node_list)

        sub_reach_info = result[0]

        # Verify outflow value preserved
        assert sub_reach_info[0][2] == -5


class TestSubPPStreamsFileNotFound:
    """Tests for file not found error handling."""

    def test_file_not_found(self, tmp_path):
        """Test that FileNotFoundError is raised for missing file."""
        nonexistent_file = str(tmp_path / "nonexistent_streams.dat")
        node_list = [100, 101]

        # The iwfm.file_test() function calls sys.exit() when file is not found
        with pytest.raises(FileNotFoundError):
            iwfm.sub_pp_streams(nonexistent_file, node_list)


def _stream_spec_4x(version, wptb=False):
    """Minimal 2-reach stream spec file for v4.0/4.1/4.2 tests."""
    wp = "\t1.0" if wptb else ""
    return (
        f"#{version}\n"
        "C Stream file test\n"
        "     2                          / NRH\n"
        "     2                          / NRTB\n"
        "C-------------------------------------------------------------------------------\n"
        "\t1\t2\t3\tUpper Creek\n"
        "\t1\t100\n"
        "\t2\t101\n"
        "\t2\t2\t0\tLower Creek\n"
        "\t3\t102\n"
        "\t4\t103\n"
        "C rating tables\n"
        "     1.0                         / FACTLT\n"
        "     60.0                        / FACTQ\n"
        "     1min                        / TUNIT\n"
        "C-------------------------------------------------------------------------------\n"
        f"\t1\t100.0\t0.0\t0.0{wp}\n"
        f"\t\t2.0\t50.0{wp}\n"
        f"\t2\t95.0\t0.0\t0.0{wp}\n"
        f"\t\t2.0\t60.0{wp}\n"
        f"\t3\t90.0\t0.0\t0.0{wp}\n"
        f"\t\t2.0\t70.0{wp}\n"
        f"\t4\t85.0\t0.0\t0.0{wp}\n"
        f"\t\t2.0\t80.0{wp}\n"
        "     0                           / NSTRPINT\n"
    )


class TestSubPPStreamsVersions:
    """Tests for the supported stream file versions."""

    def test_version_40(self, tmp_path):
        """Test that version 4.0 files are read."""
        stream_file = tmp_path / "test_streams_40.dat"
        stream_file.write_text(_stream_spec_4x('4.0'))

        result = iwfm.sub_pp_streams(str(stream_file), [100, 101, 102, 103])
        sub_reach_info, snode_dict, sub_rattab_dict, *_ = result

        assert len(sub_reach_info) == 2
        assert snode_dict == {1: 100, 2: 101, 3: 102, 4: 103}
        assert len(sub_rattab_dict) == 4

    def test_version_41(self, tmp_path):
        """Test that version 4.1 files (with WPTB column) are read."""
        stream_file = tmp_path / "test_streams_41.dat"
        stream_file.write_text(_stream_spec_4x('4.1', wptb=True))

        result = iwfm.sub_pp_streams(str(stream_file), [100, 101])
        sub_reach_info, snode_dict, sub_rattab_dict, *_ = result

        assert len(sub_reach_info) == 1               # only reach 1 in submodel
        assert len(sub_rattab_dict) == 2              # rating tables for nodes 1, 2
        # WPTB column carried through verbatim
        assert sub_rattab_dict[1][0].split()[-1] == '1.0'

    def test_version_50(self, tmp_path):
        """Test that version 5.0 files (no rating tables) are read."""
        content = (
            "#5.0\n"
            "C Stream file v5.0\n"
            "     2                          / NRH\n"
            "C-------------------------------------------------------------------------------\n"
            "\t1\t2\t3\tUpper Creek\n"
            "\t1\t100\n"
            "\t2\t101\n"
            "\t2\t2\t0\tLower Creek\n"
            "\t3\t102\n"
            "\t4\t103\n"
            "     0                           / NSTRPINT\n"
        )
        stream_file = tmp_path / "test_streams_50.dat"
        stream_file.write_text(content)

        result = iwfm.sub_pp_streams(str(stream_file), [100, 101, 102, 103])
        sub_reach_info, snode_dict, sub_rattab_dict, rating_header, stream_aq, sub_snodes = result

        assert len(sub_reach_info) == 2
        assert sub_rattab_dict == {}
        assert rating_header == []
        assert len(sub_snodes) == 4

    def test_unknown_version_raises(self, tmp_path):
        """Test that an unknown version raises NotImplementedError."""
        content = "#3.0\nC Stream file v3.0\n     1    / NRH\n     3    / NRTB\n"
        stream_file = tmp_path / "test_streams_30.dat"
        stream_file.write_text(content)

        with pytest.raises(NotImplementedError):
            iwfm.sub_pp_streams(str(stream_file), [100])


# ============================================================================
# Integration test with real-format data
# ============================================================================

class TestSubPPStreamsRealFormatData:
    """Tests using realistic IWFM stream file format."""

    def test_realistic_stream_file(self, tmp_path):
        """Test with realistic IWFM stream file structure."""
        # Create a more realistic stream file similar to C2VSimCG format
        lines = []
        lines.append("#4.2")
        lines.append("C *** DO NOT DELETE ABOVE LINE ***")
        lines.append("C")
        lines.append("C                  INTEGRATED WATER FLOW MODEL (IWFM)")
        lines.append("C")
        lines.append("C                       STREAM SPECIFICATION FILE")
        lines.append("C")
        lines.append("C   NRH;   Number of stream reaches modeled")
        lines.append("C   NRTB;  Number of data points in stream rating tables")
        lines.append("C-------------------------------------------------------------------------------")
        lines.append("     2                        / NRH")
        lines.append("     3                        / NRTB")
        lines.append("C-------------------------------------------------------------------------------")
        lines.append("C     REACH  1  -  TEST RIVER")
        lines.append("C   Reach  Number of   Outflow   Reach")
        lines.append("C            Nodes      Node      Name")
        lines.append("C   ID        NRD       IDWN      NAME")
        lines.append("C--------------------------------------------")
        lines.append("     1        3         4     Test River")
        lines.append("C--------------------------------------------")
        lines.append("C   Stream  Groundwater")
        lines.append("C   node      node")
        lines.append("C   IRV       IGW")
        lines.append("C--------------------------------------------")
        lines.append("     1       1304")
        lines.append("     2       1315")
        lines.append("     3       1317")
        lines.append("C================================================")
        lines.append("C     REACH 2 - TEST CREEK")
        lines.append("     2        2        0      Test Creek")
        lines.append("C--------------------------------------------")
        lines.append("    4        1292")
        lines.append("    5        1291")
        lines.append("C*******************************************************************************")
        lines.append("C                             Stream rating tables")
        lines.append("C")
        lines.append("C   FACTLT; Conversion factor for stream bottom elevation and stream depth")
        lines.append("C   FACTQ;  Conversion factor for rating table flow rates")
        lines.append("C-------------------------------------------------------------------------------")
        lines.append("     1.0                         / FACTLT")
        lines.append("     60.0                        / FACTQ")
        lines.append("     1min                        / TUNIT")
        lines.append("C-------------------------------------------------------------------------------")
        lines.append("C   Rating tables for each stream node")
        lines.append("C-------------------------------------------------------------")
        # Rating tables for 5 stream nodes
        for sn in [1, 2, 3, 4, 5]:
            lines.append(f"	{sn}	{300+sn*10:.2f}	0.000		0.00")
            lines.append("			1.500		100.00")
            lines.append("			3.000		200.00")

        content = "\r\n".join(lines)

        stream_file = tmp_path / "test_streams.dat"
        stream_file.write_text(content)

        # Include only nodes from reach 1
        node_list = [1304, 1315, 1317]

        result = iwfm.sub_pp_streams(str(stream_file), node_list)

        sub_reach_info, snode_dict, sub_rattab_dict, rating_header, stream_aq, sub_snodes = result

        # Verify only stream nodes 1, 2, 3 are included
        assert len(sub_snodes) == 3
        assert 1 in sub_snodes
        assert 2 in sub_snodes
        assert 3 in sub_snodes
        assert 4 not in sub_snodes
        assert 5 not in sub_snodes

        # Only reach 1 should be included
        assert len(sub_reach_info) == 1
        assert sub_reach_info[0][0] == 1

        # Rating tables only for included nodes
        assert len(sub_rattab_dict) == 3


# ============================================================================
# Tests with actual test data file (if available)
# ============================================================================

TEST_DATA_DIR = Path(__file__).parent / "C2VSimCG-2021"
PP_STREAMS_FILE = TEST_DATA_DIR / "Preprocessor" / "C2VSimCG_Streams_CVOPS.dat"


@pytest.fixture
def pp_streams_file_exists():
    """Check that the C2VSimCG preprocessor streams file exists."""
    if not TEST_DATA_DIR.exists():
        pytest.skip(f"Test data directory not found: {TEST_DATA_DIR}")
    if not PP_STREAMS_FILE.exists():
        pytest.skip(f"Preprocessor streams file not found: {PP_STREAMS_FILE}")
    return True


class TestSubPPStreamsWithRealFile:
    """Tests using the actual C2VSimCG stream specification file."""

    def test_real_file_format_verification(self, pp_streams_file_exists):
        """Test that C2VSimCG preprocessor streams file has expected structure."""
        with open(PP_STREAMS_FILE, 'r') as f:
            lines = f.readlines()

        # Verify file starts with version marker
        assert lines[0].strip().startswith('#'), "First line should start with version marker"
        assert '4.2' in lines[0], "Should be version 4.2 file"

        # Verify file has NRH and NRTB markers
        has_nrh = any('/ NRH' in line for line in lines)
        has_nrtb = any('/ NRTB' in line for line in lines)

        assert has_nrh, "Should have NRH marker for number of reaches"
        assert has_nrtb, "Should have NRTB marker for number of rating table points"

    def test_real_file_with_subset_nodes(self, pp_streams_file_exists):
        """Test sub_pp_streams with a subset of nodes from real file."""
        # Use a small subset of known groundwater nodes from C2VSimCG
        # These are from reach 1 (Kern River): gw nodes 1304, 1315, 1317
        node_list = [1304, 1315, 1317]

        result = iwfm.sub_pp_streams(str(PP_STREAMS_FILE), node_list)

        sub_reach_info, snode_dict, sub_rattab_dict, rating_header, stream_aq, sub_snodes = result

        # Verify we got some results
        assert len(sub_snodes) > 0, "Should have some stream nodes in submodel"
        assert len(sub_reach_info) > 0, "Should have at least one reach"
        assert len(sub_rattab_dict) > 0, "Should have rating tables"
        assert len(rating_header) > 0, "Should have rating header"

        # Verify stream node dict maps to groundwater nodes
        for sn in sub_snodes:
            assert sn in snode_dict, f"Stream node {sn} should be in snode_dict"
            assert snode_dict[sn] in node_list, f"GW node should be in node_list"

    def test_real_file_empty_submodel(self, pp_streams_file_exists):
        """Test sub_pp_streams with nodes not in the model."""
        # Use groundwater node IDs that don't exist in C2VSimCG
        node_list = [99999, 99998, 99997]

        result = iwfm.sub_pp_streams(str(PP_STREAMS_FILE), node_list)

        sub_reach_info, snode_dict, sub_rattab_dict, rating_header, stream_aq, sub_snodes = result

        # Should return empty submodel data
        assert len(sub_snodes) == 0
        assert len(sub_reach_info) == 0
        assert len(sub_rattab_dict) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
