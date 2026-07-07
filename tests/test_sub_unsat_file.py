# test_sub_unsat_file.py
# Tests for sub_unsat_file function
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
import os
import iwfm


def create_unsat_file_content():
    """Create mock unsaturated zone file content.

    Based on C2VSimCG_Unsat.dat format:
    - Comment lines start with 'C', 'c', '*', or '#'
    - Data lines start with whitespace
    - '/' marks end of record
    - First 9 data lines are factors/settings (NUNSAT, UZCONV, UZITERMX, etc.)
    - After that, element parameter lines with element ID in first column

    Structure required by skip_ahead in sub_unsat_file:
    - skip_ahead(0, lines, 9) = skip initial comments and 9 data lines (settings/factors)
    - Then process element lines, keeping those with IDs in elem_list
    """
    content = """#4.2
C Unsaturated zone parameter file
C
    2                                        / NUNSAT
    1e-8                                     / UZCONV
    150                                      / UZITERMX
    ..\\Results\\Unsat_Budget.hdf            / UZBUDFL
    ..\\Results\\Unsat_ZBudget.hdf           / UZZBUDFL
    ..\\Results\\Unsat_FinalCond.out         / UZFNFL
C
    0                                        / NGROUP
C
    1.0            1.0           1.0
C
    1MON                                     / TUNITZ
C Option 2 - element parameters
C IE   PD    PN     PI    PK    PRHC   PD    PN     PI    PK    PRHC
    1	21.10	0.11953	0.4	0.99997	1	21.10	0.11987	0.4	1.00010	1
    2	43.27	0.11627	0.4	0.99982	1	43.27	0.11938	0.4	1.00004	1
    3	58.10	0.10603	0.4	0.99828	1	58.10	0.11759	0.4	0.99807	1
    4	65.30	0.11495	0.4	0.99882	1	65.30	0.11885	0.4	0.99907	1
    5	34.98	0.11664	0.4	1.00002	1	34.98	0.11962	0.4	1.00001	1
"""
    return content


def create_unsat_file_simple():
    """Create simpler unsaturated zone file for basic testing.

    Minimal file with header/factors and element data lines.
    The function skips 9 data lines before processing element lines.
    """
    content = """#4.2
C Unsaturated zone file
    2                                        / NUNSAT
    1e-8                                     / UZCONV
    150                                      / UZITERMX
    ..\\Results\\Budget.hdf                  / UZBUDFL
    ..\\Results\\ZBudget.hdf                 / UZZBUDFL
    ..\\Results\\Final.out                   / UZFNFL
    0                                        / NGROUP
    1.0            1.0           1.0
    1MON                                     / TUNITZ
C Element parameters
    1	21.10	0.12	0.4	1.0	1	21.10	0.12	0.4	1.0	1
    2	43.27	0.12	0.4	1.0	1	43.27	0.12	0.4	1.0	1
    3	58.10	0.11	0.4	1.0	1	58.10	0.12	0.4	1.0	1
    4	65.30	0.11	0.4	1.0	1	65.30	0.12	0.4	1.0	1
    5	34.98	0.12	0.4	1.0	1	34.98	0.12	0.4	1.0	1
    6	66.10	0.11	0.4	1.0	1	66.10	0.12	0.4	1.0	1
"""
    return content


class TestSubUnsatFileBasic:
    """Basic functionality tests for sub_unsat_file."""

    def test_creates_output_file(self, tmp_path):
        """Test that output file is created."""
        input_file = tmp_path / 'old_unsat.dat'
        input_file.write_text(create_unsat_file_simple())
        output_file = tmp_path / 'new_unsat.dat'

        # elem_list is list of lists: [[elem_id], [elem_id], ...]
        elem_list = [[1], [2], [3], [4], [5], [6]]

        iwfm.sub_unsat_file(str(input_file), str(output_file), elem_list)

        assert os.path.exists(output_file)

    def test_returns_none(self, tmp_path):
        """Test that function returns None."""
        input_file = tmp_path / 'old_unsat.dat'
        input_file.write_text(create_unsat_file_simple())
        output_file = tmp_path / 'new_unsat.dat'

        elem_list = [[1], [2], [3], [4], [5], [6]]

        result = iwfm.sub_unsat_file(str(input_file), str(output_file), elem_list)

        assert result is None

    def test_preserves_version_tag(self, tmp_path):
        """Test that version tag is preserved."""
        input_file = tmp_path / 'old_unsat.dat'
        input_file.write_text(create_unsat_file_simple())
        output_file = tmp_path / 'new_unsat.dat'

        elem_list = [[1], [2], [3], [4], [5], [6]]

        iwfm.sub_unsat_file(str(input_file), str(output_file), elem_list)

        with open(output_file, 'r') as f:
            first_line = f.readline()

        assert '#4.2' in first_line

    def test_preserves_settings(self, tmp_path):
        """Test that settings/factors are preserved."""
        input_file = tmp_path / 'old_unsat.dat'
        input_file.write_text(create_unsat_file_simple())
        output_file = tmp_path / 'new_unsat.dat'

        elem_list = [[1], [2], [3], [4], [5], [6]]

        iwfm.sub_unsat_file(str(input_file), str(output_file), elem_list)

        with open(output_file, 'r') as f:
            content = f.read()

        # Check key settings are preserved
        assert 'NUNSAT' in content
        assert 'UZCONV' in content
        assert 'UZITERMX' in content
        assert 'NGROUP' in content
        assert 'TUNITZ' in content


