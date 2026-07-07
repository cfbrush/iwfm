#!/usr/bin/env python
# test_sub_gw_subs_file.py
# Unit tests for sub_gw_subs_file.py
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


def create_subs_file(nouts, hydrographs, ngroup, node_params, layers=4):
    """Create a subsidence file for testing.

    Parameters
    ----------
    nouts : int
        Number of subsidence output hydrographs
    hydrographs : list of tuples
        Each tuple: (id, subtyp, ioutsl, x, y, iouts, name)
        subtyp: 0 = x-y coords, 1 = node number
    ngroup : int
        Number of parametric grid groups (0 for direct node params)
    node_params : list of lists
        Each list: [node_id, sce1, sci1, dc1, dcmin1, hc1, sce2, sci2, dc2, ...]
        Values for each layer (5 values per layer)
    layers : int
        Number of aquifer layers

    Returns
    -------
    str
        File contents
    """
    lines = []

    # Header comments
    lines.append("C IWFM Subsidence Component Main Data File")
    lines.append("C*******************************************************************************")

    # File names and factors section (5 data lines to skip)
    lines.append("                                                  / INISUBFL")
    lines.append("                                                  / TPSOUTFL")
    lines.append("                                                  / FNSUBFL")
    lines.append("     1.0                                          / FACTLTOU")
    lines.append("     FEET                                         / UNITLTOU")

    # Hydrograph output section
    lines.append("C Subsidence Output Data")
    lines.append(f"    {nouts}                                         / NOUTS")
    lines.append("    1.0                                           / FACTXY")
    lines.append("    Results/Subsidence.out                        / SUBHYDOUTFL")

    # Hydrograph locations
    lines.append("C  ID  SUBTYP  IOUTSL  X  Y  IOUTS  NAME")
    for hyd in hydrographs:
        hyd_id, subtyp, ioutsl, x, y, iouts, name = hyd
        if subtyp == 0:  # x-y coordinates
            lines.append(f"    {hyd_id}     {subtyp}     {ioutsl}     {x}     {y}     0     {name}")
        else:  # node number
            lines.append(f"    {hyd_id}     {subtyp}     {ioutsl}                          {iouts}     {name}")

    # Parametric grid section
    lines.append("C Subsidence Parameters")
    lines.append(f"         {ngroup}                      / NGROUP")

    # Factors line (1 data line to skip after NGROUP + 1)
    lines.append("C  FX  FSCE  FSCI  FDC  FDCMIN  FHC")
    lines.append("   1.0   1.0   1.0   1.0   1.0   1.0")

    # Node parameters section
    # Format: first line has 6 items (node_id + 5 params), subsequent layer lines have 5 items
    lines.append("C Node Subsidence Parameters")
    lines.append("C  ID  SCE  SCI  DC  DCMIN  HC")
    for node_data in node_params:
        node_id = node_data[0]
        # First layer line includes node ID
        idx = 1
        lines.append(f"        {node_id}       {node_data[idx]}       {node_data[idx+1]}       {node_data[idx+2]}       {node_data[idx+3]}       {node_data[idx+4]}")
        # Subsequent layer lines don't have node ID (only 5 values)
        for layer in range(1, layers):
            idx = 1 + layer * 5
            if idx + 4 < len(node_data):
                lines.append(f"                {node_data[idx]}       {node_data[idx+1]}       {node_data[idx+2]}       {node_data[idx+3]}       {node_data[idx+4]}")
            else:
                # Use default values if not enough data provided
                lines.append(f"                1.0E-07       1.0E-05       50.0       1       99999.0")

    return '\n'.join(lines)


