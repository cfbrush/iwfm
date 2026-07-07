#!/usr/bin/env python
# test_sub_pp_strat_file.py
# Unit tests for sub_pp_strat_file.py
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


def create_strat_file(nl, fact, nodes):
    """Create a stratigraphy file for testing.

    Parameters
    ----------
    nl : int
        Number of layers
    fact : float
        Conversion factor for elevations and thicknesses
    nodes : list of tuples
        Each tuple: (node_id, elevation, layer_thicknesses...)
        layer_thicknesses is a list of (aquitard_thick, aquifer_thick) pairs

    Returns
    -------
    str
        File contents

    Note: The function sub_pp_strat_file parses:
    - skip_ahead(0, ..., 0) to get NL line
    - skip_ahead(line_index + 3, ..., 0) to skip NL, FACT, and comment to reach first node data
    - Then reads remaining lines, filtering by node_id in node_list
    """
    lines = []

    # Header comments
    lines.append("C IWFM Stratigraphy File")
    lines.append("C*******************************************************************************")

    # NL - first data line (number of layers)
    lines.append(f"    {nl}                             /NL")

    # FACT - second data line (conversion factor)
    lines.append(f"    {fact}                           /FACT")

    # Comments before stratigraphy data
    lines.append("C Stratigraphy Data")
    lines.append("C  Node  Elevation   Layer Thicknesses...")

    # Node stratigraphy data lines - NO comments after this point!
    for node in nodes:
        node_id = node[0]
        elevation = node[1]
        thicknesses = node[2:]
        thick_str = '      '.join(f'{t:8.2f}' for t in thicknesses)
        lines.append(f"      {node_id}    {elevation:8.2f}      {thick_str}")

    return '\n'.join(lines)


