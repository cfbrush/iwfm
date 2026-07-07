#!/usr/bin/env python
# test_iwfm_read_lake.py
# Unit tests for iwfm_read_lake.py
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


def create_iwfm_lake_file(nlakes, lakes_data):
    """Create properly structured IWFM Preprocessor Lake file for testing.

    IWFM File Format Convention:
    - Comment lines start with 'C', 'c', '*', or '#' in column 1
    - Data lines MUST start with whitespace (space or tab)

    Parameters
    ----------
    nlakes : int
        Number of lakes
    lakes_data : list of tuples
        Each tuple: (lake_id, max_elev, dest, elements)
        elements: list of element IDs

    Returns
    -------
    str
        File contents
    """
    # Header comment (simplified from real file)
    content = "C IWFM Preprocessor Lake Configuration Data File\n"

    # Number of lakes - data line starts with whitespace
    content += f"     {nlakes}                          / NLAKE\n"
    content += "C\n"

    # Lake data - MUST start with whitespace per IWFM convention
    # Format: ID  MAX_ELEV  DST  NELAKE  IELAKE (first element on same line)
    for lake_id, max_elev, dest, elements in lakes_data:
        nelem = len(elements)
        # First line: lake properties and first element
        content += f"      {lake_id}       {max_elev}          {dest}         {nelem}            {elements[0]}\n"

        # Remaining elements (each on its own line with leading whitespace)
        for elem_id in elements[1:]:
            content += f"                                                 {elem_id}\n"

    return content


