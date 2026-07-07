# test_igsm_read_nodes.py
# Tests for igsm_read_nodes function
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

"""
Tests for iwfm.igsm_read_nodes function.

The igsm_read_nodes function reads the nodal coordinates from an IGSM
preprocessor node file. It is a wrapper around iwfm_read_nodes.

Example files used for testing:
- Node file: iwfm/tests/C2VSimCG-2021/Preprocessor/C2VSimCG_Nodes.dat

C2VSimCG model characteristics:
- 1,393 nodes
- Factor: 3.2808 (feet to meters conversion)

Returns:
- node_coord: list of [node_id, x, y] for each node
- node_list: list of node IDs
- factor: conversion factor from file
"""

import pytest
import os
import sys
import inspect
import tempfile

# Add the iwfm directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from iwfm.igsm_read_nodes import igsm_read_nodes

# Path to example files
EXAMPLE_NODE_FILE = os.path.join(
    os.path.dirname(__file__),
    'C2VSimCG-2021', 'Preprocessor', 'C2VSimCG_Nodes.dat'
)

# Check if example files exist
EXAMPLE_FILES_EXIST = os.path.exists(EXAMPLE_NODE_FILE)


def create_nodes_file(nnodes, fact, nodes_data):
    """Create IGSM/IWFM Nodes file for testing.

    Parameters
    ----------
    nnodes : int
        Number of nodes
    fact : float
        Conversion factor for nodal coordinates
    nodes_data : list of tuples
        Each tuple: (node_id, x, y)

    Returns
    -------
    str
        File contents
    """
    content = "C IGSM Nodes File\n"
    content += "C\n"
    content += f"    {nnodes}                          /ND\n"
    content += f"    {fact}                        /FACT\n"
    content += "C\n"
    content += "C   Node     ----------Coordinates----------\n"
    content += "C    ID            X                 Y\n"
    content += "C\n"

    # Add node data
    for node_id, x, y in nodes_data:
        content += f"      {node_id}        {x}         {y}\n"

    return content


class TestIgsmReadNodesFunctionExists:
    """Test that igsm_read_nodes function exists and has correct signature."""

    def test_function_exists(self):
        """Test that igsm_read_nodes function is importable."""
        assert igsm_read_nodes is not None

    def test_function_is_callable(self):
        """Test that igsm_read_nodes is callable."""
        assert callable(igsm_read_nodes)

    def test_function_has_docstring(self):
        """Test that igsm_read_nodes has a docstring."""
        assert igsm_read_nodes.__doc__ is not None
        assert len(igsm_read_nodes.__doc__) > 0

    def test_function_signature(self):
        """Test that igsm_read_nodes has the expected parameters."""
        sig = inspect.signature(igsm_read_nodes)
        params = list(sig.parameters.keys())

        assert 'node_file' in params


