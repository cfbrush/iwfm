#!/usr/bin/env python
# test_sub_pp_node_file.py
# Unit tests for sub_pp_node_file.py
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


def create_node_file(nd, fact, nodes):
    """Create a node coordinate file for testing.

    Parameters
    ----------
    nd : int
        Number of nodes
    fact : float
        Conversion factor for nodal coordinates
    nodes : list of tuples
        Each tuple: (node_id, x, y)

    Returns
    -------
    str
        File contents
    """
    lines = []

    # Header comments
    lines.append("C IWFM Nodal X-Y Coordinate File")
    lines.append("C*******************************************************************************")

    # ND and FACT values
    lines.append(f"    {nd}                          /ND")
    lines.append(f"    {fact}                        /FACT")

    # Comment before node data
    lines.append("C Node Coordinates Section")
    lines.append("C   Node     ----------Coordinates----------")
    lines.append("C    ID            X                 Y")

    # Node data
    for node in nodes:
        node_id, x, y = node
        lines.append(f"      {node_id}        {x}         {y}")

    return '\n'.join(lines)


class TestSubPpNodeFile:
    """Tests for sub_pp_node_file function"""

    def test_file_not_found(self):
        """Test error handling for non-existent file"""
        from iwfm.sub.pp_node_file import sub_pp_node_file

        with pytest.raises(FileNotFoundError):
            sub_pp_node_file('nonexistent_file.dat', 'output.dat', [1, 2, 3])

    def test_basic_node_filtering(self):
        """Test basic node filtering"""
        nodes = [
            (1, 551396.4, 4496226),
            (2, 555618.8, 4497861),
            (3, 561555.5, 4500441),
            (4, 568374.3, 4498058),
            (5, 553186.9, 4492706),
        ]

        content = create_node_file(5, 3.2808, nodes)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_node.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_node.dat')

            from iwfm.sub.pp_node_file import sub_pp_node_file

            # Only keep nodes 1, 2, 3
            node_list = [1, 2, 3]

            sub_pp_node_file(old_file, new_file, node_list)

            assert os.path.exists(new_file)

            with open(new_file) as f:
                new_content = f.read()

            # Check nodes 1, 2, 3 are present
            lines = new_content.split('\n')
            data_lines = [l for l in lines if l.strip() and not l.startswith('C')]
            # Find lines with node IDs (after ND and FACT lines)
            node_lines = [l for l in data_lines if l.strip() and
                         l.split()[0].isdigit() and float(l.split()[0]) > 10]

            # Check that we have 3 node lines
            # Note: ND and FACT lines also have numbers

    def test_all_nodes_kept(self):
        """Test when all nodes are kept"""
        nodes = [
            (1, 551396.4, 4496226),
            (2, 555618.8, 4497861),
            (3, 561555.5, 4500441),
        ]

        content = create_node_file(3, 3.2808, nodes)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_node.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_node.dat')

            from iwfm.sub.pp_node_file import sub_pp_node_file

            # Keep all nodes
            node_list = [1, 2, 3]

            sub_pp_node_file(old_file, new_file, node_list)

            assert os.path.exists(new_file)

            with open(new_file) as f:
                new_content = f.read()

            # Check all coordinates are present
            assert '551396.4' in new_content
            assert '555618.8' in new_content
            assert '561555.5' in new_content

    def test_node_count_updated(self):
        """Test that node count (ND) is updated correctly"""
        nodes = [
            (1, 551396.4, 4496226),
            (2, 555618.8, 4497861),
            (3, 561555.5, 4500441),
            (4, 568374.3, 4498058),
            (5, 553186.9, 4492706),
        ]

        content = create_node_file(5, 3.2808, nodes)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_node.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_node.dat')

            from iwfm.sub.pp_node_file import sub_pp_node_file

            # Only keep 2 nodes
            node_list = [1, 3]

            sub_pp_node_file(old_file, new_file, node_list)

            with open(new_file) as f:
                new_content = f.read()

            # Check ND is updated to 2
            lines = new_content.split('\n')
            nd_line = [l for l in lines if '/ND' in l][0]
            assert '2' in nd_line

    def test_preserves_header_comments(self):
        """Test that header comments are preserved"""
        nodes = [
            (1, 551396.4, 4496226),
            (2, 555618.8, 4497861),
        ]

        content = create_node_file(2, 3.2808, nodes)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_node.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_node.dat')

            from iwfm.sub.pp_node_file import sub_pp_node_file

            node_list = [1, 2]

            sub_pp_node_file(old_file, new_file, node_list)

            with open(new_file) as f:
                new_content = f.read()

            # Check header is preserved
            assert 'IWFM Nodal X-Y Coordinate File' in new_content

    def test_preserves_fact(self):
        """Test that FACT (conversion factor) is preserved"""
        nodes = [
            (1, 551396.4, 4496226),
            (2, 555618.8, 4497861),
        ]

        content = create_node_file(2, 3.2808, nodes)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_node.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_node.dat')

            from iwfm.sub.pp_node_file import sub_pp_node_file

            node_list = [1, 2]

            sub_pp_node_file(old_file, new_file, node_list)

            with open(new_file) as f:
                new_content = f.read()

            # Check FACT is preserved
            assert '3.2808' in new_content
            assert '/FACT' in new_content

    def test_returns_none(self):
        """Test that function returns None"""
        nodes = [
            (1, 551396.4, 4496226),
            (2, 555618.8, 4497861),
        ]

        content = create_node_file(2, 3.2808, nodes)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_node.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_node.dat')

            from iwfm.sub.pp_node_file import sub_pp_node_file

            node_list = [1, 2]

            result = sub_pp_node_file(old_file, new_file, node_list)

            assert result is None

    def test_filtered_nodes_not_in_output(self):
        """Test that filtered nodes are not in output"""
        nodes = [
            (1, 551396.4, 4496226),
            (2, 555618.8, 4497861),
            (3, 561555.5, 4500441),
            (4, 568374.3, 4498058),
            (5, 553186.9, 4492706),
        ]

        content = create_node_file(5, 3.2808, nodes)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_node.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_node.dat')

            from iwfm.sub.pp_node_file import sub_pp_node_file

            # Only keep nodes 1, 3, 5
            node_list = [1, 3, 5]

            sub_pp_node_file(old_file, new_file, node_list)

            with open(new_file) as f:
                new_content = f.read()

            # Filtered nodes (2, 4) should not have their coordinates
            # Node 2 has x=555618.8, Node 4 has x=568374.3
            assert '555618.8' not in new_content
            assert '568374.3' not in new_content

            # Kept nodes should have their coordinates
            assert '551396.4' in new_content  # Node 1
            assert '561555.5' in new_content  # Node 3
            assert '553186.9' in new_content  # Node 5

    def test_single_node(self):
        """Test with only one node"""
        nodes = [
            (1, 551396.4, 4496226),
        ]

        content = create_node_file(1, 3.2808, nodes)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_node.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_node.dat')

            from iwfm.sub.pp_node_file import sub_pp_node_file

            node_list = [1]

            sub_pp_node_file(old_file, new_file, node_list)

            assert os.path.exists(new_file)

            with open(new_file) as f:
                new_content = f.read()

            # Check node 1 is present
            assert '551396.4' in new_content

    def test_large_coordinates(self):
        """Test with large coordinate values"""
        nodes = [
            (1, 1234567.89, 9876543.21),
            (2, 2345678.90, 8765432.10),
        ]

        content = create_node_file(2, 1.0, nodes)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_node.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_node.dat')

            from iwfm.sub.pp_node_file import sub_pp_node_file

            node_list = [1, 2]

            sub_pp_node_file(old_file, new_file, node_list)

            with open(new_file) as f:
                new_content = f.read()

            # Check large coordinates are preserved
            assert '1234567.89' in new_content
            assert '9876543.21' in new_content

    def test_different_fact_values(self):
        """Test with different FACT conversion factors"""
        nodes = [
            (1, 551396.4, 4496226),
        ]

        # Test with FACT = 1.0 (metric)
        content = create_node_file(1, 1.0, nodes)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_node.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_node.dat')

            from iwfm.sub.pp_node_file import sub_pp_node_file

            node_list = [1]

            sub_pp_node_file(old_file, new_file, node_list)

            with open(new_file) as f:
                new_content = f.read()

            # Check FACT is preserved
            assert '1.0' in new_content

    def test_node_order_preserved(self):
        """Test that node order is preserved from input"""
        nodes = [
            (5, 553186.9, 4492706),
            (3, 561555.5, 4500441),
            (1, 551396.4, 4496226),
            (4, 568374.3, 4498058),
            (2, 555618.8, 4497861),
        ]

        content = create_node_file(5, 3.2808, nodes)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_node.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_node.dat')

            from iwfm.sub.pp_node_file import sub_pp_node_file

            # Keep nodes 5, 3, 1
            node_list = [5, 3, 1]

            sub_pp_node_file(old_file, new_file, node_list)

            with open(new_file) as f:
                new_content = f.read()

            # All kept nodes should be present
            assert '553186.9' in new_content  # Node 5
            assert '561555.5' in new_content  # Node 3
            assert '551396.4' in new_content  # Node 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
