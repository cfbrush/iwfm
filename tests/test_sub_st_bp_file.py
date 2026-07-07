# test_sub_st_bp_file.py
# Tests for sub_st_bp_file function
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


def create_bypass_spec_file_content():
    """Create mock stream bypass specification file content.

    Based on C2VSimCG_BypassSpec.dat format:
    - Comment lines start with 'C', 'c', '*', or '#'
    - Data lines start with whitespace
    - '/' marks end of record
    - First data section: NDIVS (number of bypasses), then factors
    - Second section: bypass specs (ID, IA, TYPEDEST, DEST, IDIVC, DIVRL, DIVNL, NAME)
      - If IDIVC < 0, followed by abs(IDIVC) rating table lines
    - Third section: seepage locations (ID, NERELS, IERELS, FERELS)
      - If NERELS > 0, followed by NERELS-1 additional element lines
    """
    content = """C Stream bypass specification data file
C
      4                        / NDIVS
      60                       / FACTX
      1min                     / TUNITX
      60                       / FACTY
      1min                     / TUNITY
C-------------------------------------------------------------------------------
C ID  IA  TYPEDEST  DEST  IDIVC  DIVRL  DIVNL  NAME
C-------------------------------------------------------------------------------
	1	101	1	150	10	0	0	Bypass_1		/ Bypass 1 - simple diversion
	2	102	1	151	11	0	0	Bypass_2		/ Bypass 2 - simple diversion
	3	103	1	152	-3	0	0	Bypass_3		/ Bypass 3 - rating table
					0	0
					100	50
					1000	500
	4	104	0	0	-2	0.5	0	Bypass_4		/ Bypass 4 - rating table, outside model
					0	0
					500	500
C-------------------------------------------------------------------------------
C Seepage locations for bypass canals
C-------------------------------------------------------------------------------
C    ID         NERELS      IERELS     FERELS
C-------------------------------------------------------------------------------
   1              0             0         0
   2              0             0         0
   3              2          1001         1
                            1002         1
   4              0             0         0
"""
    return content


def create_bypass_spec_more_bypasses():
    """Create mock file with more bypasses for testing filtering."""
    content = """C Stream bypass specification data file
      6                        / NDIVS
      60                       / FACTX
      1min                     / TUNITX
      60                       / FACTY
      1min                     / TUNITY
C-------------------------------------------------------------------------------
	1	101	1	150	10	0	0	Bypass_1
	2	102	1	151	11	0	0	Bypass_2
	3	200	1	201	12	0	0	Bypass_3
	4	201	1	202	-2	0	0	Bypass_4
					0	0
					1000	1000
	5	300	0	0	13	0	0	Bypass_5
	6	301	1	302	-3	0	0	Bypass_6
					0	0
					500	250
					5000	2500
C-------------------------------------------------------------------------------
   1              0             0         0
   2              0             0         0
   3              0             0         0
   4              0             0         0
   5              0             0         0
   6              0             0         0
"""
    return content


class TestSubStBpFileBasic:
    """Basic functionality tests for sub_st_bp_file."""

    def test_creates_output_file(self, tmp_path):
        """Test that output file is created."""
        input_file = tmp_path / 'old_bypass.dat'
        input_file.write_text(create_bypass_spec_file_content())
        output_file = tmp_path / 'new_bypass.dat'

        # elem_list format: list of [elem_id, ...] sublists
        elem_list = [[1001], [1002], [1003]]
        # snode_list: list of stream node IDs
        snode_list = [101, 102, 103, 104, 150, 151, 152]

        iwfm.sub_st_bp_file(str(input_file), str(output_file), elem_list, snode_list)

        assert os.path.exists(output_file)

    def test_returns_count_of_kept_bypasses(self, tmp_path):
        """Test that function returns count of bypasses kept."""
        input_file = tmp_path / 'old_bypass.dat'
        input_file.write_text(create_bypass_spec_file_content())
        output_file = tmp_path / 'new_bypass.dat'

        elem_list = [[1001], [1002]]
        snode_list = [101, 102, 103, 104, 150, 151, 152]

        result = iwfm.sub_st_bp_file(str(input_file), str(output_file), elem_list, snode_list)

        # All 4 bypasses have stream nodes in snode_list
        assert result == 4

    def test_keeps_bypasses_with_matching_stream_nodes(self, tmp_path):
        """Test that bypasses with stream nodes in snode_list are kept."""
        input_file = tmp_path / 'old_bypass.dat'
        input_file.write_text(create_bypass_spec_file_content())
        output_file = tmp_path / 'new_bypass.dat'

        elem_list = [[1001], [1002]]
        # Only include stream nodes for bypasses 1 and 2
        snode_list = [101, 102]

        result = iwfm.sub_st_bp_file(str(input_file), str(output_file), elem_list, snode_list)

        assert result == 2

        with open(output_file, 'r') as f:
            content = f.read()

        assert 'Bypass_1' in content
        assert 'Bypass_2' in content

    def test_removes_bypasses_without_matching_stream_nodes(self, tmp_path):
        """Test that bypasses without matching stream nodes are removed."""
        input_file = tmp_path / 'old_bypass.dat'
        input_file.write_text(create_bypass_spec_file_content())
        output_file = tmp_path / 'new_bypass.dat'

        elem_list = [[1001], [1002]]
        # Only include stream nodes for bypasses 1 and 2, not 3 and 4
        snode_list = [101, 102]

        iwfm.sub_st_bp_file(str(input_file), str(output_file), elem_list, snode_list)

        with open(output_file, 'r') as f:
            content = f.read()

        # Bypasses 3 and 4 should be removed
        assert 'Bypass_3' not in content
        assert 'Bypass_4' not in content

    def test_updates_ndivs_count(self, tmp_path):
        """Test that NDIVS count is updated correctly."""
        input_file = tmp_path / 'old_bypass.dat'
        input_file.write_text(create_bypass_spec_file_content())
        output_file = tmp_path / 'new_bypass.dat'

        elem_list = [[1001], [1002]]
        # Only include stream node for bypass 1
        snode_list = [101]

        iwfm.sub_st_bp_file(str(input_file), str(output_file), elem_list, snode_list)

        with open(output_file, 'r') as f:
            lines = f.readlines()

        # Find the NDIVS line
        for line in lines:
            if 'NDIVS' in line:
                ndivs = int(line.split()[0])
                assert ndivs == 1
                break

    def test_preserves_comments(self, tmp_path):
        """Test that comments are preserved in output."""
        input_file = tmp_path / 'old_bypass.dat'
        input_file.write_text(create_bypass_spec_file_content())
        output_file = tmp_path / 'new_bypass.dat'

        elem_list = [[1001], [1002]]
        snode_list = [101, 102, 103, 104]

        iwfm.sub_st_bp_file(str(input_file), str(output_file), elem_list, snode_list)

        with open(output_file, 'r') as f:
            content = f.read()

        assert 'C Stream bypass specification data file' in content