class TestSubPpStratFile:
    """Tests for sub_pp_strat_file function"""

    def test_file_not_found(self):
        """Test error handling for non-existent file"""
        from iwfm.sub.pp_strat_file import sub_pp_strat_file

        with pytest.raises(FileNotFoundError):
            sub_pp_strat_file('nonexistent_file.dat', 'output.dat', [1, 2, 3])

    def test_basic_node_filtering(self):
        """Test basic node filtering"""
        nodes = [
            (1, 576.95, 0.00, 113.69, 0.00, 106.37, 0.00, 152.80, 0.00, 50.00),
            (2, 683.75, 0.00, 176.92, 0.00, 119.59, 0.00, 116.60, 0.00, 50.00),
            (3, 712.80, 0.00, 190.84, 0.00, 121.52, 0.00, 101.99, 0.00, 50.00),
            (4, 730.10, 0.00, 198.56, 0.00, 124.74, 0.00, 112.17, 0.00, 50.00),
            (5, 462.64, 0.00, 102.67, 0.00, 131.62, 0.00, 112.44, 0.00, 50.00),
        ]

        content = create_strat_file(4, 1.0, nodes)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_strat.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_strat.dat')

            from iwfm.sub.pp_strat_file import sub_pp_strat_file

            # Only keep nodes 1, 3, 5
            node_list = [1, 3, 5]

            sub_pp_strat_file(old_file, new_file, node_list)

            assert os.path.exists(new_file)

            with open(new_file) as f:
                new_content = f.read()

            # Check nodes 1, 3, 5 are present (check elevations)
            assert '576.95' in new_content  # Node 1
            assert '712.80' in new_content  # Node 3
            assert '462.64' in new_content  # Node 5

            # Check nodes 2, 4 are not present
            assert '683.75' not in new_content  # Node 2
            assert '730.10' not in new_content  # Node 4

    def test_all_nodes_kept(self):
        """Test when all nodes are kept"""
        nodes = [
            (1, 576.95, 0.00, 113.69, 0.00, 106.37),
            (2, 683.75, 0.00, 176.92, 0.00, 119.59),
            (3, 712.80, 0.00, 190.84, 0.00, 121.52),
        ]

        content = create_strat_file(2, 1.0, nodes)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_strat.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_strat.dat')

            from iwfm.sub.pp_strat_file import sub_pp_strat_file

            # Keep all nodes
            node_list = [1, 2, 3]

            sub_pp_strat_file(old_file, new_file, node_list)

            assert os.path.exists(new_file)

            with open(new_file) as f:
                new_content = f.read()

            # Check all elevations are present
            assert '576.95' in new_content
            assert '683.75' in new_content
            assert '712.80' in new_content

    def test_preserves_header(self):
        """Test that header comments and parameters are preserved"""
        nodes = [
            (1, 576.95, 0.00, 113.69, 0.00, 106.37),
            (2, 683.75, 0.00, 176.92, 0.00, 119.59),
        ]

        content = create_strat_file(2, 3.2808, nodes)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_strat.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_strat.dat')

            from iwfm.sub.pp_strat_file import sub_pp_strat_file

            node_list = [1, 2]

            sub_pp_strat_file(old_file, new_file, node_list)

            with open(new_file) as f:
                new_content = f.read()

            # Check header is preserved
            assert 'IWFM Stratigraphy File' in new_content
            # Check NL is preserved
            assert '/NL' in new_content
            # Check FACT is preserved
            assert '3.2808' in new_content
            assert '/FACT' in new_content

    def test_preserves_nl(self):
        """Test that NL (number of layers) is preserved"""
        nodes = [
            (1, 576.95, 0.00, 113.69, 0.00, 106.37, 0.00, 152.80, 0.00, 50.00),
        ]

        content = create_strat_file(4, 1.0, nodes)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_strat.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_strat.dat')

            from iwfm.sub.pp_strat_file import sub_pp_strat_file

            node_list = [1]

            sub_pp_strat_file(old_file, new_file, node_list)

            with open(new_file) as f:
                new_content = f.read()

            # Check NL is preserved
            lines = new_content.split('\n')
            nl_line = [l for l in lines if '/NL' in l][0]
            assert '4' in nl_line

    def test_returns_none(self):
        """Test that function returns None"""
        nodes = [
            (1, 576.95, 0.00, 113.69, 0.00, 106.37),
            (2, 683.75, 0.00, 176.92, 0.00, 119.59),
        ]

        content = create_strat_file(2, 1.0, nodes)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_strat.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_strat.dat')

            from iwfm.sub.pp_strat_file import sub_pp_strat_file

            node_list = [1, 2]

            result = sub_pp_strat_file(old_file, new_file, node_list)

            assert result is None

    def test_filtered_nodes_not_in_output(self):
        """Test that filtered nodes are not in output"""
        nodes = [
            (1, 100.00, 0.00, 10.00, 0.00, 20.00),
            (2, 200.00, 0.00, 30.00, 0.00, 40.00),
            (3, 300.00, 0.00, 50.00, 0.00, 60.00),
            (4, 400.00, 0.00, 70.00, 0.00, 80.00),
            (5, 500.00, 0.00, 90.00, 0.00, 100.00),
        ]

        content = create_strat_file(2, 1.0, nodes)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_strat.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_strat.dat')

            from iwfm.sub.pp_strat_file import sub_pp_strat_file

            # Only keep nodes 1, 3, 5
            node_list = [1, 3, 5]

            sub_pp_strat_file(old_file, new_file, node_list)

            with open(new_file) as f:
                new_content = f.read()

            # Filtered nodes (2, 4) elevations should not be in output
            assert '200.00' not in new_content
            assert '400.00' not in new_content

            # Kept nodes should have their elevations
            assert '100.00' in new_content  # Node 1
            assert '300.00' in new_content  # Node 3
            assert '500.00' in new_content  # Node 5

    def test_single_node(self):
        """Test with only one node kept"""
        nodes = [
            (1, 576.95, 0.00, 113.69, 0.00, 106.37),
            (2, 683.75, 0.00, 176.92, 0.00, 119.59),
            (3, 712.80, 0.00, 190.84, 0.00, 121.52),
        ]

        content = create_strat_file(2, 1.0, nodes)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_strat.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_strat.dat')

            from iwfm.sub.pp_strat_file import sub_pp_strat_file

            # Only keep node 2
            node_list = [2]

            sub_pp_strat_file(old_file, new_file, node_list)

            assert os.path.exists(new_file)

            with open(new_file) as f:
                new_content = f.read()

            # Only node 2 should be present
            assert '683.75' in new_content  # Node 2
            assert '576.95' not in new_content  # Node 1
            assert '712.80' not in new_content  # Node 3

    def test_different_layer_counts(self):
        """Test with different number of layers"""
        # 2 layers: 4 thickness values per node
        nodes = [
            (1, 500.00, 0.00, 100.00, 0.00, 150.00),
            (2, 600.00, 0.00, 120.00, 0.00, 180.00),
        ]

        content = create_strat_file(2, 1.0, nodes)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_strat.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_strat.dat')

            from iwfm.sub.pp_strat_file import sub_pp_strat_file

            node_list = [1, 2]

            sub_pp_strat_file(old_file, new_file, node_list)

            with open(new_file) as f:
                new_content = f.read()

            # Check layer thicknesses are preserved
            assert '100.00' in new_content  # Node 1 aquifer thickness layer 1
            assert '150.00' in new_content  # Node 1 aquifer thickness layer 2
            assert '120.00' in new_content  # Node 2 aquifer thickness layer 1
            assert '180.00' in new_content  # Node 2 aquifer thickness layer 2

    def test_large_elevations(self):
        """Test with large elevation values"""
        nodes = [
            (1, 3448.72, 0.00, 2426.98, 0.00, 824.64, 0.00, 50.00),
            (2, 2016.52, 0.00, 1201.19, 0.00, 210.52, 0.00, 50.00),
        ]

        content = create_strat_file(3, 1.0, nodes)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_strat.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_strat.dat')

            from iwfm.sub.pp_strat_file import sub_pp_strat_file

            node_list = [1, 2]

            sub_pp_strat_file(old_file, new_file, node_list)

            with open(new_file) as f:
                new_content = f.read()

            # Check large elevations are preserved
            assert '3448.72' in new_content
            assert '2016.52' in new_content
            assert '2426.98' in new_content
            assert '1201.19' in new_content

    def test_different_fact_values(self):
        """Test with different FACT conversion factors"""
        nodes = [
            (1, 576.95, 0.00, 113.69, 0.00, 106.37),
        ]

        # Test with FACT = 3.2808 (feet to meters)
        content = create_strat_file(2, 3.2808, nodes)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_strat.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_strat.dat')

            from iwfm.sub.pp_strat_file import sub_pp_strat_file

            node_list = [1]

            sub_pp_strat_file(old_file, new_file, node_list)

            with open(new_file) as f:
                new_content = f.read()

            # Check FACT is preserved
            assert '3.2808' in new_content

    def test_node_order_preserved(self):
        """Test that node order follows original file order"""
        nodes = [
            (5, 500.00, 0.00, 100.00, 0.00, 150.00),
            (3, 300.00, 0.00, 80.00, 0.00, 120.00),
            (1, 100.00, 0.00, 50.00, 0.00, 70.00),
            (4, 400.00, 0.00, 90.00, 0.00, 140.00),
            (2, 200.00, 0.00, 60.00, 0.00, 100.00),
        ]

        content = create_strat_file(2, 1.0, nodes)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_strat.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_strat.dat')

            from iwfm.sub.pp_strat_file import sub_pp_strat_file

            # Keep nodes 5, 3, 1
            node_list = [5, 3, 1]

            sub_pp_strat_file(old_file, new_file, node_list)

            with open(new_file) as f:
                new_content = f.read()

            # All kept nodes should be present
            assert '500.00' in new_content  # Node 5
            assert '300.00' in new_content  # Node 3
            assert '100.00' in new_content  # Node 1

    def test_aquitard_thicknesses(self):
        """Test that non-zero aquitard thicknesses are preserved"""
        nodes = [
            (1, 565.85, 0.00, 327.86, 7.62, 1312.07, 0.00, 1105.85),
            (2, 638.07, 0.00, 250.04, 17.53, 1399.61, 0.00, 1720.29),
        ]

        content = create_strat_file(3, 1.0, nodes)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_strat.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_strat.dat')

            from iwfm.sub.pp_strat_file import sub_pp_strat_file

            node_list = [1, 2]

            sub_pp_strat_file(old_file, new_file, node_list)

            with open(new_file) as f:
                new_content = f.read()

            # Check non-zero aquitard thicknesses are preserved
            assert '7.62' in new_content  # Node 1 aquitard
            assert '17.53' in new_content  # Node 2 aquitard


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
