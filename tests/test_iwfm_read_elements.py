#!/usr/bin/env python
# test_iwfm_read_elements.py
# Unit tests for iwfm_read_elements.py
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

import tempfile
import os


def create_elements_file(nelements, nsubregions, subregion_names, elements_data):
    """Create IWFM Element file for testing.

    Parameters
    ----------
    nelements : int
        Number of elements
    nsubregions : int
        Number of subregions
    subregion_names : list of str
        Names for each subregion
    elements_data : list of tuples
        Each tuple: (elem_id, node1, node2, node3, node4, subregion)
        node4 = 0 for triangular elements

    Returns
    -------
    str
        File contents
    """
    content = "C IWFM Elements File\n"
    content += "C\n"
    content += f"    {nelements}                           / NE\n"
    content += f"    {nsubregions}                           / NSUBREGIONS\n"

    # Add subregion definitions
    for i, name in enumerate(subregion_names, start=1):
        content += f"    {i}    {name}\n"

    content += "C\n"

    # Element data
    for elem_id, node1, node2, node3, node4, subregion in elements_data:
        content += f"    {elem_id}    {node1}    {node2}    {node3}    {node4}    {subregion}\n"

    return content


class TestIwfmReadElements:
    """Tests for iwfm_read_elements function"""

    def test_single_quadrilateral_element(self):
        """Test reading single quadrilateral element"""
        elements_data = [
            (1, 100, 101, 102, 103, 1)
        ]
        subregion_names = ["Subregion_1"]

        content = create_elements_file(1, 1, subregion_names, elements_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_elements import iwfm_read_elements

            elem_ids, elem_nodes, elem_sub = iwfm_read_elements(temp_file, verbose=False)

            # Verify element IDs
            assert len(elem_ids) == 1
            assert elem_ids[0] == 1

            # Verify element nodes (quadrilateral has 4 nodes)
            assert len(elem_nodes) == 1
            assert elem_nodes[0] == [100, 101, 102, 103]

            # Verify subregions
            assert len(elem_sub) == 1
            assert elem_sub[0] == 1

        finally:
            os.unlink(temp_file)

    def test_single_triangular_element(self):
        """Test reading single triangular element (node4=0)"""
        elements_data = [
            (1, 100, 101, 102, 0, 1)
        ]
        subregion_names = ["Subregion_1"]

        content = create_elements_file(1, 1, subregion_names, elements_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_elements import iwfm_read_elements

            elem_ids, elem_nodes, elem_sub = iwfm_read_elements(temp_file, verbose=False)

            # Verify triangular element has only 3 nodes (node4=0 is removed)
            assert elem_ids[0] == 1
            assert elem_nodes[0] == [100, 101, 102]
            assert elem_sub[0] == 1

        finally:
            os.unlink(temp_file)

    def test_multiple_quadrilateral_elements(self):
        """Test reading multiple quadrilateral elements"""
        elements_data = [
            (1, 100, 101, 102, 103, 1),
            (2, 110, 111, 112, 113, 1),
            (3, 120, 121, 122, 123, 2)
        ]
        subregion_names = ["Subregion_1", "Subregion_2"]

        content = create_elements_file(3, 2, subregion_names, elements_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_elements import iwfm_read_elements

            elem_ids, elem_nodes, elem_sub = iwfm_read_elements(temp_file, verbose=False)

            assert len(elem_ids) == 3
            assert elem_ids == [1, 2, 3]

            assert elem_nodes[0] == [100, 101, 102, 103]
            assert elem_nodes[1] == [110, 111, 112, 113]
            assert elem_nodes[2] == [120, 121, 122, 123]

            assert elem_sub == [1, 1, 2]

        finally:
            os.unlink(temp_file)

    def test_mixed_triangular_and_quadrilateral(self):
        """Test reading mix of triangular and quadrilateral elements"""
        elements_data = [
            (1, 100, 101, 102, 0, 1),      # Triangular
            (2, 110, 111, 112, 113, 1),    # Quadrilateral
            (3, 120, 121, 122, 0, 2),      # Triangular
            (4, 130, 131, 132, 133, 2)     # Quadrilateral
        ]
        subregion_names = ["Subregion_1", "Subregion_2"]

        content = create_elements_file(4, 2, subregion_names, elements_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_elements import iwfm_read_elements

            elem_ids, elem_nodes, elem_sub = iwfm_read_elements(temp_file, verbose=False)

            assert len(elem_ids) == 4

            # Verify triangular elements have 3 nodes
            assert elem_nodes[0] == [100, 101, 102]
            assert elem_nodes[2] == [120, 121, 122]

            # Verify quadrilateral elements have 4 nodes
            assert elem_nodes[1] == [110, 111, 112, 113]
            assert elem_nodes[3] == [130, 131, 132, 133]

            assert elem_sub == [1, 1, 2, 2]

        finally:
            os.unlink(temp_file)

    def test_multiple_subregions(self):
        """Test reading elements with multiple subregions"""
        elements_data = [
            (1, 100, 101, 102, 103, 1),
            (2, 110, 111, 112, 113, 2),
            (3, 120, 121, 122, 123, 3),
            (4, 130, 131, 132, 133, 4),
            (5, 140, 141, 142, 143, 5)
        ]
        subregion_names = ["Region_1", "Region_2", "Region_3", "Region_4", "Region_5"]

        content = create_elements_file(5, 5, subregion_names, elements_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_elements import iwfm_read_elements

            elem_ids, elem_nodes, elem_sub = iwfm_read_elements(temp_file, verbose=False)

            assert len(elem_ids) == 5
            assert elem_sub == [1, 2, 3, 4, 5]

        finally:
            os.unlink(temp_file)

    def test_non_sequential_element_ids(self):
        """Test reading elements with non-sequential IDs"""
        elements_data = [
            (5, 100, 101, 102, 103, 1),
            (10, 110, 111, 112, 113, 1),
            (15, 120, 121, 122, 123, 2)
        ]
        subregion_names = ["Subregion_1", "Subregion_2"]

        content = create_elements_file(3, 2, subregion_names, elements_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_elements import iwfm_read_elements

            elem_ids, elem_nodes, elem_sub = iwfm_read_elements(temp_file, verbose=False)

            assert elem_ids == [5, 10, 15]
            assert len(elem_nodes) == 3
            assert len(elem_sub) == 3

        finally:
            os.unlink(temp_file)

    def test_large_node_numbers(self):
        """Test reading elements with large node numbers"""
        elements_data = [
            (1, 1750, 1780, 1808, 1809, 1),
            (2, 1810, 1811, 1812, 1813, 2)
        ]
        subregion_names = ["Subregion_1", "Subregion_2"]

        content = create_elements_file(2, 2, subregion_names, elements_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_elements import iwfm_read_elements

            elem_ids, elem_nodes, elem_sub = iwfm_read_elements(temp_file, verbose=False)

            assert elem_nodes[0] == [1750, 1780, 1808, 1809]
            assert elem_nodes[1] == [1810, 1811, 1812, 1813]

        finally:
            os.unlink(temp_file)

    def test_verbose_mode(self, capsys):
        """Test verbose mode output"""
        elements_data = [
            (1, 100, 101, 102, 103, 1),
            (2, 110, 111, 112, 113, 1)
        ]
        subregion_names = ["Subregion_1"]

        content = create_elements_file(2, 1, subregion_names, elements_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_elements import iwfm_read_elements

            elem_ids, elem_nodes, elem_sub = iwfm_read_elements(temp_file, verbose=True)

            captured = capsys.readouterr()
            assert "Read 2 elements" in captured.out

        finally:
            os.unlink(temp_file)

    def test_comment_lines_skipped(self):
        """Test that comment lines are properly skipped"""
        content = "C IWFM Elements File\n"
        content += "C This is a comment\n"
        content += "c Another comment with lowercase c\n"
        content += "* Comment with asterisk\n"
        content += "# Comment with hash\n"
        content += "    2                           / NE\n"
        content += "C More comments\n"
        content += "    1                           / NSUBREGIONS\n"
        content += "C Subregion definitions\n"
        content += "    1    Subregion_1\n"
        content += "C Element data\n"
        content += "    1    100    101    102    103    1\n"
        content += "    2    110    111    112    113    1\n"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_elements import iwfm_read_elements

            elem_ids, elem_nodes, elem_sub = iwfm_read_elements(temp_file, verbose=False)

            # Should read correctly despite comment lines
            assert len(elem_ids) == 2
            assert elem_ids == [1, 2]
            assert elem_nodes[0] == [100, 101, 102, 103]
            assert elem_nodes[1] == [110, 111, 112, 113]

        finally:
            os.unlink(temp_file)

    def test_real_file_format(self):
        """Test with format matching real IWFM file"""
        elements_data = [
            (1, 1, 2, 7, 6, 1),
            (2, 2, 3, 8, 7, 1),
            (3, 3, 4, 9, 8, 1),
            (4, 4, 5, 10, 9, 1),
            (5, 6, 7, 12, 11, 1),
            (6, 7, 8, 13, 12, 1),
            (7, 11, 12, 19, 18, 2),
            (8, 12, 13, 20, 19, 2),
            (9, 18, 19, 26, 0, 2),     # Triangular
            (10, 19, 20, 27, 26, 2)
        ]
        subregion_names = ["Subregion_1", "Subregion_2"]

        content = create_elements_file(10, 2, subregion_names, elements_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_elements import iwfm_read_elements

            elem_ids, elem_nodes, elem_sub = iwfm_read_elements(temp_file, verbose=False)

            assert len(elem_ids) == 10
            assert elem_ids == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

            # Verify first element
            assert elem_nodes[0] == [1, 2, 7, 6]

            # Verify triangular element (element 9)
            assert elem_nodes[8] == [18, 19, 26]

            # Verify last element
            assert elem_nodes[9] == [19, 20, 27, 26]

            # Verify subregions
            assert elem_sub[:6] == [1, 1, 1, 1, 1, 1]
            assert elem_sub[6:] == [2, 2, 2, 2]

        finally:
            os.unlink(temp_file)

    def test_large_number_of_elements(self):
        """Test reading many elements"""
        # Create 100 elements
        elements_data = [(i+1, i*4, i*4+1, i*4+2, i*4+3, (i % 5) + 1) for i in range(100)]
        subregion_names = [f"Subregion_{i}" for i in range(1, 6)]

        content = create_elements_file(100, 5, subregion_names, elements_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_elements import iwfm_read_elements

            elem_ids, elem_nodes, elem_sub = iwfm_read_elements(temp_file, verbose=False)

            assert len(elem_ids) == 100
            assert len(elem_nodes) == 100
            assert len(elem_sub) == 100

            # Spot check a few elements
            assert elem_ids[0] == 1
            assert elem_ids[50] == 51
            assert elem_ids[99] == 100

            # Verify node connectivity
            assert elem_nodes[0] == [0, 1, 2, 3]
            assert elem_nodes[50] == [200, 201, 202, 203]

        finally:
            os.unlink(temp_file)


# -----------------------------------------------------------------------------
# Error-path tests
# -----------------------------------------------------------------------------

def test_iwfm_read_elements_missing_file_exits(tmp_path):
    """Calling with a nonexistent path bails out via iwfm.file_test() → sys.exit()."""
    import pytest
    from iwfm.iwfm_read_elements import iwfm_read_elements

    bogus = str(tmp_path / "does_not_exist.dat")
    with pytest.raises(SystemExit):
        iwfm_read_elements(bogus)


def test_iwfm_read_elements_empty_file_raises(tmp_path):
    """An empty (but existing) elements file fails the parser, not silently."""
    import pytest
    from iwfm.iwfm_read_elements import iwfm_read_elements

    empty = tmp_path / "empty.dat"
    empty.write_text("")
    # The parser raises IndexError when it tries to read the element count line
    # from an empty/all-comment file — assert that we don't silently succeed.
    with pytest.raises((IndexError, ValueError)):
        iwfm_read_elements(str(empty))
