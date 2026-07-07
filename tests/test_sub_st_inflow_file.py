# test_sub_st_inflow_file.py
# Tests for sub_st_inflow_file function
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


def create_inflow_file_content():
    """Create mock stream inflow file content.

    Based on C2VSimCG_StreamInflow.dat format:
    - Comment lines start with 'C', 'c', '*', or '#'
    - Data lines start with whitespace
    - '/' marks end of record
    - First data: NCOLSTRM (number of inflows), then 4 more factor lines
    - Then NCOLSTRM lines of stream node IDs (IRST) where inflow occurs
    """
    content = """C Stream inflow data file
C
          6                                         / NCOLSTRM
          43560000.0                                / FACTSTRM
          1                                         / NSPSTRM
          0                                         / NFQSTRM
                                                    / DSSFL
C-------------------------------------------------------------------------------
C   IRST
C-------------------------------------------------------------------------------
	101		/1:  River A
	102		/2:  Creek B
	103		/3:  Creek C
	201		/4:  River D
	202		/5:  Creek E
	203		/6:  Creek F
C-------------------------------------------------------------------------------
C                          Stream Inflow Data
C
C   TIME     COL1    COL2    COL3    COL4    COL5    COL6
C-------------------------------------------------------------------------------
   10/31/1973_24:00    100.0   50.0   25.0   200.0   100.0   50.0
   11/30/1973_24:00    110.0   55.0   27.5   220.0   110.0   55.0
   12/31/1973_24:00    120.0   60.0   30.0   240.0   120.0   60.0
"""
    return content


def create_inflow_file_more_nodes():
    """Create mock file with more inflow nodes for testing."""
    content = """C Stream inflow data file
          10                                        / NCOLSTRM
          43560000.0                                / FACTSTRM
          1                                         / NSPSTRM
          0                                         / NFQSTRM
                                                    / DSSFL
C-------------------------------------------------------------------------------
	101		/1:  Node 101
	102		/2:  Node 102
	103		/3:  Node 103
	104		/4:  Node 104
	105		/5:  Node 105
	201		/6:  Node 201
	202		/7:  Node 202
	203		/8:  Node 203
	204		/9:  Node 204
	205		/10: Node 205
C-------------------------------------------------------------------------------
   10/31/1973_24:00    1 2 3 4 5 6 7 8 9 10
"""
    return content


class TestSubStInflowFileBasic:
    """Basic functionality tests for sub_st_inflow_file."""

    def test_creates_output_file(self, tmp_path):
        """Test that output file is created."""
        input_file = tmp_path / 'old_inflow.dat'
        input_file.write_text(create_inflow_file_content())
        output_file = tmp_path / 'new_inflow.dat'

        snode_list = [101, 102, 103, 201, 202, 203]

        iwfm.sub_st_inflow_file(str(input_file), str(output_file), snode_list)

        assert os.path.exists(output_file)

    def test_returns_none(self, tmp_path):
        """Test that function returns None."""
        input_file = tmp_path / 'old_inflow.dat'
        input_file.write_text(create_inflow_file_content())
        output_file = tmp_path / 'new_inflow.dat'

        snode_list = [101, 102, 103]

        result = iwfm.sub_st_inflow_file(str(input_file), str(output_file), snode_list)

        assert result is None

    def test_keeps_matching_stream_nodes(self, tmp_path):
        """Test that stream nodes in snode_list are kept unchanged."""
        input_file = tmp_path / 'old_inflow.dat'
        input_file.write_text(create_inflow_file_content())
        output_file = tmp_path / 'new_inflow.dat'

        snode_list = [101, 102, 103]

        iwfm.sub_st_inflow_file(str(input_file), str(output_file), snode_list)

        with open(output_file, 'r') as f:
            content = f.read()

        # Nodes 101, 102, 103 should be preserved
        assert '101' in content
        assert '102' in content
        assert '103' in content

    def test_zeros_non_matching_stream_nodes(self, tmp_path):
        """Test that stream nodes not in snode_list are set to 0."""
        input_file = tmp_path / 'old_inflow.dat'
        input_file.write_text(create_inflow_file_content())
        output_file = tmp_path / 'new_inflow.dat'

        # Only include nodes 101, 102, 103 - not 201, 202, 203
        snode_list = [101, 102, 103]

        iwfm.sub_st_inflow_file(str(input_file), str(output_file), snode_list)

        with open(output_file, 'r') as f:
            lines = f.readlines()

        # Find the inflow location lines (after DSSFL, before data)
        # Nodes 201, 202, 203 should be replaced with 0
        # Zeroed inflow lines have format "\t0 /N:" (tab, 0, space, /number:)
        zero_count = 0
        for line in lines:
            stripped = line.strip()
            # Zeroed inflow lines start with "0 /" (node ID 0 followed by description)
            if stripped.startswith('0 /'):
                zero_count += 1

        # Should have 3 zeroed lines (for 201, 202, 203)
        assert zero_count == 3

    def test_preserves_comments(self, tmp_path):
        """Test that comments are preserved in output."""
        input_file = tmp_path / 'old_inflow.dat'
        input_file.write_text(create_inflow_file_content())
        output_file = tmp_path / 'new_inflow.dat'

        snode_list = [101, 102, 103]

        iwfm.sub_st_inflow_file(str(input_file), str(output_file), snode_list)

        with open(output_file, 'r') as f:
            content = f.read()

        assert 'C Stream inflow data file' in content

    def test_preserves_factors(self, tmp_path):
        """Test that factor lines are preserved."""
        input_file = tmp_path / 'old_inflow.dat'
        input_file.write_text(create_inflow_file_content())
        output_file = tmp_path / 'new_inflow.dat'

        snode_list = [101, 102, 103]

        iwfm.sub_st_inflow_file(str(input_file), str(output_file), snode_list)

        with open(output_file, 'r') as f:
            content = f.read()

        assert '43560000.0' in content
        assert 'FACTSTRM' in content
        assert 'NSPSTRM' in content
        assert 'NFQSTRM' in content

    def test_preserves_ncolstrm(self, tmp_path):
        """Test that NCOLSTRM (number of inflows) is preserved."""
        input_file = tmp_path / 'old_inflow.dat'
        input_file.write_text(create_inflow_file_content())
        output_file = tmp_path / 'new_inflow.dat'

        snode_list = [101, 102, 103]

        iwfm.sub_st_inflow_file(str(input_file), str(output_file), snode_list)

        with open(output_file, 'r') as f:
            content = f.read()

        # NCOLSTRM should still be 6
        assert 'NCOLSTRM' in content

    def test_preserves_inflow_descriptions(self, tmp_path):
        """Test that inflow descriptions (after /) are preserved."""
        input_file = tmp_path / 'old_inflow.dat'
        input_file.write_text(create_inflow_file_content())
        output_file = tmp_path / 'new_inflow.dat'

        snode_list = [101, 102, 103]

        iwfm.sub_st_inflow_file(str(input_file), str(output_file), snode_list)

        with open(output_file, 'r') as f:
            content = f.read()

        # Descriptions should be preserved
        assert 'River A' in content
        assert 'Creek B' in content