class TestSubUnsatFileFiltering:
    """Tests for element filtering in sub_unsat_file."""

    def test_filters_elements_by_id(self, tmp_path):
        """Test that elements are filtered by ID."""
        input_file = tmp_path / 'old_unsat.dat'
        input_file.write_text(create_unsat_file_simple())
        output_file = tmp_path / 'new_unsat.dat'

        # Only include elements 1, 2, 3
        elem_list = [[1], [2], [3]]

        iwfm.sub_unsat_file(str(input_file), str(output_file), elem_list)

        with open(output_file, 'r') as f:
            content = f.read()

        # Count element data lines (many columns, no '/', first col is integer element ID)
        lines = content.split('\n')
        elem_count = 0
        for line in lines:
            stripped = line.strip()
            if stripped and stripped[0].isdigit() and '/' not in line:
                parts = stripped.split()
                # Element data lines have many columns (11 for 2 layers)
                if len(parts) >= 10:
                    elem_count += 1

        assert elem_count == 3

    def test_removes_elements_not_in_list(self, tmp_path):
        """Test that elements not in list are removed."""
        input_file = tmp_path / 'old_unsat.dat'
        input_file.write_text(create_unsat_file_simple())
        output_file = tmp_path / 'new_unsat.dat'

        # Only include elements 2, 4
        elem_list = [[2], [4]]

        iwfm.sub_unsat_file(str(input_file), str(output_file), elem_list)

        with open(output_file, 'r') as f:
            content = f.read()
            lines = content.split('\n')

        # Find element data lines (many columns, no '/')
        elem_ids_found = []
        for line in lines:
            stripped = line.strip()
            if stripped and stripped[0].isdigit() and '/' not in line:
                parts = stripped.split()
                # Element data lines have many columns (11 for 2 layers)
                if len(parts) >= 10:
                    elem_id = int(parts[0])
                    elem_ids_found.append(elem_id)

        assert 2 in elem_ids_found
        assert 4 in elem_ids_found
        assert 1 not in elem_ids_found
        assert 3 not in elem_ids_found
        assert 5 not in elem_ids_found
        assert 6 not in elem_ids_found

    def test_keeps_all_elements_when_all_in_list(self, tmp_path):
        """Test that all elements are kept when all are in list."""
        input_file = tmp_path / 'old_unsat.dat'
        input_file.write_text(create_unsat_file_simple())
        output_file = tmp_path / 'new_unsat.dat'

        # Include all elements
        elem_list = [[1], [2], [3], [4], [5], [6]]

        iwfm.sub_unsat_file(str(input_file), str(output_file), elem_list)

        with open(output_file, 'r') as f:
            content = f.read()
            lines = content.split('\n')

        # Count element data lines (many columns, no '/')
        elem_count = 0
        for line in lines:
            stripped = line.strip()
            if stripped and stripped[0].isdigit() and '/' not in line:
                parts = stripped.split()
                # Element data lines have many columns (11 for 2 layers)
                if len(parts) >= 10:
                    elem_count += 1

        assert elem_count == 6


