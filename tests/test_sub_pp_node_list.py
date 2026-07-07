#!/usr/bin/env python
# test_sub_pp_node_list.py
# Unit tests for sub_pp_node_list.py
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


def create_elem_file(ne, nregn, subregions, elements):
    """Create an element configuration file for testing.

    Parameters
    ----------
    ne : int
        Number of elements
    nregn : int
        Number of subregions
    subregions : list of tuples
        Each tuple: (sr_id, sr_name)
    elements : list of tuples
        Each tuple: (elem_id, node1, node2, node3, node4, subregion)
        node4 = 0 for triangular elements

    Returns
    -------
    str
        File contents

    Note: The function sub_pp_node_list parses:
    - skip_ahead(0, ..., 0) to get NE line
    - skip_ahead(line_index + 1, ..., 0) to get NREGN line
    - skip_ahead(line_index + 1, ..., 0) to get first subregion line
    - skip_ahead(line_index + subs, ..., 0) to get first element line
    - Then reads ALL remaining lines as element data (no comments after)
    """
    lines = []

    # Header comments
    lines.append("C IWFM Element Configuration File")
    lines.append("C*******************************************************************************")

    # NE - first data line after comments
    lines.append(f"    {ne}                          / NE")

    # Comment before NREGN
    lines.append("C Number of subregions")

    # NREGN - next data line
    lines.append(f"    {nregn}                            / NREGN")

    # Comment before subregion names section
    lines.append("C Subregion Names")
    lines.append("C  ID  RNAME")

    # Subregion data lines (one per subregion)
    for sr_id, sr_name in subregions:
        lines.append(f"    {sr_id}      {sr_name}             /RNAME{sr_id}")

    # Comment before element data (skip_ahead will skip this)
    lines.append("C Element Configuration Data")
    lines.append("C  IE  IDE(1)  IDE(2)  IDE(3)  IDE(4)  IRGE")

    # Element data lines - NO comments after this point!
    for elem in elements:
        elem_id, n1, n2, n3, n4, irge = elem
        lines.append(f"    {elem_id}           {n1}       {n2}       {n3}       {n4}         {irge}")

    return '\n'.join(lines)


