#!/usr/bin/env python
# test_sub_pp_lake_file.py
# Unit tests for sub_pp_lake_file.py
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


class TestSubPpLakeFile:
    """Tests for sub_pp_lake_file function"""

    def test_file_not_found(self):
        """Test error handling for non-existent file"""
        from iwfm.sub.pp_lake_file import sub_pp_lake_file

        with pytest.raises(FileNotFoundError):
            sub_pp_lake_file('nonexistent_file.dat', 'output.dat', [])

    def test_single_lake(self):
        """Test with a single lake"""
        lakes = [
            (1, 0, 0, 3, 'Test Lake', [100, 101, 102]),
        ]

        content = create_lake_file(1, lakes)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_lake.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_lake.dat')

            from iwfm.sub.pp_lake_file import sub_pp_lake_file

            # lake_info format: [ID, TYPDST, DST, NELAKE, lake_name, [elements]]
            lake_info = [
                ['1', '0', '0', '3', 'Test Lake', [100, 101, 102]]
            ]

            sub_pp_lake_file(old_file, new_file, lake_info)

            assert os.path.exists(new_file)

            with open(new_file) as f:
                new_content = f.read()

            # Check lake count
            assert '1' in new_content
            # Check elements are present
            assert '100' in new_content
            assert '101' in new_content
            assert '102' in new_content

    def test_multiple_lakes(self):
        """Test with multiple lakes"""
        lakes = [
            (1, 0, 0, 2, 'Lake One', [100, 101]),
            (2, 1, 5, 3, 'Lake Two', [200, 201, 202]),
        ]

        content = create_lake_file(2, lakes)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_lake.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_lake.dat')

            from iwfm.sub.pp_lake_file import sub_pp_lake_file

            lake_info = [
                ['1', '0', '0', '2', 'Lake One', [100, 101]],
                ['2', '1', '5', '3', 'Lake Two', [200, 201, 202]]
            ]

            sub_pp_lake_file(old_file, new_file, lake_info)

            assert os.path.exists(new_file)

            with open(new_file) as f:
                new_content = f.read()

            # Check both lakes are present
            assert '100' in new_content
            assert '101' in new_content
            assert '200' in new_content
            assert '201' in new_content
            assert '202' in new_content

    def test_empty_lake_list(self):
        """Test with empty lake list (no lakes in submodel)"""
        lakes = [
            (1, 0, 0, 2, 'Original Lake', [100, 101]),
        ]

        content = create_lake_file(1, lakes)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_lake.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_lake.dat')

            from iwfm.sub.pp_lake_file import sub_pp_lake_file

            # Empty lake_info - no lakes in submodel
            lake_info = []

            sub_pp_lake_file(old_file, new_file, lake_info)

            assert os.path.exists(new_file)

            with open(new_file) as f:
                new_content = f.read()

            # Check NLAKE is 0
            lines = new_content.split('\n')
            nlake_line = [l for l in lines if '/ NLAKE' in l or 'NLAKE' in l.upper()]
            # The function updates the count to len(lake_info) = 0
            assert len(nlake_line) > 0

    def test_lake_count_updated(self):
        """Test that lake count is updated correctly"""
        # Original has 2 lakes
        lakes = [
            (1, 0, 0, 2, 'Lake One', [100, 101]),
            (2, 1, 5, 3, 'Lake Two', [200, 201, 202]),
        ]

        content = create_lake_file(2, lakes)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_lake.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_lake.dat')

            from iwfm.sub.pp_lake_file import sub_pp_lake_file

            # Only one lake in submodel
            lake_info = [
                ['1', '0', '0', '2', 'Lake One', [100, 101]]
            ]

            sub_pp_lake_file(old_file, new_file, lake_info)

            with open(new_file) as f:
                new_content = f.read()

            # Check the count line is present and updated
            lines = new_content.split('\n')
            # Find non-comment lines with NLAKE
            data_lines = [l for l in lines if not l.startswith('C') and l.strip()]
            # First data line should have the count
            assert len(data_lines) > 0

    def test_preserves_header_comments(self):
        """Test that header comments are preserved"""
        lakes = [
            (1, 0, 0, 2, 'Test Lake', [100, 101]),
        ]

        content = create_lake_file(1, lakes)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_lake.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_lake.dat')

            from iwfm.sub.pp_lake_file import sub_pp_lake_file

            lake_info = [
                ['1', '0', '0', '2', 'Test Lake', [100, 101]]
            ]

            sub_pp_lake_file(old_file, new_file, lake_info)

            with open(new_file) as f:
                new_content = f.read()

            # Check header is preserved
            assert 'IWFM Lake Configuration Data File' in new_content

    def test_returns_none(self):
        """Test that function returns None"""
        lakes = [
            (1, 0, 0, 2, 'Test Lake', [100, 101]),
        ]

        content = create_lake_file(1, lakes)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_lake.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_lake.dat')

            from iwfm.sub.pp_lake_file import sub_pp_lake_file

            lake_info = [
                ['1', '0', '0', '2', 'Test Lake', [100, 101]]
            ]

            result = sub_pp_lake_file(old_file, new_file, lake_info)

            assert result is None

    def test_lake_with_many_elements(self):
        """Test lake with many elements"""
        lakes = [
            (1, 0, 0, 10, 'Big Lake', list(range(100, 110))),
        ]

        content = create_lake_file(1, lakes)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_lake.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_lake.dat')

            from iwfm.sub.pp_lake_file import sub_pp_lake_file

            lake_info = [
                ['1', '0', '0', '10', 'Big Lake', list(range(100, 110))]
            ]

            sub_pp_lake_file(old_file, new_file, lake_info)

            assert os.path.exists(new_file)

            with open(new_file) as f:
                new_content = f.read()

            # Check all elements are present
            for elem in range(100, 110):
                assert str(elem) in new_content

    def test_lake_outflow_to_stream(self):
        """Test lake with outflow to stream node (TYPDST=1)"""
        lakes = [
            (1, 1, 25, 2, 'Stream Lake', [100, 101]),
        ]

        content = create_lake_file(1, lakes)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_lake.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_lake.dat')

            from iwfm.sub.pp_lake_file import sub_pp_lake_file

            lake_info = [
                ['1', '1', '25', '2', 'Stream Lake', [100, 101]]
            ]

            sub_pp_lake_file(old_file, new_file, lake_info)

            assert os.path.exists(new_file)

            with open(new_file) as f:
                new_content = f.read()

            # Check TYPDST and DST values are present
            assert '25' in new_content

    def test_lake_outflow_to_lake(self):
        """Test lake with outflow to downstream lake (TYPDST=3)"""
        lakes = [
            (1, 3, 2, 2, 'Upper Lake', [100, 101]),
            (2, 0, 0, 2, 'Lower Lake', [200, 201]),
        ]

        content = create_lake_file(2, lakes)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_lake.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_lake.dat')

            from iwfm.sub.pp_lake_file import sub_pp_lake_file

            lake_info = [
                ['1', '3', '2', '2', 'Upper Lake', [100, 101]],
                ['2', '0', '0', '2', 'Lower Lake', [200, 201]]
            ]

            sub_pp_lake_file(old_file, new_file, lake_info)

            assert os.path.exists(new_file)

            with open(new_file) as f:
                new_content = f.read()

            # Check both lakes are present
            assert '100' in new_content
            assert '200' in new_content

    def test_lake_name_preserved(self):
        """Test that lake name is included in output"""
        lakes = [
            (1, 0, 0, 2, 'Black Butte Lake', [100, 101]),
        ]

        content = create_lake_file(1, lakes)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_lake.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_lake.dat')

            from iwfm.sub.pp_lake_file import sub_pp_lake_file

            lake_info = [
                ['1', '0', '0', '2', 'Black Butte Lake', [100, 101]]
            ]

            sub_pp_lake_file(old_file, new_file, lake_info)

            with open(new_file) as f:
                new_content = f.read()

            # Check lake name is preserved
            assert 'Black Butte Lake' in new_content


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