class TestSubUnsatFileComments:
    """Tests for comment handling in sub_unsat_file."""

    def test_preserves_comment_lines(self, tmp_path):
        """Test that comment lines are preserved."""
        input_file = tmp_path / 'old_unsat.dat'
        input_file.write_text(create_unsat_file_simple())
        output_file = tmp_path / 'new_unsat.dat'

        elem_list = [[1], [2], [3]]

        iwfm.sub_unsat_file(str(input_file), str(output_file), elem_list)

        with open(output_file, 'r') as f:
            content = f.read()

        # Check that comment markers are still present
        assert 'C ' in content or 'C\n' in content

    def test_handles_different_comment_chars(self, tmp_path):
        """Test handling of different comment characters (C, c, *, #)."""
        content = """#4.2
C Comment with C
c Comment with c
* Comment with asterisk
# Comment with hash
    2                                        / NUNSAT
    1e-8                                     / UZCONV
    150                                      / UZITERMX
    ..\\Results\\Budget.hdf                  / UZBUDFL
    ..\\Results\\ZBudget.hdf                 / UZZBUDFL
    ..\\Results\\Final.out                   / UZFNFL
    0                                        / NGROUP
    1.0            1.0           1.0
    1MON                                     / TUNITZ
C Element data
    1	21.10	0.12	0.4	1.0	1	21.10	0.12	0.4	1.0	1
    2	43.27	0.12	0.4	1.0	1	43.27	0.12	0.4	1.0	1
"""
        input_file = tmp_path / 'old_unsat.dat'
        input_file.write_text(content)
        output_file = tmp_path / 'new_unsat.dat'

        elem_list = [[1], [2]]

        iwfm.sub_unsat_file(str(input_file), str(output_file), elem_list)

        with open(output_file, 'r') as f:
            result = f.read()

        # All comment styles should be preserved
        assert 'Comment with C' in result
        assert 'Comment with c' in result
        assert 'Comment with asterisk' in result
        assert 'Comment with hash' in result


class TestSubUnsatFileVerbose:
    """Tests for verbose output."""

    def test_verbose_output(self, tmp_path, capsys):
        """Test that verbose mode produces output."""
        input_file = tmp_path / 'old_unsat.dat'
        input_file.write_text(create_unsat_file_simple())
        output_file = tmp_path / 'new_unsat.dat'

        elem_list = [[1], [2], [3]]

        iwfm.sub_unsat_file(str(input_file), str(output_file), elem_list, verbose=True)

        captured = capsys.readouterr()
        assert 'Wrote unsaturated zone file' in captured.out
        assert str(output_file) in captured.out

    def test_no_verbose_output_by_default(self, tmp_path, capsys):
        """Test that no output is produced when verbose=False."""
        input_file = tmp_path / 'old_unsat.dat'
        input_file.write_text(create_unsat_file_simple())
        output_file = tmp_path / 'new_unsat.dat'

        elem_list = [[1], [2], [3]]

        iwfm.sub_unsat_file(str(input_file), str(output_file), elem_list, verbose=False)

        captured = capsys.readouterr()
        assert captured.out == ''


class TestSubUnsatFileNotFound:
    """Tests for file not found handling."""

    def test_missing_input_file_raises_error(self, tmp_path):
        """Test that missing input file raises FileNotFoundError."""
        output_file = tmp_path / 'new_unsat.dat'
        elem_list = [[1]]

        with pytest.raises(FileNotFoundError):
            iwfm.sub_unsat_file(str(tmp_path / 'nonexistent.dat'), str(output_file), elem_list)


