# test_sub_streams_file.py
# Tests for sub_streams_file function
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
from unittest.mock import patch
import iwfm
from iwfm.iwfm_dataclasses import SimulationFiles


def create_streams_file_no_subfiles():
    """Create mock streams file with no optional sub-files (blank paths).

    Based on C2VSimCG_Streams.dat format:
    - First line is version tag
    - Comment lines start with 'C', 'c', '*', or '#'
    - Data lines start with whitespace
    - '/' marks end of record
    """
    content = """#4.2
C Stream parameters data file
C
                                                / INFLOWFL
                                                / DIVSPECFL
                                                / BYPSPECFL
                                                / DIVFL
    Results\\Streams_Budget.hdf                 / STRMRCHBUDFL
    Results\\Diversions.hdf                     / DIVDTLBUDFL
C*******************************************************************************
       4                                     	/ NOUTR
       0                                       	/ IHSQR
       0.000022957                             	/ FACTVROU
       AC-FT/MON                              	/ UNITVROU
       1                                     	/ FACTLTOU
       FEET                                   	/ UNITLTOU
       Results\\Stream_Hydrographs.out         / STHYDOUTFL
C-------------------------------------------------------------------------------
	101		Node101	/	Stream Node 101
	102		Node102	/	Stream Node 102
	103		Node103	/	Stream Node 103
	104		Node104	/	Stream Node 104
C*******************************************************************************
        4                         			/ NBUDR
        Results\\StreamNode_Budget.hdf          / STNDBUDFL
C-------------------------------------------------------------------------------
	101
	102
	103
	104
C*******************************************************************************
C   FACTK   FACTL   FACTW
C-------------------------------------------------------------------------------
    1.0                                         / FACTK
    1.0                                         / FACTL
    1.0                                         / FACTW
C-------------------------------------------------------------------------------
	101	300	100	2.0	1
	102	300	101	2.0	1
	103	300	102	2.0	1
	104	300	103	2.0	1
"""
    return content


def create_streams_file_with_subfiles():
    """Create mock streams file with sub-files specified."""
    content = """#4.2
C Stream parameters data file
C
    Streams\\StreamInflow.dat                   / INFLOWFL
    Streams\\DiversionSpec.dat                  / DIVSPECFL
    Streams\\BypassSpec.dat                     / BYPSPECFL
    Streams\\Diversions.dat                     / DIVFL
    Results\\Streams_Budget.hdf                 / STRMRCHBUDFL
    Results\\Diversions.hdf                     / DIVDTLBUDFL
C*******************************************************************************
       6                                     	/ NOUTR
       0                                       	/ IHSQR
       0.000022957                             	/ FACTVROU
       AC-FT/MON                              	/ UNITVROU
       1                                     	/ FACTLTOU
       FEET                                   	/ UNITLTOU
       Results\\Stream_Hydrographs.out         / STHYDOUTFL
C-------------------------------------------------------------------------------
	101		Node101	/	Stream Node 101
	102		Node102	/	Stream Node 102
	103		Node103	/	Stream Node 103
	201		Node201	/	Stream Node 201
	202		Node202	/	Stream Node 202
	203		Node203	/	Stream Node 203
C*******************************************************************************
        8                         			/ NBUDR
        Results\\StreamNode_Budget.hdf          / STNDBUDFL
C-------------------------------------------------------------------------------
	101
	102
	103
	104
	201
	202
	203
	204
C*******************************************************************************
    1.0                                         / FACTK
    1.0                                         / FACTL
    1.0                                         / FACTW
C-------------------------------------------------------------------------------
	101	300	100	2.0	1
	102	300	101	2.0	1
	103	300	102	2.0	1
	104	300	103	2.0	1
	201	400	200	2.5	1
	202	400	201	2.5	1
	203	400	202	2.5	1
	204	400	203	2.5	1
"""
    return content


def create_inflow_file_content():
    """Create mock stream inflow file content."""
    content = """C Stream inflow data file
          4                                         / NCOLSTRM
          43560000.0                                / FACTSTRM
          1                                         / NSPSTRM
          0                                         / NFQSTRM
                                                    / DSSFL
C-------------------------------------------------------------------------------
	101		/1:  Node 101
	102		/2:  Node 102
	103		/3:  Node 103
	104		/4:  Node 104
"""
    return content


