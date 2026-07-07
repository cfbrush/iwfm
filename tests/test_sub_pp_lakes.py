#!/usr/bin/env python
# test_sub_pp_lakes.py
# Unit tests for sub_pp_lakes.py
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


def create_lake_file(nlake, lakes):
    """Create a lake configuration file for testing.

    Parameters
    ----------
    nlake : int
        Number of lakes
    lakes : list of tuples
        Each tuple: (lake_id, typdst, dst, nelake, lake_name, ielake_list)
        ielake_list is a list of element IDs

    Returns
    -------
    str
        File contents
    """
    lines = []

    # Header comments
    lines.append("C IWFM Lake Configuration Data File")
    lines.append("C*******************************************************************************")

    # NLAKE value
    lines.append(f"     {nlake}                          / NLAKE")

    # Comment before lake data
    lines.append("C Lake Data Section")
    lines.append("C     ID    TYPDST      DST       NELAKE        IELAKE")

    # Lake data
    for lake in lakes:
        lake_id, typdst, dst, nelake, lake_name, ielake_list = lake
        # First line with first element
        lines.append(f"      {lake_id}       {typdst}          {dst}         {nelake}            {ielake_list[0]} / {lake_name}")
        # Additional elements on subsequent lines
        for elem in ielake_list[1:]:
            lines.append(f"                                                 {elem}")

    return '\n'.join(lines)