class TestIgsmReadNodesReturnValue:
    """Test the return value structure of igsm_read_nodes."""

    def test_returns_three_values(self):
        """Test that igsm_read_nodes returns three values."""
        nodes_data = [(1, 100.0, 200.0)]
        content = create_nodes_file(1, 1.0, nodes_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            result = igsm_read_nodes(temp_file)
            assert len(result) == 3
        finally:
            os.unlink(temp_file)

    def test_returns_node_coord_list(self):
        """Test that first return value is a list of node coordinates."""
        nodes_data = [(1, 100.0, 200.0), (2, 110.0, 210.0)]
        content = create_nodes_file(2, 1.0, nodes_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            node_coord, node_list, factor = igsm_read_nodes(temp_file)
            assert isinstance(node_coord, list)
            assert len(node_coord) == 2
            # Each entry should have node_id, x, y
            assert len(node_coord[0]) >= 3
        finally:
            os.unlink(temp_file)

    def test_returns_node_list(self):
        """Test that second return value is a list of node IDs."""
        nodes_data = [(1, 100.0, 200.0), (2, 110.0, 210.0)]
        content = create_nodes_file(2, 1.0, nodes_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            node_coord, node_list, factor = igsm_read_nodes(temp_file)
            assert isinstance(node_list, list)
            assert node_list == [1, 2]
        finally:
            os.unlink(temp_file)

    def test_returns_factor(self):
        """Test that third return value is the factor."""
        nodes_data = [(1, 100.0, 200.0)]
        content = create_nodes_file(1, 3.2808, nodes_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            node_coord, node_list, factor = igsm_read_nodes(temp_file)
            assert factor == 3.2808
        finally:
            os.unlink(temp_file)


class TestIgsmReadNodesSingleNode:
    """Test igsm_read_nodes with single node."""

    def test_single_node(self):
        """Test reading single node."""
        nodes_data = [(1, 551396.4, 4496226.0)]
        content = create_nodes_file(1, 3.2808, nodes_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            node_coord, node_list, factor = igsm_read_nodes(temp_file)

            # Verify node list
            assert len(node_list) == 1
            assert node_list[0] == 1

            # Verify node coordinates
            assert len(node_coord) == 1
            assert node_coord[0][0] == 1
            assert node_coord[0][1] == pytest.approx(551396.4, abs=0.1)
            assert node_coord[0][2] == pytest.approx(4496226.0, abs=0.1)

            # Verify factor
            assert factor == 3.2808
        finally:
            os.unlink(temp_file)


class TestIgsmReadNodesMultipleNodes:
    """Test igsm_read_nodes with multiple nodes."""

    def test_multiple_nodes(self):
        """Test reading multiple nodes."""
        nodes_data = [
            (1, 551396.4, 4496226.0),
            (2, 555618.8, 4497861.0),
            (3, 561555.5, 4500441.0),
            (4, 568374.3, 4498058.0),
            (5, 553186.9, 4492706.0)
        ]
        content = create_nodes_file(5, 3.2808, nodes_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            node_coord, node_list, factor = igsm_read_nodes(temp_file)

            # Verify node count
            assert len(node_list) == 5
            assert len(node_coord) == 5

            # Verify node IDs
            assert node_list == [1, 2, 3, 4, 5]

            # Verify first node
            assert node_coord[0][0] == 1
            assert node_coord[0][1] == pytest.approx(551396.4, abs=0.1)

            # Verify last node
            assert node_coord[4][0] == 5
            assert node_coord[4][1] == pytest.approx(553186.9, abs=0.1)
        finally:
            os.unlink(temp_file)

    def test_non_sequential_node_ids(self):
        """Test reading nodes with non-sequential IDs."""
        nodes_data = [
            (5, 100.0, 200.0),
            (10, 110.0, 210.0),
            (15, 120.0, 220.0),
            (20, 130.0, 230.0)
        ]
        content = create_nodes_file(4, 1.0, nodes_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            node_coord, node_list, factor = igsm_read_nodes(temp_file)

            # Verify non-sequential IDs are preserved
            assert node_list == [5, 10, 15, 20]
            assert node_coord[0][0] == 5
            assert node_coord[1][0] == 10
            assert node_coord[2][0] == 15
            assert node_coord[3][0] == 20
        finally:
            os.unlink(temp_file)


class TestIgsmReadNodesCoordinates:
    """Test coordinate handling in igsm_read_nodes."""

    def test_large_coordinates(self):
        """Test reading nodes with large coordinate values."""
        nodes_data = [
            (1, 551396.4, 4496226.0),
            (2, 555618.8, 4497861.0),
            (3, 561555.5, 4500441.0)
        ]
        content = create_nodes_file(3, 3.2808, nodes_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            node_coord, node_list, factor = igsm_read_nodes(temp_file)

            # Verify large coordinates are read correctly
            assert node_coord[0][1] == pytest.approx(551396.4, abs=0.1)
            assert node_coord[0][2] == pytest.approx(4496226.0, abs=0.1)
            assert node_coord[2][1] == pytest.approx(561555.5, abs=0.1)
            assert node_coord[2][2] == pytest.approx(4500441.0, abs=0.1)
        finally:
            os.unlink(temp_file)

    def test_negative_coordinates(self):
        """Test reading nodes with negative coordinates."""
        nodes_data = [
            (1, -100.5, -200.5),
            (2, 100.5, -200.5),
            (3, -100.5, 200.5),
            (4, 100.5, 200.5)
        ]
        content = create_nodes_file(4, 1.0, nodes_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            node_coord, node_list, factor = igsm_read_nodes(temp_file)

            # Verify negative coordinates
            assert node_coord[0][1] == pytest.approx(-100.5, abs=0.1)
            assert node_coord[0][2] == pytest.approx(-200.5, abs=0.1)
            assert node_coord[1][1] == pytest.approx(100.5, abs=0.1)
            assert node_coord[1][2] == pytest.approx(-200.5, abs=0.1)
        finally:
            os.unlink(temp_file)

    def test_integer_coordinates(self):
        """Test reading nodes with integer coordinates."""
        nodes_data = [
            (1, 100, 200),
            (2, 150, 250),
            (3, 200, 300)
        ]
        content = create_nodes_file(3, 1.0, nodes_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            node_coord, node_list, factor = igsm_read_nodes(temp_file)

            # Verify integer coordinates are read as floats
            assert isinstance(node_coord[0][1], float)
            assert isinstance(node_coord[0][2], float)
            assert node_coord[0][1] == 100.0
            assert node_coord[0][2] == 200.0
        finally:
            os.unlink(temp_file)


class TestIgsmReadNodesFactor:
    """Test factor handling in igsm_read_nodes."""

    def test_factor_from_file(self):
        """Test reading factor from file."""
        nodes_data = [(1, 100.0, 200.0)]
        content = create_nodes_file(1, 3.2808, nodes_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            node_coord, node_list, factor = igsm_read_nodes(temp_file)
            assert factor == 3.2808
        finally:
            os.unlink(temp_file)

    def test_unit_factor(self):
        """Test with unit factor (1.0)."""
        nodes_data = [(1, 100.0, 200.0)]
        content = create_nodes_file(1, 1.0, nodes_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            node_coord, node_list, factor = igsm_read_nodes(temp_file)
            assert factor == 1.0
        finally:
            os.unlink(temp_file)


class TestIgsmReadNodesCommentHandling:
    """Test comment handling in igsm_read_nodes."""

    def test_comment_lines_skipped(self):
        """Test that comment lines are properly skipped."""
        content = "C IGSM Nodes File\n"
        content += "c This is a comment\n"
        content += "* Another comment\n"
        content += "# Hash comment\n"
        content += "    3                          /ND\n"
        content += "C More comments\n"
        content += "    1.0                        /FACT\n"
        content += "C\n"
        content += "      1        100.0         200.0\n"
        content += "      2        110.0         210.0\n"
        content += "      3        120.0         220.0\n"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            node_coord, node_list, factor = igsm_read_nodes(temp_file)

            # Should read correctly despite comment lines
            assert len(node_list) == 3
            assert node_list == [1, 2, 3]
        finally:
            os.unlink(temp_file)


class TestIgsmReadNodesErrorHandling:
    """Test error handling in igsm_read_nodes."""

    def test_nonexistent_file_raises_error(self):
        """Test that nonexistent file raises an error."""
        with pytest.raises(FileNotFoundError):
            igsm_read_nodes('/nonexistent/file.dat')


class TestIgsmReadNodesLargeDataset:
    """Test igsm_read_nodes with larger datasets."""

    def test_hundred_nodes(self):
        """Test reading 100 nodes."""
        nodes_data = [(i + 1, 100.0 + i, 200.0 + i) for i in range(100)]
        content = create_nodes_file(100, 1.0, nodes_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            node_coord, node_list, factor = igsm_read_nodes(temp_file)

            # Verify all nodes read
            assert len(node_list) == 100
            assert len(node_coord) == 100

            # Spot check first, middle, and last
            assert node_list[0] == 1
            assert node_list[50] == 51
            assert node_list[99] == 100

            assert node_coord[0][1] == 100.0
            assert node_coord[50][1] == 150.0
            assert node_coord[99][1] == 199.0
        finally:
            os.unlink(temp_file)


@pytest.mark.skipif(not EXAMPLE_FILES_EXIST,
                    reason="Example node file not available")
class TestIgsmReadNodesC2VSimCG:
    """Test igsm_read_nodes with real C2VSimCG node file."""

    def test_reads_c2vsimcg_node_file(self):
        """Test reading the C2VSimCG node file."""
        node_coord, node_list, factor = igsm_read_nodes(EXAMPLE_NODE_FILE)

        # C2VSimCG has 1393 nodes
        assert len(node_list) == 1393
        assert len(node_coord) == 1393

    def test_c2vsimcg_node_ids_sequential(self):
        """Test that C2VSimCG node IDs are sequential from 1."""
        node_coord, node_list, factor = igsm_read_nodes(EXAMPLE_NODE_FILE)

        assert node_list[0] == 1
        assert node_list[-1] == 1393

    def test_c2vsimcg_factor(self):
        """Test that C2VSimCG factor is 3.2808 (feet to meters)."""
        node_coord, node_list, factor = igsm_read_nodes(EXAMPLE_NODE_FILE)

        assert factor == pytest.approx(3.2808, abs=0.0001)

    def test_c2vsimcg_coordinates_reasonable(self):
        """Test that C2VSimCG coordinates are in reasonable range."""
        node_coord, node_list, factor = igsm_read_nodes(EXAMPLE_NODE_FILE)

        # Check coordinates are in reasonable range for California
        for i in range(len(node_coord)):
            x = node_coord[i][1]
            y = node_coord[i][2]
            # X should be positive (UTM easting)
            assert x > 0
            # Y should be positive (UTM northing)
            assert y > 0
            # Reasonable UTM range for California
            assert 100000 < x < 900000
            assert 3500000 < y < 4600000

    def test_c2vsimcg_node_coord_structure(self):
        """Test that C2VSimCG node_coord has correct structure."""
        node_coord, node_list, factor = igsm_read_nodes(EXAMPLE_NODE_FILE)

        # Each node_coord entry should be [node_id, x, y]
        for i in range(min(10, len(node_coord))):
            assert len(node_coord[i]) >= 3
            assert isinstance(node_coord[i][0], int)  # node_id
            assert isinstance(node_coord[i][1], float)  # x
            assert isinstance(node_coord[i][2], float)  # y

    def test_c2vsimcg_first_node(self):
        """Test first node of C2VSimCG."""
        node_coord, node_list, factor = igsm_read_nodes(EXAMPLE_NODE_FILE)

        # First node should be node 1
        assert node_coord[0][0] == 1
        # Coordinates should be reasonable
        assert node_coord[0][1] > 500000
        assert node_coord[0][2] > 4000000

    def test_c2vsimcg_last_node(self):
        """Test last node of C2VSimCG."""
        node_coord, node_list, factor = igsm_read_nodes(EXAMPLE_NODE_FILE)

        # Last node should be node 1393
        assert node_coord[-1][0] == 1393
        # Coordinates should be reasonable (UTM range for California)
        assert node_coord[-1][1] > 500000
        assert node_coord[-1][2] > 3500000  # Southern California can be below 4M