def create_bypass_file_content():
    """Create mock bypass specification file content."""
    content = """C Stream bypass specification data file
      2                        / NDIVS
      60                       / FACTX
      1min                     / TUNITX
      60                       / FACTY
      1min                     / TUNITY
C-------------------------------------------------------------------------------
	1	101	1	102	10	0	0	Bypass_1
	2	201	1	202	11	0	0	Bypass_2
C-------------------------------------------------------------------------------
   1              0             0         0
   2              0             0         0
"""
    return content


class TestSubStreamsFileBasic:
    """Basic functionality tests for sub_streams_file."""

    def test_creates_output_file(self, tmp_path):
        """Test that output file is created."""
        streams_file = tmp_path / 'streams.dat'
        streams_file.write_text(create_streams_file_no_subfiles())

        sim_files = SimulationFiles(stream_file=str(streams_file))
        sim_files_new = SimulationFiles(
            stream_file=str(tmp_path / 'new_streams.dat'),
            stin_file=str(tmp_path / 'new_inflow'),
            divspec_file=str(tmp_path / 'new_divspec'),
            bp_file=str(tmp_path / 'new_bypass'),
            div_file=str(tmp_path / 'new_div'),
        )

        elem_list = [[100], [101], [102], [103]]
        sub_snodes = [101, 102, 103, 104]

        iwfm.sub_streams_file(sim_files, sim_files_new, elem_list, sub_snodes)

        assert os.path.exists(sim_files_new.stream_file)

    def test_returns_none(self, tmp_path):
        """Test that function returns None."""
        streams_file = tmp_path / 'streams.dat'
        streams_file.write_text(create_streams_file_no_subfiles())

        sim_files = SimulationFiles(stream_file=str(streams_file))
        sim_files_new = SimulationFiles(
            stream_file=str(tmp_path / 'new_streams.dat'),
            stin_file=str(tmp_path / 'new_inflow'),
            divspec_file=str(tmp_path / 'new_divspec'),
            bp_file=str(tmp_path / 'new_bypass'),
            div_file=str(tmp_path / 'new_div'),
        )

        elem_list = [[100], [101], [102], [103]]
        sub_snodes = [101, 102, 103, 104]

        result = iwfm.sub_streams_file(sim_files, sim_files_new, elem_list, sub_snodes)

        assert result is None

    def test_preserves_version_tag(self, tmp_path):
        """Test that version tag is preserved."""
        streams_file = tmp_path / 'streams.dat'
        streams_file.write_text(create_streams_file_no_subfiles())

        sim_files = SimulationFiles(stream_file=str(streams_file))
        sim_files_new = SimulationFiles(
            stream_file=str(tmp_path / 'new_streams.dat'),
            stin_file=str(tmp_path / 'new_inflow'),
            divspec_file=str(tmp_path / 'new_divspec'),
            bp_file=str(tmp_path / 'new_bypass'),
            div_file=str(tmp_path / 'new_div'),
        )

        elem_list = [[100]]
        sub_snodes = [101, 102, 103, 104]

        iwfm.sub_streams_file(sim_files, sim_files_new, elem_list, sub_snodes)

        with open(sim_files_new.stream_file, 'r') as f:
            first_line = f.readline()

        assert '#4.2' in first_line


class TestSubStreamsFileHydrographs:
    """Tests for hydrograph filtering in sub_streams_file."""

    def test_filters_hydrographs_by_stream_node(self, tmp_path):
        """Test that hydrographs are filtered by stream node."""
        streams_file = tmp_path / 'streams.dat'
        streams_file.write_text(create_streams_file_no_subfiles())

        sim_files = SimulationFiles(stream_file=str(streams_file))
        sim_files_new = SimulationFiles(
            stream_file=str(tmp_path / 'new_streams.dat'),
            stin_file=str(tmp_path / 'new_inflow'),
            divspec_file=str(tmp_path / 'new_divspec'),
            bp_file=str(tmp_path / 'new_bypass'),
            div_file=str(tmp_path / 'new_div'),
        )

        elem_list = [[100], [101]]
        # Only include stream nodes 101, 102
        sub_snodes = [101, 102]

        iwfm.sub_streams_file(sim_files, sim_files_new, elem_list, sub_snodes)

        with open(sim_files_new.stream_file, 'r') as f:
            lines = f.readlines()

        # Find NOUTR line
        for line in lines:
            if 'NOUTR' in line:
                noutr = int(line.split()[0])
                assert noutr == 2  # Only 101 and 102
                break

    def test_updates_noutr_count(self, tmp_path):
        """Test that NOUTR count is updated correctly."""
        streams_file = tmp_path / 'streams.dat'
        streams_file.write_text(create_streams_file_no_subfiles())

        sim_files = SimulationFiles(stream_file=str(streams_file))
        sim_files_new = SimulationFiles(
            stream_file=str(tmp_path / 'new_streams.dat'),
            stin_file=str(tmp_path / 'new_inflow'),
            divspec_file=str(tmp_path / 'new_divspec'),
            bp_file=str(tmp_path / 'new_bypass'),
            div_file=str(tmp_path / 'new_div'),
        )

        elem_list = [[100]]
        # Only include stream node 101
        sub_snodes = [101]

        iwfm.sub_streams_file(sim_files, sim_files_new, elem_list, sub_snodes)

        with open(sim_files_new.stream_file, 'r') as f:
            lines = f.readlines()

        # Find NOUTR line
        for line in lines:
            if 'NOUTR' in line:
                noutr = int(line.split()[0])
                assert noutr == 1
                break