class TestSubStBpFileRatingTables:
    """Tests for handling rating table bypasses."""

    def test_keeps_rating_table_lines_for_kept_bypass(self, tmp_path):
        """Test that rating table lines are kept when bypass is kept."""
        input_file = tmp_path / 'old_bypass.dat'
        input_file.write_text(create_bypass_spec_file_content())
        output_file = tmp_path / 'new_bypass.dat'

        elem_list = [[1001], [1002]]
        # Include stream node 103 for bypass 3 (has rating table)
        snode_list = [103]

        iwfm.sub_st_bp_file(str(input_file), str(output_file), elem_list, snode_list)

        with open(output_file, 'r') as f:
            content = f.read()

        assert 'Bypass_3' in content
        # Rating table values should be present
        assert '1000' in content

    def test_removes_rating_table_lines_for_removed_bypass(self, tmp_path):
        """Test that rating table lines are removed when bypass is removed."""
        input_file = tmp_path / 'old_bypass.dat'
        input_file.write_text(create_bypass_spec_file_content())
        output_file = tmp_path / 'new_bypass.dat'

        elem_list = [[1001], [1002]]
        # Only include stream node 101, bypass 3 should be removed
        snode_list = [101]

        iwfm.sub_st_bp_file(str(input_file), str(output_file), elem_list, snode_list)

        with open(output_file, 'r') as f:
            content = f.read()

        assert 'Bypass_3' not in content


class TestSubStBpFileVerbose:
    """Tests for verbose output."""

    def test_verbose_output(self, tmp_path, capsys):
        """Test that verbose mode produces output."""
        input_file = tmp_path / 'old_bypass.dat'
        input_file.write_text(create_bypass_spec_file_content())
        output_file = tmp_path / 'new_bypass.dat'

        elem_list = [[1001], [1002]]
        snode_list = [101, 102, 103, 104]

        iwfm.sub_st_bp_file(str(input_file), str(output_file), elem_list, snode_list, verbose=True)

        captured = capsys.readouterr()
        assert 'Wrote stream bypass specification file' in captured.out
        assert str(output_file) in captured.out

    def test_no_verbose_output_by_default(self, tmp_path, capsys):
        """Test that no output is produced when verbose=False."""
        input_file = tmp_path / 'old_bypass.dat'
        input_file.write_text(create_bypass_spec_file_content())
        output_file = tmp_path / 'new_bypass.dat'

        elem_list = [[1001], [1002]]
        snode_list = [101, 102, 103, 104]

        iwfm.sub_st_bp_file(str(input_file), str(output_file), elem_list, snode_list, verbose=False)

        captured = capsys.readouterr()
        assert captured.out == ''


class TestSubStBpFileNotFound:
    """Tests for file not found handling."""

    def test_missing_input_file_raises_error(self, tmp_path):
        """Test that missing input file raises FileNotFoundError."""
        output_file = tmp_path / 'new_bypass.dat'
        elem_list = [[1001]]
        snode_list = [101]

        with pytest.raises(FileNotFoundError):
            iwfm.sub_st_bp_file(str(tmp_path / 'nonexistent.dat'), str(output_file), elem_list, snode_list)