class TestSubUnsatFileEdgeCases:
    """Edge case tests for sub_unsat_file."""

    def test_empty_elem_list(self, tmp_path):
        """Test with empty element list - removes all elements."""
        input_file = tmp_path / 'old_unsat.dat'
        input_file.write_text(create_unsat_file_simple())
        output_file = tmp_path / 'new_unsat.dat'

        # Empty element list
        elem_list = []

        iwfm.sub_unsat_file(str(input_file), str(output_file), elem_list)

        with open(output_file, 'r') as f:
            content = f.read()
            lines = content.split('\n')

        # No element data lines should remain
        elem_count = 0
        for line in lines:
            stripped = line.strip()
            if stripped and stripped[0].isdigit() and '/' not in line:
                parts = stripped.split()
                # Element data lines have many columns (11 for 2 layers)
                if len(parts) >= 10:
                    elem_count += 1

        assert elem_count == 0

    def test_single_element(self, tmp_path):
        """Test with single element."""
        input_file = tmp_path / 'old_unsat.dat'
        input_file.write_text(create_unsat_file_simple())
        output_file = tmp_path / 'new_unsat.dat'

        # Only element 3
        elem_list = [[3]]

        iwfm.sub_unsat_file(str(input_file), str(output_file), elem_list)

        with open(output_file, 'r') as f:
            content = f.read()
            lines = content.split('\n')

        # Find element data lines (many columns, no '/')
        elem_ids_found = []
        for line in lines:
            stripped = line.strip()
            if stripped and stripped[0].isdigit() and '/' not in line:
                parts = stripped.split()
                # Element data lines have many columns (11 for 2 layers)
                if len(parts) >= 10:
                    elem_id = int(parts[0])
                    elem_ids_found.append(elem_id)

        assert elem_ids_found == [3]

    def test_output_ends_with_newline(self, tmp_path):
        """Test that output file ends properly."""
        input_file = tmp_path / 'old_unsat.dat'
        input_file.write_text(create_unsat_file_simple())
        output_file = tmp_path / 'new_unsat.dat'

        elem_list = [[1], [2], [3]]

        iwfm.sub_unsat_file(str(input_file), str(output_file), elem_list)

        with open(output_file, 'r') as f:
            content = f.read()

        # Should end with newline(s)
        assert content.endswith('\n')

    def test_noncontiguous_elements(self, tmp_path):
        """Test with non-contiguous element IDs."""
        input_file = tmp_path / 'old_unsat.dat'
        input_file.write_text(create_unsat_file_simple())
        output_file = tmp_path / 'new_unsat.dat'

        # Non-contiguous: 1, 3, 5
        elem_list = [[1], [3], [5]]

        iwfm.sub_unsat_file(str(input_file), str(output_file), elem_list)

        with open(output_file, 'r') as f:
            content = f.read()
            lines = content.split('\n')

        # Find element data lines (many columns, no '/')
        elem_ids_found = []
        for line in lines:
            stripped = line.strip()
            if stripped and stripped[0].isdigit() and '/' not in line:
                parts = stripped.split()
                # Element data lines have many columns (11 for 2 layers)
                if len(parts) >= 10:
                    elem_id = int(parts[0])
                    elem_ids_found.append(elem_id)

        assert sorted(elem_ids_found) == [1, 3, 5]


class TestSubUnsatFileWithRealFile:
    """Tests using actual C2VSimCG_Unsat.dat file if available."""

    @pytest.fixture
    def real_unsat_file(self):
        """Return path to real unsaturated zone file if it exists and is readable."""
        real_file = '/Volumes/MinEx/Documents/Dropbox/work/Programing/repos/iwfm-py/iwfm-tests/C2VSimCG-2021/Simulation/C2VSimCG_Unsat.dat'
        if not os.path.exists(real_file):
            pytest.skip("Real C2VSimCG_Unsat.dat file not available")
        # Check if file is readable
        try:
            with open(real_file, 'r') as f:
                f.read()
        except UnicodeDecodeError:
            pytest.skip("Real file has encoding issues (non-UTF-8 characters)")
        return real_file

    def test_real_file_format_verification(self, real_unsat_file):
        """Test that real C2VSimCG unsaturated zone file has expected structure."""
        with open(real_unsat_file, 'r') as f:
            content = f.read()

        # Verify file has expected sections
        assert 'NUNSAT' in content
        assert 'UZCONV' in content
        assert 'NGROUP' in content

    def test_with_real_file(self, tmp_path, real_unsat_file):
        """Test sub_unsat_file with real unsaturated zone file."""
        output_file = tmp_path / 'new_unsat.dat'

        # Use some element IDs (first few elements from the model)
        elem_list = [[1], [2], [3], [4], [5], [6], [7], [8], [9], [10]]

        iwfm.sub_unsat_file(real_unsat_file, str(output_file), elem_list)

        assert os.path.exists(output_file)

        with open(output_file, 'r') as f:
            content = f.read()

        # Should have version tag
        assert '#4.2' in content
        # Should have NUNSAT marker
        assert 'NUNSAT' in content

    def test_real_file_filtering(self, tmp_path, real_unsat_file):
        """Test element filtering with real file."""
        output_file = tmp_path / 'new_unsat.dat'

        # Use only elements 1, 5, 10
        elem_list = [[1], [5], [10]]

        iwfm.sub_unsat_file(real_unsat_file, str(output_file), elem_list)

        with open(output_file, 'r') as f:
            content = f.read()
            lines = content.split('\n')

        # Count element data lines (after all settings, no / marker)
        elem_ids_found = []
        for line in lines:
            stripped = line.strip()
            if stripped and stripped[0].isdigit() and '/' not in line:
                parts = stripped.split()
                if len(parts) > 5:  # Element data has many columns
                    elem_id = int(parts[0])
                    elem_ids_found.append(elem_id)

        assert 1 in elem_ids_found
        assert 5 in elem_ids_found
        assert 10 in elem_ids_found
        assert len(elem_ids_found) == 3