class TestSubStreamsFileBudgets:
    """Tests for budget filtering in sub_streams_file."""

    def test_filters_budgets_by_stream_node(self, tmp_path):
        """Test that budget nodes are filtered by stream node."""
        streams_file = tmp_path / 'streams.dat'
        streams_file.write_text(create_streams_file_no_subfiles())

        sim_files = SimulationFiles(stream_file=str(streams_file))
        sim_files_new = SimulationFiles(
            stream_file=str(tmp_path / 'new_streams.dat'),
            stin_file=str(tmp_path / 'new_inflow'),
            divspec_file=str(tmp_path / 'new_divspec'),
            bp_file=str(tmp_path / 'new_bypass'),
            div_file=str(tmp_path / 'new_div'),
        )

        elem_list = [[100], [101]]
        # Only include stream nodes 101, 103
        sub_snodes = [101, 103]

        iwfm.sub_streams_file(sim_files, sim_files_new, elem_list, sub_snodes)

        with open(sim_files_new.stream_file, 'r') as f:
            lines = f.readlines()

        # Find NBUDR line
        for line in lines:
            if 'NBUDR' in line:
                nbudr = int(line.split()[0])
                assert nbudr == 2  # Only 101 and 103
                break

    def test_updates_nbudr_count(self, tmp_path):
        """Test that NBUDR count is updated correctly."""
        streams_file = tmp_path / 'streams.dat'
        streams_file.write_text(create_streams_file_no_subfiles())

        sim_files = SimulationFiles(stream_file=str(streams_file))
        sim_files_new = SimulationFiles(
            stream_file=str(tmp_path / 'new_streams.dat'),
            stin_file=str(tmp_path / 'new_inflow'),
            divspec_file=str(tmp_path / 'new_divspec'),
            bp_file=str(tmp_path / 'new_bypass'),
            div_file=str(tmp_path / 'new_div'),
        )

        elem_list = [[100]]
        # Only include stream node 102
        sub_snodes = [102]

        iwfm.sub_streams_file(sim_files, sim_files_new, elem_list, sub_snodes)

        with open(sim_files_new.stream_file, 'r') as f:
            lines = f.readlines()

        # Find NBUDR line
        for line in lines:
            if 'NBUDR' in line:
                nbudr = int(line.split()[0])
                assert nbudr == 1
                break


class TestSubStreamsFileStreambedParams:
    """Tests for streambed parameter filtering in sub_streams_file."""

    def test_filters_streambed_params_by_stream_node(self, tmp_path):
        """Test that streambed parameters are filtered by stream node."""
        streams_file = tmp_path / 'streams.dat'
        streams_file.write_text(create_streams_file_no_subfiles())

        sim_files = SimulationFiles(stream_file=str(streams_file))
        sim_files_new = SimulationFiles(
            stream_file=str(tmp_path / 'new_streams.dat'),
            stin_file=str(tmp_path / 'new_inflow'),
            divspec_file=str(tmp_path / 'new_divspec'),
            bp_file=str(tmp_path / 'new_bypass'),
            div_file=str(tmp_path / 'new_div'),
        )

        elem_list = [[100], [101]]
        # Only include stream nodes 101, 102
        sub_snodes = [101, 102]

        iwfm.sub_streams_file(sim_files, sim_files_new, elem_list, sub_snodes)

        with open(sim_files_new.stream_file, 'r') as f:
            lines = f.readlines()

        # Find streambed param section (after FACTW line)
        # Streambed params have format: node width elem bedthk wp (5 numeric fields)
        in_streambed_section = False
        streambed_count = 0
        for line in lines:
            if 'FACTW' in line:
                in_streambed_section = True
                continue
            if in_streambed_section:
                stripped = line.strip()
                if stripped and stripped[0].isdigit():
                    parts = stripped.split()
                    if len(parts) >= 5:
                        streambed_count += 1

        assert streambed_count == 2