class TestSubGwSubsFile:
    """Tests for sub_gw_subs_file function"""

    def test_file_not_found(self):
        """Test error handling for non-existent file"""
        from iwfm.sub.gw_subs_file import sub_gw_subs_file
        from shapely.geometry import Polygon

        bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

        with pytest.raises(FileNotFoundError):
            sub_gw_subs_file('nonexistent_file.dat', 'output.dat', [1, 2, 3], bounding_poly)

    def test_no_hydrographs(self):
        """Test subsidence file with no hydrograph outputs"""
        # 2 nodes with 4 layers each (node_id + 5 values per layer = 21 values)
        node_params = [
            [1, 1.7e-07, 1.3e-05, 60.0, 1, 99999.0,
                1.7e-07, 1.3e-05, 8.0, 1, 99999.0,
                1.7e-07, 1.3e-05, 73.0, 1, 99999.0,
                1.7e-07, 1.3e-05, 28.0, 1, 99999.0],
            [2, 1.7e-07, 1.7e-05, 125.0, 1, 99999.0,
                1.7e-07, 1.7e-05, 78.0, 1, 99999.0,
                1.7e-07, 1.7e-05, 94.0, 1, 99999.0,
                1.7e-07, 1.7e-05, 26.0, 1, 99999.0],
        ]

        content = create_subs_file(0, [], 0, node_params, layers=4)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_subs.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_subs.dat')

            from iwfm.sub.gw_subs_file import sub_gw_subs_file
            from shapely.geometry import Polygon

            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            sub_gw_subs_file(old_file, new_file, [1, 2], bounding_poly)

            assert os.path.exists(new_file)

            with open(new_file) as f:
                new_content = f.read()

            # NOUTS should still be 0
            assert '/ NOUTS' in new_content

    def test_filter_hydrographs_by_location(self):
        """Test filtering hydrographs based on bounding polygon"""
        node_params = [
            [1, 1.7e-07, 1.3e-05, 60.0, 1, 99999.0,
                1.7e-07, 1.3e-05, 8.0, 1, 99999.0,
                1.7e-07, 1.3e-05, 73.0, 1, 99999.0,
                1.7e-07, 1.3e-05, 28.0, 1, 99999.0],
            [2, 1.7e-07, 1.7e-05, 125.0, 1, 99999.0,
                1.7e-07, 1.7e-05, 78.0, 1, 99999.0,
                1.7e-07, 1.7e-05, 94.0, 1, 99999.0,
                1.7e-07, 1.7e-05, 26.0, 1, 99999.0],
        ]

        # Hydrographs: 1 inside (50,50), 2 outside (500,500)
        hydrographs = [
            (1, 0, 1, 50.0, 50.0, 0, 'Inside'),
            (2, 0, 1, 500.0, 500.0, 0, 'Outside'),
        ]

        content = create_subs_file(2, hydrographs, 0, node_params, layers=4)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_subs.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_subs.dat')

            from iwfm.sub.gw_subs_file import sub_gw_subs_file
            from shapely.geometry import Polygon

            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            sub_gw_subs_file(old_file, new_file, [1, 2], bounding_poly)

            with open(new_file) as f:
                new_content = f.read()

            # NOUTS should be updated to 1
            lines = new_content.split('\n')
            nouts_line = [l for l in lines if '/ NOUTS' in l][0]
            assert '1' in nouts_line

    def test_filter_nodes_not_in_submodel(self):
        """Test filtering node parameters for nodes not in submodel"""
        # 3 nodes, only nodes 1 and 2 in submodel
        node_params = [
            [1, 1.7e-07, 1.3e-05, 60.0, 1, 99999.0,
                1.7e-07, 1.3e-05, 8.0, 1, 99999.0,
                1.7e-07, 1.3e-05, 73.0, 1, 99999.0,
                1.7e-07, 1.3e-05, 28.0, 1, 99999.0],
            [2, 1.7e-07, 1.7e-05, 125.0, 1, 99999.0,
                1.7e-07, 1.7e-05, 78.0, 1, 99999.0,
                1.7e-07, 1.7e-05, 94.0, 1, 99999.0,
                1.7e-07, 1.7e-05, 26.0, 1, 99999.0],
            [3, 1.6e-07, 2.7e-05, 163.0, 1, 99999.0,
                1.6e-07, 2.7e-05, 96.0, 1, 99999.0,
                1.6e-07, 2.7e-05, 90.0, 1, 99999.0,
                1.6e-07, 2.7e-05, 32.0, 1, 99999.0],
        ]

        content = create_subs_file(0, [], 0, node_params, layers=4)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_subs.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_subs.dat')

            from iwfm.sub.gw_subs_file import sub_gw_subs_file
            from shapely.geometry import Polygon

            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            # Only nodes 1 and 2 in submodel (not node 3)
            sub_gw_subs_file(old_file, new_file, [1, 2], bounding_poly)

            with open(new_file) as f:
                new_content = f.read()

            # Node 3 parameters should be removed
            # Count lines starting with node IDs
            lines = new_content.split('\n')
            node_lines = [l for l in lines if l.strip().startswith('1 ') or
                          l.strip().startswith('2 ') or l.strip().startswith('3 ')]
            # Should only have nodes 1 and 2
            assert len([l for l in node_lines if l.strip().startswith('3 ')]) == 0

    def test_all_hydrographs_inside(self):
        """Test when all hydrographs are inside the bounding polygon"""
        node_params = [
            [1, 1.7e-07, 1.3e-05, 60.0, 1, 99999.0,
                1.7e-07, 1.3e-05, 8.0, 1, 99999.0,
                1.7e-07, 1.3e-05, 73.0, 1, 99999.0,
                1.7e-07, 1.3e-05, 28.0, 1, 99999.0],
            [2, 1.7e-07, 1.7e-05, 125.0, 1, 99999.0,
                1.7e-07, 1.7e-05, 78.0, 1, 99999.0,
                1.7e-07, 1.7e-05, 94.0, 1, 99999.0,
                1.7e-07, 1.7e-05, 26.0, 1, 99999.0],
        ]

        hydrographs = [
            (1, 0, 1, 50.0, 50.0, 0, 'Point1'),
            (2, 0, 1, 25.0, 75.0, 0, 'Point2'),
            (3, 0, 1, 75.0, 25.0, 0, 'Point3'),
        ]

        content = create_subs_file(3, hydrographs, 0, node_params, layers=4)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_subs.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_subs.dat')

            from iwfm.sub.gw_subs_file import sub_gw_subs_file
            from shapely.geometry import Polygon

            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            sub_gw_subs_file(old_file, new_file, [1, 2], bounding_poly)

            with open(new_file) as f:
                new_content = f.read()

            # NOUTS should still be 3
            lines = new_content.split('\n')
            nouts_line = [l for l in lines if '/ NOUTS' in l][0]
            assert '3' in nouts_line

    def test_all_hydrographs_outside(self):
        """Test when all hydrographs are outside the bounding polygon"""
        node_params = [
            [1, 1.7e-07, 1.3e-05, 60.0, 1, 99999.0,
                1.7e-07, 1.3e-05, 8.0, 1, 99999.0,
                1.7e-07, 1.3e-05, 73.0, 1, 99999.0,
                1.7e-07, 1.3e-05, 28.0, 1, 99999.0],
            [2, 1.7e-07, 1.7e-05, 125.0, 1, 99999.0,
                1.7e-07, 1.7e-05, 78.0, 1, 99999.0,
                1.7e-07, 1.7e-05, 94.0, 1, 99999.0,
                1.7e-07, 1.7e-05, 26.0, 1, 99999.0],
        ]

        hydrographs = [
            (1, 0, 1, 500.0, 500.0, 0, 'Outside1'),
            (2, 0, 1, 600.0, 600.0, 0, 'Outside2'),
        ]

        content = create_subs_file(2, hydrographs, 0, node_params, layers=4)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_subs.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_subs.dat')

            from iwfm.sub.gw_subs_file import sub_gw_subs_file
            from shapely.geometry import Polygon

            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            sub_gw_subs_file(old_file, new_file, [1, 2], bounding_poly)

            with open(new_file) as f:
                new_content = f.read()

            # NOUTS should be 0
            lines = new_content.split('\n')
            nouts_line = [l for l in lines if '/ NOUTS' in l][0]
            assert '0' in nouts_line

    def test_verbose_mode(self):
        """Test that verbose mode runs without error"""
        node_params = [
            [1, 1.7e-07, 1.3e-05, 60.0, 1, 99999.0,
                1.7e-07, 1.3e-05, 8.0, 1, 99999.0,
                1.7e-07, 1.3e-05, 73.0, 1, 99999.0,
                1.7e-07, 1.3e-05, 28.0, 1, 99999.0],
            [2, 1.7e-07, 1.7e-05, 125.0, 1, 99999.0,
                1.7e-07, 1.7e-05, 78.0, 1, 99999.0,
                1.7e-07, 1.7e-05, 94.0, 1, 99999.0,
                1.7e-07, 1.7e-05, 26.0, 1, 99999.0],
        ]

        content = create_subs_file(0, [], 0, node_params, layers=4)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_subs.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_subs.dat')

            from iwfm.sub.gw_subs_file import sub_gw_subs_file
            from shapely.geometry import Polygon

            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            # Should not raise an error with verbose=True
            sub_gw_subs_file(old_file, new_file, [1, 2], bounding_poly, verbose=True)

            assert os.path.exists(new_file)

    def test_returns_none(self):
        """Test that function returns None"""
        node_params = [
            [1, 1.7e-07, 1.3e-05, 60.0, 1, 99999.0,
                1.7e-07, 1.3e-05, 8.0, 1, 99999.0,
                1.7e-07, 1.3e-05, 73.0, 1, 99999.0,
                1.7e-07, 1.3e-05, 28.0, 1, 99999.0],
            [2, 1.7e-07, 1.7e-05, 125.0, 1, 99999.0,
                1.7e-07, 1.7e-05, 78.0, 1, 99999.0,
                1.7e-07, 1.7e-05, 94.0, 1, 99999.0,
                1.7e-07, 1.7e-05, 26.0, 1, 99999.0],
        ]

        content = create_subs_file(0, [], 0, node_params, layers=4)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_subs.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_subs.dat')

            from iwfm.sub.gw_subs_file import sub_gw_subs_file
            from shapely.geometry import Polygon

            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            result = sub_gw_subs_file(old_file, new_file, [1, 2], bounding_poly)

            assert result is None

    def test_preserves_header_comments(self):
        """Test that header comments are preserved in output"""
        node_params = [
            [1, 1.7e-07, 1.3e-05, 60.0, 1, 99999.0,
                1.7e-07, 1.3e-05, 8.0, 1, 99999.0,
                1.7e-07, 1.3e-05, 73.0, 1, 99999.0,
                1.7e-07, 1.3e-05, 28.0, 1, 99999.0],
            [2, 1.7e-07, 1.7e-05, 125.0, 1, 99999.0,
                1.7e-07, 1.7e-05, 78.0, 1, 99999.0,
                1.7e-07, 1.7e-05, 94.0, 1, 99999.0,
                1.7e-07, 1.7e-05, 26.0, 1, 99999.0],
        ]

        content = create_subs_file(0, [], 0, node_params, layers=4)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_subs.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_subs.dat')

            from iwfm.sub.gw_subs_file import sub_gw_subs_file
            from shapely.geometry import Polygon

            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            sub_gw_subs_file(old_file, new_file, [1, 2], bounding_poly)

            with open(new_file) as f:
                new_content = f.read()

            # Check header is preserved
            assert 'IWFM Subsidence Component' in new_content

    def test_multiple_layers(self):
        """Test subsidence file with multiple aquifer layers"""
        # 2 nodes with 4 layers each
        node_params = [
            [1, 1.7e-07, 1.3e-05, 60.0, 1, 99999.0,
                1.7e-07, 1.3e-05, 8.0, 1, 99999.0,
                1.7e-07, 1.3e-05, 73.0, 1, 99999.0,
                1.7e-07, 1.3e-05, 28.0, 1, 99999.0],
            [2, 1.7e-07, 1.7e-05, 125.0, 1, 99999.0,
                1.7e-07, 1.7e-05, 78.0, 1, 99999.0,
                1.7e-07, 1.7e-05, 94.0, 1, 99999.0,
                1.7e-07, 1.7e-05, 26.0, 1, 99999.0],
            [3, 1.6e-07, 2.7e-05, 163.0, 1, 99999.0,
                1.6e-07, 2.7e-05, 96.0, 1, 99999.0,
                1.6e-07, 2.7e-05, 90.0, 1, 99999.0,
                1.6e-07, 2.7e-05, 32.0, 1, 99999.0],
        ]

        content = create_subs_file(0, [], 0, node_params, layers=4)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_subs.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_subs.dat')

            from iwfm.sub.gw_subs_file import sub_gw_subs_file
            from shapely.geometry import Polygon

            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            # Only nodes 1 and 3 in submodel
            sub_gw_subs_file(old_file, new_file, [1, 3], bounding_poly)

            assert os.path.exists(new_file)

            with open(new_file) as f:
                new_content = f.read()

            # Node 2 should be removed
            # Count parameter blocks
            lines = new_content.split('\n')
            # Look for lines starting with node ID and having 6 items
            node_header_lines = []
            for l in lines:
                parts = l.split()
                if len(parts) == 6:
                    try:
                        node_id = int(parts[0])
                        if node_id in [1, 2, 3]:
                            node_header_lines.append(node_id)
                    except ValueError:
                        pass

            # Should only have nodes 1 and 3
            assert 1 in node_header_lines
            assert 3 in node_header_lines
            assert 2 not in node_header_lines

    def test_preserves_file_references(self):
        """Test that file reference lines are preserved"""
        node_params = [
            [1, 1.7e-07, 1.3e-05, 60.0, 1, 99999.0,
                1.7e-07, 1.3e-05, 8.0, 1, 99999.0,
                1.7e-07, 1.3e-05, 73.0, 1, 99999.0,
                1.7e-07, 1.3e-05, 28.0, 1, 99999.0],
            [2, 1.7e-07, 1.7e-05, 125.0, 1, 99999.0,
                1.7e-07, 1.7e-05, 78.0, 1, 99999.0,
                1.7e-07, 1.7e-05, 94.0, 1, 99999.0,
                1.7e-07, 1.7e-05, 26.0, 1, 99999.0],
        ]

        content = create_subs_file(0, [], 0, node_params, layers=4)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_subs.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_subs.dat')

            from iwfm.sub.gw_subs_file import sub_gw_subs_file
            from shapely.geometry import Polygon

            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            sub_gw_subs_file(old_file, new_file, [1, 2], bounding_poly)

            with open(new_file) as f:
                new_content = f.read()

            # Check file references are preserved
            assert '/ INISUBFL' in new_content
            assert '/ TPSOUTFL' in new_content
            assert '/ FNSUBFL' in new_content
            assert '/ FACTLTOU' in new_content
            assert '/ UNITLTOU' in new_content


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