class TestSubStBpFileEdgeCases:
    """Edge case tests for sub_st_bp_file."""

    def test_all_bypasses_removed(self, tmp_path):
        """Test when all bypasses are removed."""
        input_file = tmp_path / 'old_bypass.dat'
        input_file.write_text(create_bypass_spec_file_content())
        output_file = tmp_path / 'new_bypass.dat'

        elem_list = [[1001]]
        # No matching stream nodes
        snode_list = [999]

        result = iwfm.sub_st_bp_file(str(input_file), str(output_file), elem_list, snode_list)

        assert result == 0

        with open(output_file, 'r') as f:
            content = f.read()

        # NDIVS should be 0
        for line in content.split('\n'):
            if 'NDIVS' in line:
                ndivs = int(line.split()[0])
                assert ndivs == 0
                break

    def test_all_bypasses_kept(self, tmp_path):
        """Test when all bypasses are kept."""
        input_file = tmp_path / 'old_bypass.dat'
        input_file.write_text(create_bypass_spec_file_content())
        output_file = tmp_path / 'new_bypass.dat'

        elem_list = [[1001], [1002]]
        # All stream nodes included
        snode_list = [101, 102, 103, 104]

        result = iwfm.sub_st_bp_file(str(input_file), str(output_file), elem_list, snode_list)

        assert result == 4

    def test_with_more_bypasses(self, tmp_path):
        """Test with more bypasses and selective filtering."""
        input_file = tmp_path / 'old_bypass.dat'
        input_file.write_text(create_bypass_spec_more_bypasses())
        output_file = tmp_path / 'new_bypass.dat'

        elem_list = [[1001], [1002]]
        # Only keep bypasses 1, 3, 5 (stream nodes 101, 200, 300)
        snode_list = [101, 200, 300]

        result = iwfm.sub_st_bp_file(str(input_file), str(output_file), elem_list, snode_list)

        assert result == 3

        with open(output_file, 'r') as f:
            content = f.read()

        assert 'Bypass_1' in content
        assert 'Bypass_3' in content
        assert 'Bypass_5' in content
        assert 'Bypass_2' not in content
        assert 'Bypass_4' not in content
        assert 'Bypass_6' not in content

    def test_empty_elem_list(self, tmp_path):
        """Test with empty element list."""
        input_file = tmp_path / 'old_bypass.dat'
        input_file.write_text(create_bypass_spec_file_content())
        output_file = tmp_path / 'new_bypass.dat'

        elem_list = []
        snode_list = [101, 102]

        result = iwfm.sub_st_bp_file(str(input_file), str(output_file), elem_list, snode_list)

        # Should still work, bypasses filtered by snode_list
        assert result == 2


class TestSubStBpFileWithRealFile:
    """Tests using actual C2VSimCG_BypassSpec.dat file if available."""

    @pytest.fixture
    def real_bypass_file(self):
        """Return path to real bypass spec file if it exists and is readable."""
        real_file = '/Volumes/MinEx/Documents/Dropbox/work/Programing/repos/iwfm-py/iwfm-tests/C2VSimCG-2021/Simulation/Streams/C2VSimCG_BypassSpec.dat'
        if not os.path.exists(real_file):
            pytest.skip("Real C2VSimCG_BypassSpec.dat file not available")
        # Check if file is readable (may have encoding issues)
        try:
            with open(real_file, 'r') as f:
                f.read()
        except UnicodeDecodeError:
            pytest.skip("Real file has encoding issues (non-UTF-8 characters)")
        return real_file

    def test_with_real_file(self, tmp_path, real_bypass_file):
        """Test sub_st_bp_file with real bypass spec file."""
        output_file = tmp_path / 'new_bypass.dat'

        # Use some real stream nodes from the file
        elem_list = [[1060], [1072], [1129]]
        snode_list = [401, 402, 404, 407, 409, 430, 498, 503, 446]  # Some Sacramento Valley nodes

        result = iwfm.sub_st_bp_file(real_bypass_file, str(output_file), elem_list, snode_list)

        assert os.path.exists(output_file)
        assert result >= 0

        with open(output_file, 'r') as f:
            content = f.read()

        # Should have some content
        assert 'NDIVS' in content

    def test_real_file_selective_nodes(self, tmp_path, real_bypass_file):
        """Test with selective stream nodes from real file."""
        output_file = tmp_path / 'new_bypass.dat'

        elem_list = [[1001]]
        # Only keep bypasses with these stream nodes
        snode_list = [401, 402]  # M&T Flood and 3Bs Flood

        result = iwfm.sub_st_bp_file(real_bypass_file, str(output_file), elem_list, snode_list)

        assert result == 2  # Should keep only 2 bypasses

        with open(output_file, 'r') as f:
            content = f.read()

        assert 'M&T_Flood' in content
        assert '3Bs_Flood' in content