class TestSubStreamsFileVerbose:
    """Tests for verbose output."""

    def test_verbose_output(self, tmp_path, capsys):
        """Test that verbose mode produces output."""
        streams_file = tmp_path / 'streams.dat'
        streams_file.write_text(create_streams_file_no_subfiles())

        sim_files = SimulationFiles(stream_file=str(streams_file))
        sim_files_new = SimulationFiles(
            stream_file=str(tmp_path / 'new_streams.dat'),
            stin_file=str(tmp_path / 'new_inflow'),
            divspec_file=str(tmp_path / 'new_divspec'),
            bp_file=str(tmp_path / 'new_bypass'),
            div_file=str(tmp_path / 'new_div'),
        )

        elem_list = [[100]]
        sub_snodes = [101, 102, 103, 104]

        iwfm.sub_streams_file(sim_files, sim_files_new, elem_list, sub_snodes, verbose=True)

        captured = capsys.readouterr()
        assert 'Wrote stream main file' in captured.out

    def test_no_verbose_output_by_default(self, tmp_path, capsys):
        """Test that no output is produced when verbose=False."""
        streams_file = tmp_path / 'streams.dat'
        streams_file.write_text(create_streams_file_no_subfiles())

        sim_files = SimulationFiles(stream_file=str(streams_file))
        sim_files_new = SimulationFiles(
            stream_file=str(tmp_path / 'new_streams.dat'),
            stin_file=str(tmp_path / 'new_inflow'),
            divspec_file=str(tmp_path / 'new_divspec'),
            bp_file=str(tmp_path / 'new_bypass'),
            div_file=str(tmp_path / 'new_div'),
        )

        elem_list = [[100]]
        sub_snodes = [101, 102, 103, 104]

        iwfm.sub_streams_file(sim_files, sim_files_new, elem_list, sub_snodes, verbose=False)

        captured = capsys.readouterr()
        assert captured.out == ''


class TestSubStreamsFileNotFound:
    """Tests for file not found handling."""

    def test_missing_stream_file_raises_error(self, tmp_path):
        """Test that missing stream file raises FileNotFoundError."""
        sim_files = SimulationFiles(stream_file=str(tmp_path / 'nonexistent.dat'))
        sim_files_new = SimulationFiles(
            stream_file=str(tmp_path / 'new_streams.dat'),
            stin_file=str(tmp_path / 'new_inflow'),
            divspec_file=str(tmp_path / 'new_divspec'),
            bp_file=str(tmp_path / 'new_bypass'),
            div_file=str(tmp_path / 'new_div'),
        )

        elem_list = [[100]]
        sub_snodes = [101]

        with pytest.raises(FileNotFoundError):
            iwfm.sub_streams_file(sim_files, sim_files_new, elem_list, sub_snodes)

    def test_missing_stream_file_key_raises_error(self, tmp_path):
        """Test that missing stream_file key raises FileNotFoundError."""
        sim_files = SimulationFiles()  # stream_file defaults to empty string
        sim_files_new = SimulationFiles(
            stream_file=str(tmp_path / 'new_streams.dat'),
            stin_file=str(tmp_path / 'new_inflow'),
            divspec_file=str(tmp_path / 'new_divspec'),
            bp_file=str(tmp_path / 'new_bypass'),
            div_file=str(tmp_path / 'new_div'),
        )

        elem_list = [[100]]
        sub_snodes = [101]

        with pytest.raises(FileNotFoundError):
            iwfm.sub_streams_file(sim_files, sim_files_new, elem_list, sub_snodes)