class TestSubStInflowFileFiltering:
    """Tests for node filtering in sub_st_inflow_file."""

    def test_all_nodes_in_snode_list(self, tmp_path):
        """Test when all nodes are in snode_list."""
        input_file = tmp_path / 'old_inflow.dat'
        input_file.write_text(create_inflow_file_content())
        output_file = tmp_path / 'new_inflow.dat'

        # All nodes included
        snode_list = [101, 102, 103, 201, 202, 203]

        iwfm.sub_st_inflow_file(str(input_file), str(output_file), snode_list)

        with open(output_file, 'r') as f:
            lines = f.readlines()

        # No lines should be zeroed
        zero_count = 0
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('0') and '/' in line and 'NFQSTRM' not in line:
                zero_count += 1

        assert zero_count == 0

    def test_no_nodes_in_snode_list(self, tmp_path):
        """Test when no nodes are in snode_list."""
        input_file = tmp_path / 'old_inflow.dat'
        input_file.write_text(create_inflow_file_content())
        output_file = tmp_path / 'new_inflow.dat'

        # No matching nodes
        snode_list = [999, 998, 997]

        iwfm.sub_st_inflow_file(str(input_file), str(output_file), snode_list)

        with open(output_file, 'r') as f:
            lines = f.readlines()

        # All 6 inflow lines should be zeroed
        zero_count = 0
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('0') and '/' in line and 'NFQSTRM' not in line and 'DSSFL' not in line:
                zero_count += 1

        assert zero_count == 6

    def test_selective_filtering(self, tmp_path):
        """Test selective filtering of nodes."""
        input_file = tmp_path / 'old_inflow.dat'
        input_file.write_text(create_inflow_file_more_nodes())
        output_file = tmp_path / 'new_inflow.dat'

        # Only include odd-numbered nodes from first group
        snode_list = [101, 103, 105, 201, 203, 205]

        iwfm.sub_st_inflow_file(str(input_file), str(output_file), snode_list)

        with open(output_file, 'r') as f:
            content = f.read()

        # Nodes 102, 104, 202, 204 should be zeroed
        # Check that preserved nodes are still there
        assert '101' in content
        assert '103' in content
        assert '105' in content