class TestSubPpNodeList:
    """Tests for sub_pp_node_list function"""

    def test_file_not_found(self):
        """Test error handling for non-existent file"""
        from iwfm.sub.pp_node_list import sub_pp_node_list

        with pytest.raises(FileNotFoundError):
            sub_pp_node_list('nonexistent_file.dat', [[1], [2], [3]])

    def test_basic_node_extraction(self):
        """Test basic node extraction from elements"""
        subregions = [
            (1, 'Subregion 1'),
        ]
        elements = [
            (1, 1, 8, 9, 5, 1),
            (2, 1, 5, 6, 2, 1),
            (3, 2, 6, 7, 3, 1),
        ]

        content = create_elem_file(3, 1, subregions, elements)

        with tempfile.TemporaryDirectory() as tmpdir:
            elem_file = os.path.join(tmpdir, 'elem.dat')
            with open(elem_file, 'w') as f:
                f.write(content)

            from iwfm.sub.pp_node_list import sub_pp_node_list

            # elem_list format: list of [elem_id, ...] where elem_id is extracted
            elem_list = [[1], [2], [3]]

            node_list = sub_pp_node_list(elem_file, elem_list)

            # Element 1: 1, 8, 9, 5
            # Element 2: 1, 5, 6, 2
            # Element 3: 2, 6, 7, 3
            # Unique nodes: 1, 2, 3, 5, 6, 7, 8, 9
            expected_nodes = [1, 2, 3, 5, 6, 7, 8, 9]
            assert node_list == expected_nodes

    def test_partial_elements(self):
        """Test node extraction from subset of elements"""
        subregions = [
            (1, 'Subregion 1'),
        ]
        elements = [
            (1, 1, 8, 9, 5, 1),
            (2, 1, 5, 6, 2, 1),
            (3, 2, 6, 7, 3, 1),
            (4, 10, 11, 12, 13, 1),
            (5, 20, 21, 22, 23, 1),
        ]

        content = create_elem_file(5, 1, subregions, elements)

        with tempfile.TemporaryDirectory() as tmpdir:
            elem_file = os.path.join(tmpdir, 'elem.dat')
            with open(elem_file, 'w') as f:
                f.write(content)

            from iwfm.sub.pp_node_list import sub_pp_node_list

            # Only elements 1, 2
            elem_list = [[1], [2]]

            node_list = sub_pp_node_list(elem_file, elem_list)

            # Element 1: 1, 8, 9, 5
            # Element 2: 1, 5, 6, 2
            # Unique nodes: 1, 2, 5, 6, 8, 9
            expected_nodes = [1, 2, 5, 6, 8, 9]
            assert node_list == expected_nodes

    def test_triangular_elements(self):
        """Test handling of triangular elements (node4 = 0)"""
        subregions = [
            (1, 'Subregion 1'),
        ]
        elements = [
            (1, 3, 7, 4, 0, 1),  # triangular
            (2, 1, 8, 9, 0, 1),  # triangular
            (3, 10, 11, 12, 0, 1),  # triangular
        ]

        content = create_elem_file(3, 1, subregions, elements)

        with tempfile.TemporaryDirectory() as tmpdir:
            elem_file = os.path.join(tmpdir, 'elem.dat')
            with open(elem_file, 'w') as f:
                f.write(content)

            from iwfm.sub.pp_node_list import sub_pp_node_list

            elem_list = [[1], [2], [3]]

            node_list = sub_pp_node_list(elem_file, elem_list)

            # Element 1: 3, 7, 4, 0 (triangular)
            # Element 2: 1, 8, 9, 0 (triangular)
            # Element 3: 10, 11, 12, 0 (triangular)
            # Unique nodes: 1, 3, 4, 7, 8, 9, 10, 11, 12 (0 should be removed)
            expected_nodes = [1, 3, 4, 7, 8, 9, 10, 11, 12]
            assert node_list == expected_nodes
            assert 0 not in node_list

    def test_mixed_elements(self):
        """Test with mix of triangular and quadrilateral elements"""
        subregions = [
            (1, 'Subregion 1'),
        ]
        elements = [
            (1, 1, 2, 3, 4, 1),  # quadrilateral
            (2, 5, 6, 7, 0, 1),  # triangular
            (3, 8, 9, 10, 11, 1),  # quadrilateral
        ]

        content = create_elem_file(3, 1, subregions, elements)

        with tempfile.TemporaryDirectory() as tmpdir:
            elem_file = os.path.join(tmpdir, 'elem.dat')
            with open(elem_file, 'w') as f:
                f.write(content)

            from iwfm.sub.pp_node_list import sub_pp_node_list

            elem_list = [[1], [2], [3]]

            node_list = sub_pp_node_list(elem_file, elem_list)

            # Element 1: 1, 2, 3, 4 (quadrilateral)
            # Element 2: 5, 6, 7, 0 (triangular)
            # Element 3: 8, 9, 10, 11 (quadrilateral)
            # Unique nodes, 0 removed: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11
            expected_nodes = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
            assert node_list == expected_nodes

    def test_nodes_sorted(self):
        """Test that returned nodes are sorted"""
        subregions = [
            (1, 'Subregion 1'),
        ]
        elements = [
            (1, 50, 30, 10, 20, 1),
            (2, 5, 15, 25, 35, 1),
        ]

        content = create_elem_file(2, 1, subregions, elements)

        with tempfile.TemporaryDirectory() as tmpdir:
            elem_file = os.path.join(tmpdir, 'elem.dat')
            with open(elem_file, 'w') as f:
                f.write(content)

            from iwfm.sub.pp_node_list import sub_pp_node_list

            elem_list = [[1], [2]]

            node_list = sub_pp_node_list(elem_file, elem_list)

            # Should be sorted
            assert node_list == sorted(node_list)

    def test_unique_nodes(self):
        """Test that returned nodes are unique"""
        subregions = [
            (1, 'Subregion 1'),
        ]
        # Elements share nodes
        elements = [
            (1, 1, 2, 3, 4, 1),
            (2, 2, 3, 5, 6, 1),  # shares nodes 2, 3 with element 1
            (3, 3, 4, 6, 7, 1),  # shares nodes 3, 4, 6 with elements 1, 2
        ]

        content = create_elem_file(3, 1, subregions, elements)

        with tempfile.TemporaryDirectory() as tmpdir:
            elem_file = os.path.join(tmpdir, 'elem.dat')
            with open(elem_file, 'w') as f:
                f.write(content)

            from iwfm.sub.pp_node_list import sub_pp_node_list

            elem_list = [[1], [2], [3]]

            node_list = sub_pp_node_list(elem_file, elem_list)

            # All nodes should be unique
            assert len(node_list) == len(set(node_list))
            # Element 1: 1, 2, 3, 4
            # Element 2: 2, 3, 5, 6
            # Element 3: 3, 4, 6, 7
            # Unique: 1, 2, 3, 4, 5, 6, 7
            assert node_list == [1, 2, 3, 4, 5, 6, 7]

    def test_single_element(self):
        """Test with single element"""
        subregions = [
            (1, 'Subregion 1'),
        ]
        elements = [
            (1, 1, 2, 3, 4, 1),
        ]

        content = create_elem_file(1, 1, subregions, elements)

        with tempfile.TemporaryDirectory() as tmpdir:
            elem_file = os.path.join(tmpdir, 'elem.dat')
            with open(elem_file, 'w') as f:
                f.write(content)

            from iwfm.sub.pp_node_list import sub_pp_node_list

            elem_list = [[1]]

            node_list = sub_pp_node_list(elem_file, elem_list)

            # Element 1: 1, 2, 3, 4
            expected_nodes = [1, 2, 3, 4]
            assert node_list == expected_nodes

    def test_multiple_subregions(self):
        """Test with multiple subregions"""
        subregions = [
            (1, 'Subregion 1'),
            (2, 'Subregion 2'),
            (3, 'Subregion 3'),
        ]
        elements = [
            (1, 1, 2, 3, 4, 1),
            (2, 5, 6, 7, 8, 2),
            (3, 9, 10, 11, 12, 3),
        ]

        content = create_elem_file(3, 3, subregions, elements)

        with tempfile.TemporaryDirectory() as tmpdir:
            elem_file = os.path.join(tmpdir, 'elem.dat')
            with open(elem_file, 'w') as f:
                f.write(content)

            from iwfm.sub.pp_node_list import sub_pp_node_list

            # Elements 1, 2, 3
            elem_list = [[1], [2], [3]]

            node_list = sub_pp_node_list(elem_file, elem_list)

            # Element 1: 1, 2, 3, 4
            # Element 2: 5, 6, 7, 8
            # Element 3: 9, 10, 11, 12
            expected_nodes = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
            assert node_list == expected_nodes

    def test_elem_list_with_extra_data(self):
        """Test that elem_list works when elements have additional data"""
        subregions = [
            (1, 'Subregion 1'),
        ]
        elements = [
            (1, 1, 2, 3, 4, 1),
            (2, 5, 6, 7, 8, 1),
            (3, 9, 10, 11, 12, 1),
        ]

        content = create_elem_file(3, 1, subregions, elements)

        with tempfile.TemporaryDirectory() as tmpdir:
            elem_file = os.path.join(tmpdir, 'elem.dat')
            with open(elem_file, 'w') as f:
                f.write(content)

            from iwfm.sub.pp_node_list import sub_pp_node_list

            # elem_list with extra data beyond elem_id
            elem_list = [[1, 'extra', 'data'], [2, 'more', 'data'], [3, 'yet', 'more']]

            node_list = sub_pp_node_list(elem_file, elem_list)

            # Element 1: 1, 2, 3, 4
            # Element 2: 5, 6, 7, 8
            # Element 3: 9, 10, 11, 12
            expected_nodes = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
            assert node_list == expected_nodes

    def test_returns_list(self):
        """Test that function returns a list"""
        subregions = [
            (1, 'Subregion 1'),
        ]
        elements = [
            (1, 1, 2, 3, 4, 1),
            (2, 5, 6, 7, 8, 1),
        ]

        content = create_elem_file(2, 1, subregions, elements)

        with tempfile.TemporaryDirectory() as tmpdir:
            elem_file = os.path.join(tmpdir, 'elem.dat')
            with open(elem_file, 'w') as f:
                f.write(content)

            from iwfm.sub.pp_node_list import sub_pp_node_list

            elem_list = [[1], [2]]

            result = sub_pp_node_list(elem_file, elem_list)

            assert isinstance(result, list)
            # All elements should be integers
            for node in result:
                assert isinstance(node, int)

    def test_no_matching_elements(self):
        """Test when elem_list has no matching elements in file"""
        subregions = [
            (1, 'Subregion 1'),
        ]
        elements = [
            (1, 1, 2, 3, 4, 1),
            (2, 5, 6, 7, 8, 1),
        ]

        content = create_elem_file(2, 1, subregions, elements)

        with tempfile.TemporaryDirectory() as tmpdir:
            elem_file = os.path.join(tmpdir, 'elem.dat')
            with open(elem_file, 'w') as f:
                f.write(content)

            from iwfm.sub.pp_node_list import sub_pp_node_list

            # Elements 100, 200 don't exist
            elem_list = [[100], [200]]

            # This may raise an IndexError when trying to pop from empty list
            # or return empty list depending on implementation
            with pytest.raises(IndexError):
                sub_pp_node_list(elem_file, elem_list)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