class TestSubStreamsFileEdgeCases:
    """Edge case tests for sub_streams_file."""

    def test_all_nodes_removed(self, tmp_path):
        """Test when all stream nodes are removed."""
        streams_file = tmp_path / 'streams.dat'
        streams_file.write_text(create_streams_file_no_subfiles())

        sim_files = SimulationFiles(stream_file=str(streams_file))
        sim_files_new = SimulationFiles(
            stream_file=str(tmp_path / 'new_streams.dat'),
            stin_file=str(tmp_path / 'new_inflow'),
            divspec_file=str(tmp_path / 'new_divspec'),
            bp_file=str(tmp_path / 'new_bypass'),
            div_file=str(tmp_path / 'new_div'),
        )

        elem_list = [[100]]
        # No matching stream nodes
        sub_snodes = [999]

        iwfm.sub_streams_file(sim_files, sim_files_new, elem_list, sub_snodes)

        with open(sim_files_new.stream_file, 'r') as f:
            lines = f.readlines()

        # NOUTR and NBUDR should be 0
        for line in lines:
            if 'NOUTR' in line:
                noutr = int(line.split()[0])
                assert noutr == 0
            if 'NBUDR' in line:
                nbudr = int(line.split()[0])
                assert nbudr == 0

    def test_all_nodes_kept(self, tmp_path):
        """Test when all stream nodes are kept."""
        streams_file = tmp_path / 'streams.dat'
        streams_file.write_text(create_streams_file_no_subfiles())

        sim_files = SimulationFiles(stream_file=str(streams_file))
        sim_files_new = SimulationFiles(
            stream_file=str(tmp_path / 'new_streams.dat'),
            stin_file=str(tmp_path / 'new_inflow'),
            divspec_file=str(tmp_path / 'new_divspec'),
            bp_file=str(tmp_path / 'new_bypass'),
            div_file=str(tmp_path / 'new_div'),
        )

        elem_list = [[100], [101], [102], [103]]
        # All stream nodes included
        sub_snodes = [101, 102, 103, 104]

        iwfm.sub_streams_file(sim_files, sim_files_new, elem_list, sub_snodes)

        with open(sim_files_new.stream_file, 'r') as f:
            lines = f.readlines()

        # NOUTR should be 4
        for line in lines:
            if 'NOUTR' in line:
                noutr = int(line.split()[0])
                assert noutr == 4
                break

    def test_blank_file_paths_handled(self, tmp_path):
        """Test that blank file paths are handled correctly."""
        streams_file = tmp_path / 'streams.dat'
        streams_file.write_text(create_streams_file_no_subfiles())

        sim_files = SimulationFiles(stream_file=str(streams_file))
        sim_files_new = SimulationFiles(
            stream_file=str(tmp_path / 'new_streams.dat'),
            stin_file=str(tmp_path / 'new_inflow'),
            divspec_file=str(tmp_path / 'new_divspec'),
            bp_file=str(tmp_path / 'new_bypass'),
            div_file=str(tmp_path / 'new_div'),
        )

        elem_list = [[100]]
        sub_snodes = [101, 102, 103, 104]

        # Should not raise an error for blank file paths
        iwfm.sub_streams_file(sim_files, sim_files_new, elem_list, sub_snodes)

        assert os.path.exists(sim_files_new.stream_file)