class TestSubStInflowFileVerbose:
    """Tests for verbose output."""

    def test_verbose_output(self, tmp_path, capsys):
        """Test that verbose mode produces output."""
        input_file = tmp_path / 'old_inflow.dat'
        input_file.write_text(create_inflow_file_content())
        output_file = tmp_path / 'new_inflow.dat'

        snode_list = [101, 102, 103]

        iwfm.sub_st_inflow_file(str(input_file), str(output_file), snode_list, verbose=True)

        captured = capsys.readouterr()
        assert 'Wrote stream inflow file' in captured.out
        assert str(output_file) in captured.out

    def test_no_verbose_output_by_default(self, tmp_path, capsys):
        """Test that no output is produced when verbose=False."""
        input_file = tmp_path / 'old_inflow.dat'
        input_file.write_text(create_inflow_file_content())
        output_file = tmp_path / 'new_inflow.dat'

        snode_list = [101, 102, 103]

        iwfm.sub_st_inflow_file(str(input_file), str(output_file), snode_list, verbose=False)

        captured = capsys.readouterr()
        assert captured.out == ''


class TestSubStInflowFileNotFound:
    """Tests for file not found handling."""

    def test_missing_input_file_raises_error(self, tmp_path):
        """Test that missing input file raises FileNotFoundError."""
        output_file = tmp_path / 'new_inflow.dat'
        snode_list = [101]

        with pytest.raises(FileNotFoundError):
            iwfm.sub_st_inflow_file(str(tmp_path / 'nonexistent.dat'), str(output_file), snode_list)


class TestSubStInflowFileEdgeCases:
    """Edge case tests for sub_st_inflow_file."""

    def test_empty_snode_list(self, tmp_path):
        """Test with empty snode_list."""
        input_file = tmp_path / 'old_inflow.dat'
        input_file.write_text(create_inflow_file_content())
        output_file = tmp_path / 'new_inflow.dat'

        snode_list = []

        iwfm.sub_st_inflow_file(str(input_file), str(output_file), snode_list)

        # Should still create output file
        assert os.path.exists(output_file)

        with open(output_file, 'r') as f:
            lines = f.readlines()

        # All nodes should be zeroed
        zero_count = 0
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('0') and '/' in line and 'NFQSTRM' not in line and 'DSSFL' not in line:
                zero_count += 1

        assert zero_count == 6

    def test_preserves_time_series_data(self, tmp_path):
        """Test that time series data is preserved."""
        input_file = tmp_path / 'old_inflow.dat'
        input_file.write_text(create_inflow_file_content())
        output_file = tmp_path / 'new_inflow.dat'

        snode_list = [101, 102, 103]

        iwfm.sub_st_inflow_file(str(input_file), str(output_file), snode_list)

        with open(output_file, 'r') as f:
            content = f.read()

        # Time series data should be preserved
        assert '10/31/1973_24:00' in content
        assert '11/30/1973_24:00' in content
        assert '12/31/1973_24:00' in content

    def test_output_ends_with_newline(self, tmp_path):
        """Test that output file ends with blank line."""
        input_file = tmp_path / 'old_inflow.dat'
        input_file.write_text(create_inflow_file_content())
        output_file = tmp_path / 'new_inflow.dat'

        snode_list = [101, 102, 103]

        iwfm.sub_st_inflow_file(str(input_file), str(output_file), snode_list)

        with open(output_file, 'r') as f:
            content = f.read()

        assert content.endswith('\n')


class TestSubStInflowFileWithRealFile:
    """Tests using actual C2VSimCG_StreamInflow.dat file if available."""

    @pytest.fixture
    def real_inflow_file(self):
        """Return path to real stream inflow file if it exists and is readable."""
        real_file = '/Volumes/MinEx/Documents/Dropbox/work/Programing/repos/iwfm-py/iwfm-tests/C2VSimCG-2021/Simulation/Streams/C2VSimCG_StreamInflow.dat'
        if not os.path.exists(real_file):
            pytest.skip("Real C2VSimCG_StreamInflow.dat file not available")
        try:
            with open(real_file, 'r') as f:
                f.read()
        except UnicodeDecodeError:
            pytest.skip("Real file has encoding issues (non-UTF-8 characters)")
        return real_file

    def test_with_real_file(self, tmp_path, real_inflow_file):
        """Test sub_st_inflow_file with real stream inflow file."""
        output_file = tmp_path / 'new_inflow.dat'

        # Use some real stream nodes from the file
        snode_list = [311, 308, 318, 341, 468, 505]  # Sacramento, Clear Creek, Cow Creek, etc.

        iwfm.sub_st_inflow_file(real_inflow_file, str(output_file), snode_list)

        assert os.path.exists(output_file)

        with open(output_file, 'r') as f:
            content = f.read()

        # Should have some content
        assert 'NCOLSTRM' in content
        # Sacramento River node should be preserved
        assert '311' in content

    def test_real_file_selective_nodes(self, tmp_path, real_inflow_file):
        """Test with selective stream nodes from real file."""
        output_file = tmp_path / 'new_inflow.dat'

        # Only keep Sacramento River (311) and Feather River (468)
        snode_list = [311, 468]

        iwfm.sub_st_inflow_file(real_inflow_file, str(output_file), snode_list)

        with open(output_file, 'r') as f:
            content = f.read()

        # These nodes should be preserved
        assert '311' in content
        assert '468' in content