class TestSubPpLakes:
    """Tests for sub_pp_lakes function"""

    def test_file_not_found(self):
        """Test error handling for non-existent file"""
        from iwfm.sub.pp_lakes import sub_pp_lakes

        with pytest.raises(FileNotFoundError):
            sub_pp_lakes('nonexistent_file.dat', [[1], [2], [3]])

    def test_single_lake_all_elements_in_submodel(self):
        """Test with single lake where all elements are in submodel"""
        lakes = [
            (1, 0, 0, 3, 'Test Lake', [100, 101, 102]),
        ]

        content = create_lake_file(1, lakes)

        with tempfile.TemporaryDirectory() as tmpdir:
            lake_file = os.path.join(tmpdir, 'lake.dat')
            with open(lake_file, 'w') as f:
                f.write(content)

            from iwfm.sub.pp_lakes import sub_pp_lakes

            # elem_list format: list of [elem_id, ...] where elem_id is extracted
            elem_list = [[100], [101], [102], [200], [201]]

            lake_info, have_lake = sub_pp_lakes(lake_file, elem_list)

            assert have_lake is True
            assert len(lake_info) == 1
            assert lake_info[0][0] == '1'  # lake ID
            assert lake_info[0][3] == '3'  # nelake (all 3 elements)
            assert lake_info[0][5] == [100, 101, 102]  # lake elements

    def test_single_lake_partial_elements_in_submodel(self):
        """Test with single lake where only some elements are in submodel"""
        lakes = [
            (1, 0, 0, 5, 'Test Lake', [100, 101, 102, 103, 104]),
        ]

        content = create_lake_file(1, lakes)

        with tempfile.TemporaryDirectory() as tmpdir:
            lake_file = os.path.join(tmpdir, 'lake.dat')
            with open(lake_file, 'w') as f:
                f.write(content)

            from iwfm.sub.pp_lakes import sub_pp_lakes

            # Only elements 100, 102 are in submodel
            elem_list = [[100], [102], [200], [201]]

            lake_info, have_lake = sub_pp_lakes(lake_file, elem_list)

            assert have_lake is True
            assert len(lake_info) == 1
            assert lake_info[0][3] == '2'  # nelake (only 2 elements in submodel)
            assert lake_info[0][5] == [100, 102]

    def test_single_lake_no_elements_in_submodel(self):
        """Test with single lake where no elements are in submodel"""
        lakes = [
            (1, 0, 0, 3, 'Test Lake', [100, 101, 102]),
        ]

        content = create_lake_file(1, lakes)

        with tempfile.TemporaryDirectory() as tmpdir:
            lake_file = os.path.join(tmpdir, 'lake.dat')
            with open(lake_file, 'w') as f:
                f.write(content)

            from iwfm.sub.pp_lakes import sub_pp_lakes

            # No lake elements in submodel
            elem_list = [[200], [201], [202]]

            lake_info, have_lake = sub_pp_lakes(lake_file, elem_list)

            assert have_lake is False
            assert len(lake_info) == 0

    def test_multiple_lakes_all_in_submodel(self):
        """Test with multiple lakes all in submodel"""
        lakes = [
            (1, 0, 0, 2, 'Lake One', [100, 101]),
            (2, 1, 5, 3, 'Lake Two', [200, 201, 202]),
        ]

        content = create_lake_file(2, lakes)

        with tempfile.TemporaryDirectory() as tmpdir:
            lake_file = os.path.join(tmpdir, 'lake.dat')
            with open(lake_file, 'w') as f:
                f.write(content)

            from iwfm.sub.pp_lakes import sub_pp_lakes

            # All lake elements in submodel
            elem_list = [[100], [101], [200], [201], [202], [300]]

            lake_info, have_lake = sub_pp_lakes(lake_file, elem_list)

            assert have_lake is True
            assert len(lake_info) == 2
            assert lake_info[0][5] == [100, 101]
            assert lake_info[1][5] == [200, 201, 202]

    def test_multiple_lakes_one_in_submodel(self):
        """Test with multiple lakes where only one is in submodel"""
        lakes = [
            (1, 0, 0, 2, 'Lake One', [100, 101]),
            (2, 1, 5, 3, 'Lake Two', [200, 201, 202]),
        ]

        content = create_lake_file(2, lakes)

        with tempfile.TemporaryDirectory() as tmpdir:
            lake_file = os.path.join(tmpdir, 'lake.dat')
            with open(lake_file, 'w') as f:
                f.write(content)

            from iwfm.sub.pp_lakes import sub_pp_lakes

            # Only lake 2 elements in submodel
            elem_list = [[200], [201], [202], [300]]

            lake_info, have_lake = sub_pp_lakes(lake_file, elem_list)

            assert have_lake is True
            assert len(lake_info) == 1
            assert lake_info[0][0] == '2'  # Lake Two ID
            assert lake_info[0][5] == [200, 201, 202]

    def test_multiple_lakes_none_in_submodel(self):
        """Test with multiple lakes where none are in submodel"""
        lakes = [
            (1, 0, 0, 2, 'Lake One', [100, 101]),
            (2, 1, 5, 3, 'Lake Two', [200, 201, 202]),
        ]

        content = create_lake_file(2, lakes)

        with tempfile.TemporaryDirectory() as tmpdir:
            lake_file = os.path.join(tmpdir, 'lake.dat')
            with open(lake_file, 'w') as f:
                f.write(content)

            from iwfm.sub.pp_lakes import sub_pp_lakes

            # No lake elements in submodel
            elem_list = [[300], [301], [302]]

            lake_info, have_lake = sub_pp_lakes(lake_file, elem_list)

            assert have_lake is False
            assert len(lake_info) == 0

    def test_lake_info_structure(self):
        """Test that lake_info has correct structure"""
        lakes = [
            (1, 0, 0, 2, 'Test Lake', [100, 101]),
        ]

        content = create_lake_file(1, lakes)

        with tempfile.TemporaryDirectory() as tmpdir:
            lake_file = os.path.join(tmpdir, 'lake.dat')
            with open(lake_file, 'w') as f:
                f.write(content)

            from iwfm.sub.pp_lakes import sub_pp_lakes

            elem_list = [[100], [101]]

            lake_info, have_lake = sub_pp_lakes(lake_file, elem_list)

            assert len(lake_info) == 1
            # Structure: [lake_id, typdst, dst, nelake_str, lake_name, [elem_ids]]
            assert len(lake_info[0]) == 6
            assert lake_info[0][0] == '1'  # lake_id
            assert lake_info[0][1] == '0'  # typdst
            assert lake_info[0][2] == '0'  # dst
            assert lake_info[0][3] == '2'  # nelake (as string)
            assert 'Test Lake' in lake_info[0][4]  # lake name
            assert isinstance(lake_info[0][5], list)  # elem_ids list

    def test_lake_outflow_to_stream(self):
        """Test lake with outflow to stream node (TYPDST=1)"""
        lakes = [
            (1, 1, 25, 2, 'Stream Lake', [100, 101]),
        ]

        content = create_lake_file(1, lakes)

        with tempfile.TemporaryDirectory() as tmpdir:
            lake_file = os.path.join(tmpdir, 'lake.dat')
            with open(lake_file, 'w') as f:
                f.write(content)

            from iwfm.sub.pp_lakes import sub_pp_lakes

            elem_list = [[100], [101]]

            lake_info, have_lake = sub_pp_lakes(lake_file, elem_list)

            assert have_lake is True
            assert lake_info[0][1] == '1'  # TYPDST
            assert lake_info[0][2] == '25'  # DST (stream node)

    def test_lake_outflow_to_lake(self):
        """Test lake with outflow to downstream lake (TYPDST=3)"""
        lakes = [
            (1, 3, 2, 2, 'Upper Lake', [100, 101]),
            (2, 0, 0, 2, 'Lower Lake', [200, 201]),
        ]

        content = create_lake_file(2, lakes)

        with tempfile.TemporaryDirectory() as tmpdir:
            lake_file = os.path.join(tmpdir, 'lake.dat')
            with open(lake_file, 'w') as f:
                f.write(content)

            from iwfm.sub.pp_lakes import sub_pp_lakes

            elem_list = [[100], [101], [200], [201]]

            lake_info, have_lake = sub_pp_lakes(lake_file, elem_list)

            assert have_lake is True
            assert len(lake_info) == 2
            assert lake_info[0][1] == '3'  # TYPDST for Upper Lake
            assert lake_info[0][2] == '2'  # DST (downstream lake ID)

    def test_no_lakes_in_file(self):
        """Test file with zero lakes"""
        content = "C IWFM Lake Configuration Data File\n"
        content += "C Comment line\n"
        content += "     0                          / NLAKE\n"

        with tempfile.TemporaryDirectory() as tmpdir:
            lake_file = os.path.join(tmpdir, 'lake.dat')
            with open(lake_file, 'w') as f:
                f.write(content)

            from iwfm.sub.pp_lakes import sub_pp_lakes

            elem_list = [[100], [101]]

            lake_info, have_lake = sub_pp_lakes(lake_file, elem_list)

            assert have_lake is False
            assert len(lake_info) == 0

    def test_lake_name_preserved(self):
        """Test that lake name is preserved in output"""
        lakes = [
            (1, 0, 0, 2, 'Black Butte Lake', [100, 101]),
        ]

        content = create_lake_file(1, lakes)

        with tempfile.TemporaryDirectory() as tmpdir:
            lake_file = os.path.join(tmpdir, 'lake.dat')
            with open(lake_file, 'w') as f:
                f.write(content)

            from iwfm.sub.pp_lakes import sub_pp_lakes

            elem_list = [[100], [101]]

            lake_info, have_lake = sub_pp_lakes(lake_file, elem_list)

            assert 'Black Butte Lake' in lake_info[0][4]

    def test_elem_list_with_extra_data(self):
        """Test that elem_list works when elements have additional data"""
        lakes = [
            (1, 0, 0, 2, 'Test Lake', [100, 101]),
        ]

        content = create_lake_file(1, lakes)

        with tempfile.TemporaryDirectory() as tmpdir:
            lake_file = os.path.join(tmpdir, 'lake.dat')
            with open(lake_file, 'w') as f:
                f.write(content)

            from iwfm.sub.pp_lakes import sub_pp_lakes

            # elem_list with extra data beyond elem_id
            elem_list = [[100, 1, 2, 3, 4, 5], [101, 1, 2, 3, 4, 5], [200, 1, 2, 3, 4, 5]]

            lake_info, have_lake = sub_pp_lakes(lake_file, elem_list)

            assert have_lake is True
            assert len(lake_info) == 1
            assert lake_info[0][5] == [100, 101]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