class TestSubStreamsFileWithSubfiles:
    """Tests for sub_streams_file with sub-files specified."""

    def test_calls_sub_st_inflow_file(self, tmp_path):
        """Test that sub_st_inflow_file is called when inflow file exists."""
        # Create directory structure
        streams_dir = tmp_path / 'Streams'
        streams_dir.mkdir()

        streams_file = tmp_path / 'streams.dat'
        streams_file.write_text(create_streams_file_with_subfiles())

        inflow_file = streams_dir / 'StreamInflow.dat'
        inflow_file.write_text(create_inflow_file_content())

        bypass_file = streams_dir / 'BypassSpec.dat'
        bypass_file.write_text(create_bypass_file_content())

        sim_files = SimulationFiles(stream_file=str(streams_file))
        sim_files_new = SimulationFiles(
            stream_file=str(tmp_path / 'new_streams.dat'),
            stin_file=str(tmp_path / 'new_inflow'),
            divspec_file=str(tmp_path / 'new_divspec'),
            bp_file=str(tmp_path / 'new_bypass'),
            div_file=str(tmp_path / 'new_div'),
        )

        elem_list = [[100], [101]]
        sub_snodes = [101, 102, 103, 104]

        with patch('iwfm.sub_st_inflow_file') as mock_inflow, \
             patch('iwfm.sub_st_bp_file') as mock_bp:
            mock_bp.return_value = 2

            iwfm.sub_streams_file(sim_files, sim_files_new, elem_list, sub_snodes, base_path=tmp_path)

            # sub_st_inflow_file should be called
            mock_inflow.assert_called_once()

    def test_calls_sub_st_bp_file(self, tmp_path):
        """Test that sub_st_bp_file is called when bypass file exists."""
        streams_dir = tmp_path / 'Streams'
        streams_dir.mkdir()

        streams_file = tmp_path / 'streams.dat'
        streams_file.write_text(create_streams_file_with_subfiles())

        inflow_file = streams_dir / 'StreamInflow.dat'
        inflow_file.write_text(create_inflow_file_content())

        bypass_file = streams_dir / 'BypassSpec.dat'
        bypass_file.write_text(create_bypass_file_content())

        sim_files = SimulationFiles(stream_file=str(streams_file))
        sim_files_new = SimulationFiles(
            stream_file=str(tmp_path / 'new_streams.dat'),
            stin_file=str(tmp_path / 'new_inflow'),
            divspec_file=str(tmp_path / 'new_divspec'),
            bp_file=str(tmp_path / 'new_bypass'),
            div_file=str(tmp_path / 'new_div'),
        )

        elem_list = [[100], [101]]
        sub_snodes = [101, 102, 103, 104]

        with patch('iwfm.sub_st_inflow_file') as mock_inflow, \
             patch('iwfm.sub_st_bp_file') as mock_bp:
            mock_bp.return_value = 2

            iwfm.sub_streams_file(sim_files, sim_files_new, elem_list, sub_snodes, base_path=tmp_path)

            # sub_st_bp_file should be called
            mock_bp.assert_called_once()


class TestSubStreamsFileWithRealFile:
    """Tests using actual C2VSimCG_Streams.dat file if available."""

    @pytest.fixture
    def real_streams_file(self):
        """Return path to real streams file if it exists and is readable."""
        real_file = '/Volumes/MinEx/Documents/Dropbox/work/Programing/repos/iwfm-py/iwfm-tests/C2VSimCG-2021/Simulation/Streams/C2VSimCG_Streams.dat'
        if not os.path.exists(real_file):
            pytest.skip("Real C2VSimCG_Streams.dat file not available")
        try:
            with open(real_file, 'r') as f:
                f.read()
        except UnicodeDecodeError:
            pytest.skip("Real file has encoding issues (non-UTF-8 characters)")
        return real_file

    def test_real_file_format_verification(self, real_streams_file):
        """Test that real C2VSimCG streams file has expected structure."""
        with open(real_streams_file, 'r') as f:
            content = f.read()

        # Verify file has expected sections
        assert '/ INFLOWFL' in content or 'INFLOWFL' in content
        assert '/ NOUTR' in content or 'NOUTR' in content
        assert '/ NBUDR' in content or 'NBUDR' in content

    def test_with_real_file_mocked_subfiles(self, tmp_path, real_streams_file):
        """Test sub_streams_file with real streams file, mocking sub-file processing."""
        sim_files = SimulationFiles(stream_file=real_streams_file)
        sim_files_new = SimulationFiles(
            stream_file=str(tmp_path / 'new_streams.dat'),
            stin_file=str(tmp_path / 'new_inflow'),
            divspec_file=str(tmp_path / 'new_divspec'),
            bp_file=str(tmp_path / 'new_bypass'),
            div_file=str(tmp_path / 'new_div'),
        )

        elem_list = [[100], [101], [102]]
        # Use some stream nodes from the file
        sub_snodes = [320, 330, 335, 339, 341, 351]

        # Mock the sub-file processing functions
        with patch('iwfm.sub_st_inflow_file') as mock_inflow, \
             patch('iwfm.sub_st_bp_file') as mock_bp:
            mock_bp.return_value = 0  # No bypasses kept

            from pathlib import Path
            base_path = Path('/Volumes/MinEx/Documents/Dropbox/work/Programing/repos/iwfm-py/iwfm-tests/C2VSimCG-2021/Simulation')
            iwfm.sub_streams_file(sim_files, sim_files_new, elem_list, sub_snodes, base_path=base_path)

        assert os.path.exists(sim_files_new.stream_file)

        with open(sim_files_new.stream_file, 'r') as f:
            content = f.read()

        # Should have version tag
        assert '#4.2' in content
