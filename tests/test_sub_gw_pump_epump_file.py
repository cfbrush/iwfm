#!/usr/bin/env python
# test_sub_gw_pump_epump_file.py
# Unit tests for sub_gw_pump_epump_file.py
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


def create_epump_file(nsink, pump_specs, ngrp, groups):
    """Create an element pumping file for testing.

    Parameters
    ----------
    nsink : int
        Number of element pumping specifications
    pump_specs : list of tuples
        Each tuple: (elem_id, icolsk, fracsk, ioptsk, fracskl1, fracskl2, fracskl3, fracskl4,
                     typdstsk, dstsk, icfirigsk, icadjsk)
    ngrp : int
        Number of element groups
    groups : list of tuples
        Each tuple: (grp_id, elem_list) where elem_list is a list of element IDs

    Returns
    -------
    str
        File contents
    """
    lines = []

    # Header comments
    lines.append("C IWFM Element Pumping Specification File")
    lines.append("C*******************************************************************************")

    # NSINK section
    lines.append(f"     {nsink}                       / NSINK")
    lines.append("C  ID  ICOLSK   FRACSK   IOPTSK   FRACSKL(1-4)   TYPDSTSK  DSTSK  ICFIRIGSK  ICADJSK")

    # Pumping specifications
    for spec in pump_specs:
        elem_id, icolsk, fracsk, ioptsk = spec[0], spec[1], spec[2], spec[3]
        fracskl1, fracskl2, fracskl3, fracskl4 = spec[4], spec[5], spec[6], spec[7]
        typdstsk, dstsk, icfirigsk, icadjsk = spec[8], spec[9], spec[10], spec[11]
        lines.append(f"    {elem_id}     {icolsk}     {fracsk}     {ioptsk}       "
                     f"{fracskl1}     {fracskl2}     {fracskl3}    {fracskl4}       "
                     f"{typdstsk}         {dstsk}       {icfirigsk}           {icadjsk}")

    # NGRP section
    lines.append("C Element Groups")
    lines.append(f"     {ngrp}                  / NGRP")
    lines.append("C    ID     NELEM    IELEM")

    # Element groups
    for grp_id, elem_list in groups:
        nelem = len(elem_list)
        # First line: grp_id, nelem, first_elem
        lines.append(f"     {grp_id}       {nelem}       {elem_list[0]}    / Group {grp_id}")
        # Continuation lines for remaining elements
        for i in range(1, nelem):
            lines.append(f"                     {elem_list[i]}")

    return '\n'.join(lines)


