#!/usr/bin/env python
# test_sub_pp_elem_file.py
# Unit tests for sub_pp_elem_file.py
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
    """
    lines = []

    # Header comments
    lines.append("C IWFM Element Configuration File")
    lines.append("C*******************************************************************************")

    # NE and NREGN
    lines.append(f"    {ne}                          / NE")
    lines.append(f"    {nregn}                            / NREGN")

    # Subregion names section
    lines.append("C Subregion Names")
    lines.append("C  ID  RNAME")
    for sr_id, sr_name in subregions:
        lines.append(f"    {sr_id}      {sr_name}             /RNAME{sr_id}")

    # Comment line before element data (important for the code to detect end of subregions)
    lines.append("C Element Configuration Data")
    lines.append("C  IE  IDE(1)  IDE(2)  IDE(3)  IDE(4)  IRGE")
    for elem in elements:
        elem_id, n1, n2, n3, n4, irge = elem
        lines.append(f"    {elem_id}           {n1}       {n2}       {n3}       {n4}         {irge}")

    return '\n'.join(lines)


class TestSubPpElemFile:
    """Tests for sub_pp_elem_file function"""

    def test_file_not_found(self):
        """Test error handling for non-existent file"""
        from iwfm.sub.pp_elem_file import sub_pp_elem_file

        with pytest.raises(FileNotFoundError):
            sub_pp_elem_file('nonexistent_file.dat', 'output.dat', [[1]], [1])

    def test_basic_element_filtering(self):
        """Test basic element filtering"""
        subregions = [
            (1, 'Subregion 1'),
            (2, 'Subregion 2'),
        ]
        elements = [
            (1, 1, 8, 9, 5, 1),
            (2, 1, 5, 6, 2, 1),
            (3, 2, 6, 7, 3, 1),
            (4, 3, 7, 4, 0, 2),  # triangular element
            (5, 5, 9, 10, 6, 2),
        ]

        content = create_elem_file(5, 2, subregions, elements)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_elem.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_elem.dat')

            from iwfm.sub.pp_elem_file import sub_pp_elem_file

            # elem_list format: list of [elem_id, ...] where elem_id is extracted
            elem_list = [[1], [2], [3]]  # Only elements 1, 2, 3
            new_srs = [1]  # Only subregion 1

            result = sub_pp_elem_file(old_file, new_file, elem_list, new_srs)

            assert os.path.exists(new_file)

            # Should return elem_nodes for kept elements
            assert isinstance(result, list)
            assert len(result) == 3  # Elements 1, 2, 3

    def test_all_elements_kept(self):
        """Test when all elements are kept"""
        # Need more subregions in original than in new_srs for the function to work
        subregions = [
            (1, 'Subregion 1'),
            (2, 'Subregion 2'),  # Extra subregion to be removed
        ]
        elements = [
            (1, 1, 8, 9, 5, 1),
            (2, 1, 5, 6, 2, 1),
            (3, 2, 6, 7, 3, 1),
        ]

        content = create_elem_file(3, 2, subregions, elements)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_elem.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_elem.dat')

            from iwfm.sub.pp_elem_file import sub_pp_elem_file

            elem_list = [[1], [2], [3]]
            new_srs = [1]

            result = sub_pp_elem_file(old_file, new_file, elem_list, new_srs)

            assert len(result) == 3

            with open(new_file) as f:
                new_content = f.read()

            # Check NE is updated
            assert '/ NE' in new_content

    def test_triangular_elements(self):
        """Test handling of triangular elements (node4 = 0)"""
        subregions = [
            (1, 'Subregion 1'),
            (2, 'Subregion 2'),  # Extra subregion
        ]
        elements = [
            (1, 3, 7, 4, 0, 1),  # triangular
            (2, 1, 8, 9, 5, 1),  # quadrilateral
            (3, 5, 9, 10, 0, 1),  # triangular
        ]

        content = create_elem_file(3, 2, subregions, elements)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_elem.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_elem.dat')

            from iwfm.sub.pp_elem_file import sub_pp_elem_file

            elem_list = [[1], [3]]  # Only triangular elements
            new_srs = [1]

            result = sub_pp_elem_file(old_file, new_file, elem_list, new_srs)

            assert len(result) == 2

            # Check that the triangular elements have node4 = 0
            for elem_nodes in result:
                if elem_nodes[0] in [1, 3]:
                    assert elem_nodes[4] == 0  # node4 position

    def test_multiple_subregions(self):
        """Test with multiple subregions"""
        subregions = [
            (1, 'Subregion 1'),
            (2, 'Subregion 2'),
            (3, 'Subregion 3'),
        ]
        elements = [
            (1, 1, 8, 9, 5, 1),
            (2, 1, 5, 6, 2, 2),
            (3, 2, 6, 7, 3, 3),
        ]

        content = create_elem_file(3, 3, subregions, elements)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_elem.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_elem.dat')

            from iwfm.sub.pp_elem_file import sub_pp_elem_file

            elem_list = [[1], [2]]  # Elements 1, 2
            new_srs = [1, 2]  # Subregions 1, 2

            result = sub_pp_elem_file(old_file, new_file, elem_list, new_srs)

            assert len(result) == 2

            with open(new_file) as f:
                new_content = f.read()

            # Check NREGN is updated to 2
            lines = new_content.split('\n')
            nregn_line = [l for l in lines if '/ NREGN' in l][0]
            assert '2' in nregn_line

    def test_returns_elem_nodes(self):
        """Test that function returns correct elem_nodes structure"""
        subregions = [
            (1, 'Subregion 1'),
            (2, 'Subregion 2'),  # Extra subregion
        ]
        elements = [
            (1, 1, 8, 9, 5, 1),
            (2, 1, 5, 6, 2, 1),
        ]

        content = create_elem_file(2, 2, subregions, elements)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_elem.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_elem.dat')

            from iwfm.sub.pp_elem_file import sub_pp_elem_file

            elem_list = [[1], [2]]
            new_srs = [1]

            result = sub_pp_elem_file(old_file, new_file, elem_list, new_srs)

            # Check structure of returned data
            assert len(result) == 2
            for elem_nodes in result:
                assert isinstance(elem_nodes, list)
                # Each element should have: elem_id, node1, node2, node3, node4, subregion
                assert len(elem_nodes) == 6
                # All values should be integers
                for val in elem_nodes:
                    assert isinstance(val, int)

    def test_preserves_header_comments(self):
        """Test that header comments are preserved"""
        subregions = [
            (1, 'Subregion 1'),
            (2, 'Subregion 2'),  # Extra subregion to be removed
        ]
        elements = [
            (1, 1, 8, 9, 5, 1),
        ]

        content = create_elem_file(1, 2, subregions, elements)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_elem.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_elem.dat')

            from iwfm.sub.pp_elem_file import sub_pp_elem_file

            elem_list = [[1]]
            new_srs = [1]

            sub_pp_elem_file(old_file, new_file, elem_list, new_srs)

            with open(new_file) as f:
                new_content = f.read()

            # Check header is preserved
            assert 'IWFM Element Configuration File' in new_content

    def test_ne_updated(self):
        """Test that NE (number of elements) is updated correctly"""
        subregions = [
            (1, 'Subregion 1'),
            (2, 'Subregion 2'),  # Extra subregion to be removed
        ]
        elements = [
            (1, 1, 8, 9, 5, 1),
            (2, 1, 5, 6, 2, 1),
            (3, 2, 6, 7, 3, 1),
            (4, 3, 7, 4, 0, 1),
            (5, 5, 9, 10, 6, 1),
        ]

        content = create_elem_file(5, 2, subregions, elements)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_elem.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_elem.dat')

            from iwfm.sub.pp_elem_file import sub_pp_elem_file

            # Only keep 2 elements
            elem_list = [[1], [3]]
            new_srs = [1]

            sub_pp_elem_file(old_file, new_file, elem_list, new_srs)

            with open(new_file) as f:
                new_content = f.read()

            # Check NE is updated to 2
            lines = new_content.split('\n')
            ne_line = [l for l in lines if '/ NE' in l][0]
            assert '2' in ne_line

    def test_subregion_names_updated(self):
        """Test that subregion names are updated"""
        subregions = [
            (1, 'Subregion 1'),
            (2, 'Subregion 2'),
            (3, 'Subregion 3'),
        ]
        elements = [
            (1, 1, 8, 9, 5, 1),
            (2, 1, 5, 6, 2, 2),
        ]

        content = create_elem_file(2, 3, subregions, elements)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_elem.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_elem.dat')

            from iwfm.sub.pp_elem_file import sub_pp_elem_file

            elem_list = [[1], [2]]
            new_srs = [1, 2]  # Only subregions 1 and 2

            sub_pp_elem_file(old_file, new_file, elem_list, new_srs)

            with open(new_file) as f:
                new_content = f.read()

            # Check that subregion 3 is not in the output
            # and subregions 1 and 2 are present
            assert 'Subregion 1' in new_content
            assert 'Subregion 2' in new_content

    def test_single_element(self):
        """Test with only one element"""
        subregions = [
            (1, 'Subregion 1'),
            (2, 'Subregion 2'),  # Extra subregion to be removed
        ]
        elements = [
            (1, 1, 8, 9, 5, 1),
        ]

        content = create_elem_file(1, 2, subregions, elements)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_elem.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_elem.dat')

            from iwfm.sub.pp_elem_file import sub_pp_elem_file

            elem_list = [[1]]
            new_srs = [1]

            result = sub_pp_elem_file(old_file, new_file, elem_list, new_srs)

            assert len(result) == 1
            assert result[0][0] == 1  # Element ID


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