class TestIwfmReadLake:
    """Tests for iwfm_read_lake function"""

    def test_single_lake_single_element(self):
        """Test reading single lake with single element"""
        lakes_data = [
            (1, 515.0, 0, [100])  # Lake 1, max_elev=515, no dest, 1 element
        ]
        content = create_iwfm_lake_file(1, lakes_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_lake import iwfm_read_lake

            lake_elems, lakes = iwfm_read_lake(temp_file)

            # Verify one lake was read
            assert len(lakes) == 1
            assert len(lake_elems) == 1

            # Verify lake properties: [lake_id, max_elev, dest, nelem]
            assert lakes[0][0] == 1       # lake_id
            assert lakes[0][1] == 515.0   # max_elev
            assert lakes[0][2] == 0       # dest (no downstream)
            assert lakes[0][3] == 1       # nelem

            # Verify lake element: [lake_id, element_id]
            assert lake_elems[0][0] == 1    # lake_id
            assert lake_elems[0][1] == 100  # element_id

        finally:
            os.unlink(temp_file)

    def test_single_lake_multiple_elements(self):
        """Test reading single lake with multiple elements"""
        lakes_data = [
            (1, 443.7, 0, [2992, 2993, 2994, 2995, 2996])
        ]
        content = create_iwfm_lake_file(1, lakes_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_lake import iwfm_read_lake

            lake_elems, lakes = iwfm_read_lake(temp_file)

            # Verify one lake was read
            assert len(lakes) == 1
            assert len(lake_elems) == 5

            # Verify lake properties
            assert lakes[0][0] == 1       # lake_id
            assert lakes[0][1] == 443.7   # max_elev
            assert lakes[0][2] == 0       # dest
            assert lakes[0][3] == 5       # nelem

            # Verify all elements belong to lake 1
            for elem in lake_elems:
                assert elem[0] == 1  # All belong to lake 1

            # Verify element IDs
            assert lake_elems[0][1] == 2992
            assert lake_elems[1][1] == 2993
            assert lake_elems[2][1] == 2994
            assert lake_elems[3][1] == 2995
            assert lake_elems[4][1] == 2996

        finally:
            os.unlink(temp_file)

    def test_multiple_lakes(self):
        """Test reading multiple lakes"""
        lakes_data = [
            (1, 515.0, 2, [100, 101]),
            (2, 510.0, 0, [200, 201, 202]),
            (3, 520.0, 1, [300])
        ]
        content = create_iwfm_lake_file(3, lakes_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_lake import iwfm_read_lake

            lake_elems, lakes = iwfm_read_lake(temp_file)

            # Verify three lakes were read
            assert len(lakes) == 3
            assert len(lake_elems) == 6  # 2 + 3 + 1 elements

            # Verify lake 1
            assert lakes[0] == [1, 515.0, 2, 2]

            # Verify lake 2
            assert lakes[1] == [2, 510.0, 0, 3]

            # Verify lake 3
            assert lakes[2] == [3, 520.0, 1, 1]

            # Verify elements for lake 1
            lake1_elems = [e for e in lake_elems if e[0] == 1]
            assert len(lake1_elems) == 2
            assert lake1_elems[0][1] == 100
            assert lake1_elems[1][1] == 101

            # Verify elements for lake 2
            lake2_elems = [e for e in lake_elems if e[0] == 2]
            assert len(lake2_elems) == 3

            # Verify elements for lake 3
            lake3_elems = [e for e in lake_elems if e[0] == 3]
            assert len(lake3_elems) == 1

        finally:
            os.unlink(temp_file)

    def test_lake_with_stream_destination(self):
        """Test lake with destination to stream node"""
        # In IWFM, dest can be stream node ID (positive) or lake ID (negative)
        lakes_data = [
            (1, 520.0, 5, [100, 101])  # Lake 1 flows to stream node 5
        ]
        content = create_iwfm_lake_file(1, lakes_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_lake import iwfm_read_lake

            lake_elems, lakes = iwfm_read_lake(temp_file)

            # Verify destination
            assert lakes[0][2] == 5  # Stream node destination

        finally:
            os.unlink(temp_file)

    def test_different_max_elevations(self):
        """Test lakes with different maximum elevations"""
        lakes_data = [
            (1, 515.0, 0, [100]),
            (2, 520.5, 0, [200]),
            (3, 505.25, 0, [300])
        ]
        content = create_iwfm_lake_file(3, lakes_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_lake import iwfm_read_lake

            lake_elems, lakes = iwfm_read_lake(temp_file)

            # Verify different elevations
            assert lakes[0][1] == 515.0
            assert lakes[1][1] == 520.5
            assert lakes[2][1] == 505.25

        finally:
            os.unlink(temp_file)

    def test_comment_lines_skipped(self):
        """Test that comment lines are properly skipped"""
        # Create file with various comment formats
        content = "C Comment with C\n"
        content += "c Comment with lowercase c\n"
        content += "* Comment with asterisk\n"
        content += "# Comment with hash\n"
        content += "     2                          / NLAKE\n"
        content += "C More comments\n"
        content += "      1       515.0          0         2            100\n"
        content += "                                                 101\n"
        content += "      2       520.0          0         1            200\n"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_lake import iwfm_read_lake

            lake_elems, lakes = iwfm_read_lake(temp_file)

            # Verify data was read correctly despite comment lines
            assert len(lakes) == 2
            assert len(lake_elems) == 3
            assert lakes[0][0] == 1
            assert lakes[1][0] == 2

        finally:
            os.unlink(temp_file)

    def test_lake_element_correspondence(self):
        """Test that lake_elems and lakes correspond correctly"""
        lakes_data = [
            (1, 515.0, 0, [100, 101]),
            (2, 520.0, 0, [200, 201, 202])
        ]
        content = create_iwfm_lake_file(2, lakes_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_lake import iwfm_read_lake

            lake_elems, lakes = iwfm_read_lake(temp_file)

            # Verify lake 1 has correct number of elements
            lake1_count = lakes[0][3]  # nelem for lake 1
            lake1_elems = [e for e in lake_elems if e[0] == 1]
            assert len(lake1_elems) == lake1_count
            assert lake1_count == 2

            # Verify lake 2 has correct number of elements
            lake2_count = lakes[1][3]  # nelem for lake 2
            lake2_elems = [e for e in lake_elems if e[0] == 2]
            assert len(lake2_elems) == lake2_count
            assert lake2_count == 3

        finally:
            os.unlink(temp_file)

    def test_real_file_format(self):
        """Test with format matching real IWFM preprocessor file (Black Butte Lake)"""
        # Based on C2VSimFG_NSac_Lake_PP.dat
        elements = [
            2992, 2993, 2994, 2995, 2996, 2997, 2998, 2999,
            3064, 3065, 3066, 3067, 3068, 3069, 3070, 3071, 3072,
            3143, 3144, 3145, 3222, 3223, 3224,
            3297, 3298, 3299, 3300, 3372, 3373, 3374, 3444
        ]
        lakes_data = [
            (1, 0, 0, elements)  # Lake 1, max_elev column=0, dest=0, 31 elements
        ]
        content = create_iwfm_lake_file(1, lakes_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_lake import iwfm_read_lake

            lake_elems, lakes = iwfm_read_lake(temp_file)

            # Verify lake properties
            assert len(lakes) == 1
            assert lakes[0][0] == 1       # lake_id
            assert lakes[0][3] == 31      # nelem

            # Verify all 31 elements
            assert len(lake_elems) == 31

            # Verify first and last elements
            assert lake_elems[0][1] == 2992
            assert lake_elems[30][1] == 3444

            # All elements should belong to lake 1
            for elem in lake_elems:
                assert elem[0] == 1

        finally:
            os.unlink(temp_file)

    def test_non_sequential_lake_ids(self):
        """Test lakes with non-sequential IDs"""
        lakes_data = [
            (5, 515.0, 0, [100]),
            (10, 520.0, 0, [200]),
            (2, 525.0, 0, [300])
        ]
        content = create_iwfm_lake_file(3, lakes_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_lake import iwfm_read_lake

            lake_elems, lakes = iwfm_read_lake(temp_file)

            # Verify lake IDs are preserved
            assert lakes[0][0] == 5
            assert lakes[1][0] == 10
            assert lakes[2][0] == 2

            # Verify element associations
            assert lake_elems[0][0] == 5
            assert lake_elems[1][0] == 10
            assert lake_elems[2][0] == 2

        finally:
            os.unlink(temp_file)

    def test_zero_lakes(self):
        """Test file with zero lakes"""
        content = "C IWFM Preprocessor Lake Configuration Data File\n"
        content += "     0                          / NLAKE\n"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_lake import iwfm_read_lake

            lake_elems, lakes = iwfm_read_lake(temp_file)

            # Verify empty results
            assert len(lakes) == 0
            assert len(lake_elems) == 0

        finally:
            os.unlink(temp_file)

    def test_file_not_found(self):
        """Test error handling for non-existent file"""
        from iwfm.iwfm_read_lake import iwfm_read_lake

        with pytest.raises(FileNotFoundError):
            iwfm_read_lake('nonexistent_file.dat')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