class TestSubGwPumpEpumpFile:
    """Tests for sub_gw_pump_epump_file function"""

    def test_file_not_found(self):
        """Test error handling for non-existent file"""
        from iwfm.sub.gw_pump_epump_file import sub_gw_pump_epump_file

        with pytest.raises(FileNotFoundError):
            sub_gw_pump_epump_file('nonexistent_file.dat', 'new_file.dat', [1, 2, 3])

    def test_basic_filtering(self):
        """Test basic element filtering"""
        # Create pumping specs for elements 1-5
        pump_specs = [
            (1, 1, 1.0, 3, 0.25, 0.25, 0.25, 0.25, -1, 0, 1, 3),
            (2, 1, 1.0, 3, 0.25, 0.25, 0.25, 0.25, -1, 0, 1, 3),
            (3, 1, 1.0, 3, 0.25, 0.25, 0.25, 0.25, -1, 0, 1, 3),
            (4, 1, 1.0, 3, 0.25, 0.25, 0.25, 0.25, -1, 0, 1, 3),
            (5, 1, 1.0, 3, 0.25, 0.25, 0.25, 0.25, -1, 0, 1, 3)
        ]

        content = create_epump_file(5, pump_specs, 0, [])

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_epump.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_epump.dat')

            from iwfm.sub.gw_pump_epump_file import sub_gw_pump_epump_file

            # Only keep elements 1, 3, 5
            result = sub_gw_pump_epump_file(old_file, new_file, [1, 3, 5])

            assert result is True  # Has wells
            assert os.path.exists(new_file)

            with open(new_file) as f:
                new_content = f.read()

            # Check NSINK was updated to 3
            assert '3' in new_content  # NSINK should be 3

    def test_all_elements_filtered(self):
        """Test when no elements match submodel"""
        pump_specs = [
            (1, 1, 1.0, 3, 0.25, 0.25, 0.25, 0.25, -1, 0, 1, 3),
            (2, 1, 1.0, 3, 0.25, 0.25, 0.25, 0.25, -1, 0, 1, 3),
            (3, 1, 1.0, 3, 0.25, 0.25, 0.25, 0.25, -1, 0, 1, 3)
        ]

        content = create_epump_file(3, pump_specs, 0, [])

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_epump.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_epump.dat')

            from iwfm.sub.gw_pump_epump_file import sub_gw_pump_epump_file

            # Elements 10, 20, 30 are not in the file
            result = sub_gw_pump_epump_file(old_file, new_file, [10, 20, 30])

            assert result is False  # No wells remaining
            assert os.path.exists(new_file)

            with open(new_file) as f:
                new_content = f.read()

            # NSINK should be 0
            assert '0                       / NSINK' in new_content

    def test_with_element_groups(self):
        """Test filtering with element groups"""
        pump_specs = [
            (1, 1, 1.0, 3, 0.25, 0.25, 0.25, 0.25, -1, 0, 1, 3),
            (2, 1, 1.0, 3, 0.25, 0.25, 0.25, 0.25, -1, 0, 1, 3),
            (3, 1, 1.0, 3, 0.25, 0.25, 0.25, 0.25, -1, 0, 1, 3),
            (4, 1, 1.0, 3, 0.25, 0.25, 0.25, 0.25, -1, 0, 1, 3)
        ]

        # Two groups
        groups = [
            (1, [1, 2, 3]),      # Group 1 has elements 1, 2, 3
            (2, [4, 5, 6, 7])    # Group 2 has elements 4, 5, 6, 7
        ]

        content = create_epump_file(4, pump_specs, 2, groups)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_epump.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_epump.dat')

            from iwfm.sub.gw_pump_epump_file import sub_gw_pump_epump_file

            # Only elements 1, 2, 4 are in submodel
            result = sub_gw_pump_epump_file(old_file, new_file, [1, 2, 4])

            assert result is True
            assert os.path.exists(new_file)

            with open(new_file) as f:
                new_content = f.read()

            # Group 1 should have 2 elements (1, 2), Group 2 should have 1 element (4)
            assert '2                  / NGRP' in new_content

    def test_group_completely_filtered(self):
        """Test when an entire group is filtered out"""
        pump_specs = [
            (1, 1, 1.0, 3, 0.25, 0.25, 0.25, 0.25, -1, 0, 1, 3),
            (2, 1, 1.0, 3, 0.25, 0.25, 0.25, 0.25, -1, 0, 1, 3)
        ]

        groups = [
            (1, [1, 2]),        # Group 1 has elements 1, 2
            (2, [10, 20, 30])   # Group 2 has elements 10, 20, 30 (not in submodel)
        ]

        content = create_epump_file(2, pump_specs, 2, groups)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_epump.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_epump.dat')

            from iwfm.sub.gw_pump_epump_file import sub_gw_pump_epump_file

            # Only elements 1, 2 are in submodel (group 2 completely filtered)
            result = sub_gw_pump_epump_file(old_file, new_file, [1, 2])

            assert result is True
            assert os.path.exists(new_file)

            with open(new_file) as f:
                new_content = f.read()

            # Only 1 group should remain
            assert '1                  / NGRP' in new_content

    def test_no_groups(self):
        """Test file with no element groups (NGRP = 0)"""
        pump_specs = [
            (1, 1, 1.0, 3, 0.25, 0.25, 0.25, 0.25, -1, 0, 1, 3),
            (2, 1, 1.0, 3, 0.25, 0.25, 0.25, 0.25, -1, 0, 1, 3)
        ]

        content = create_epump_file(2, pump_specs, 0, [])

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_epump.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_epump.dat')

            from iwfm.sub.gw_pump_epump_file import sub_gw_pump_epump_file

            result = sub_gw_pump_epump_file(old_file, new_file, [1, 2])

            assert result is True
            assert os.path.exists(new_file)

            with open(new_file) as f:
                new_content = f.read()

            assert '0                  / NGRP' in new_content

    def test_verbose_mode(self):
        """Test that verbose mode runs without error"""
        pump_specs = [
            (1, 1, 1.0, 3, 0.25, 0.25, 0.25, 0.25, -1, 0, 1, 3),
            (2, 1, 1.0, 3, 0.25, 0.25, 0.25, 0.25, -1, 0, 1, 3)
        ]

        content = create_epump_file(2, pump_specs, 0, [])

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_epump.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_epump.dat')

            from iwfm.sub.gw_pump_epump_file import sub_gw_pump_epump_file

            # Should not raise an error with verbose=True
            result = sub_gw_pump_epump_file(old_file, new_file, [1, 2], verbose=True)

            assert result is True
            assert os.path.exists(new_file)

    def test_return_value_true(self):
        """Test that function returns True when wells remain"""
        pump_specs = [
            (1, 1, 1.0, 3, 0.25, 0.25, 0.25, 0.25, -1, 0, 1, 3)
        ]

        content = create_epump_file(1, pump_specs, 0, [])

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_epump.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_epump.dat')

            from iwfm.sub.gw_pump_epump_file import sub_gw_pump_epump_file

            result = sub_gw_pump_epump_file(old_file, new_file, [1])

            assert result is True

    def test_return_value_false(self):
        """Test that function returns False when no wells remain"""
        pump_specs = [
            (1, 1, 1.0, 3, 0.25, 0.25, 0.25, 0.25, -1, 0, 1, 3)
        ]

        content = create_epump_file(1, pump_specs, 0, [])

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_epump.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_epump.dat')

            from iwfm.sub.gw_pump_epump_file import sub_gw_pump_epump_file

            # Element 100 is not in the file
            result = sub_gw_pump_epump_file(old_file, new_file, [100])

            assert result is False

    def test_preserves_comments(self):
        """Test that header comments are preserved in output"""
        pump_specs = [
            (1, 1, 1.0, 3, 0.25, 0.25, 0.25, 0.25, -1, 0, 1, 3)
        ]

        content = create_epump_file(1, pump_specs, 0, [])

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_epump.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_epump.dat')

            from iwfm.sub.gw_pump_epump_file import sub_gw_pump_epump_file

            sub_gw_pump_epump_file(old_file, new_file, [1])

            with open(new_file) as f:
                new_content = f.read()

            # Check header is preserved
            assert 'IWFM Element Pumping Specification File' in new_content

    def test_large_element_ids(self):
        """Test with large element IDs (like in real files)"""
        pump_specs = [
            (1336, 1, 1.0, 3, 0.25, 0.25, 0.25, 0.25, -1, 0, 1, 3),
            (1349, 1, 1.0, 3, 0.25, 0.25, 0.25, 0.25, -1, 0, 1, 3),
            (1358, 1, 1.0, 3, 0.25, 0.25, 0.25, 0.25, -1, 0, 1, 3),
            (1359, 1, 1.0, 3, 0.25, 0.25, 0.25, 0.25, -1, 0, 1, 3)
        ]

        # Group with large element IDs (like Arvin-Edison WSD in real file)
        groups = [
            (1, [1336, 1349, 1358, 1359])
        ]

        content = create_epump_file(4, pump_specs, 1, groups)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_epump.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_epump.dat')

            from iwfm.sub.gw_pump_epump_file import sub_gw_pump_epump_file

            # Only elements 1336, 1358 in submodel
            result = sub_gw_pump_epump_file(old_file, new_file, [1336, 1358])

            assert result is True
            assert os.path.exists(new_file)

            with open(new_file) as f:
                new_content = f.read()

            # NSINK should be 2
            assert '2                       / NSINK' in new_content
            # Group should have 2 elements
            assert '1336' in new_content
            assert '1358' in new_content

    def test_multiple_groups_partial_filtering(self):
        """Test with multiple groups where some elements are filtered from each"""
        pump_specs = [
            (1, 1, 1.0, 3, 0.25, 0.25, 0.25, 0.25, -1, 0, 1, 3),
            (2, 1, 1.0, 3, 0.25, 0.25, 0.25, 0.25, -1, 0, 1, 3),
            (3, 1, 1.0, 3, 0.25, 0.25, 0.25, 0.25, -1, 0, 1, 3),
            (4, 1, 1.0, 3, 0.25, 0.25, 0.25, 0.25, -1, 0, 1, 3),
            (5, 1, 1.0, 3, 0.25, 0.25, 0.25, 0.25, -1, 0, 1, 3),
            (6, 1, 1.0, 3, 0.25, 0.25, 0.25, 0.25, -1, 0, 1, 3)
        ]

        groups = [
            (1, [1, 2, 3]),      # Keep 1, 3
            (2, [4, 5]),         # Keep 5
            (3, [6, 7, 8, 9])    # Keep 6 only
        ]

        content = create_epump_file(6, pump_specs, 3, groups)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_epump.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_epump.dat')

            from iwfm.sub.gw_pump_epump_file import sub_gw_pump_epump_file

            # Submodel elements
            result = sub_gw_pump_epump_file(old_file, new_file, [1, 3, 5, 6])

            assert result is True

            with open(new_file) as f:
                new_content = f.read()

            # All 3 groups should remain (each has at least 1 element)
            assert '3                  / NGRP' in new_content


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
