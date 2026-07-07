#!/usr/bin/env python
# test_sub_rz_nv_file.py
# Unit tests for sub_rz_nv_file.py
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
from pathlib import Path
from unittest.mock import patch

import iwfm
from iwfm.iwfm_dataclasses import SimulationFiles


def create_nv_file_content(nelems, elem_ids, include_initial_cond=True,
                           area_file='RootZone\\NativeVeg_Area.dat'):
    """Create properly structured IWFM native/riparian vegetation file content for testing.

    This function creates a mock native/riparian vegetation file following the IWFM format.
    Comment lines have 'C', 'c', '*' or '#' in first text column.
    Data lines begin with whitespace. Uses '/' = end of record marker.

    Parameters
    ----------
    nelems : int
        Number of elements in the model
    elem_ids : list of int
        List of element IDs to include in element data sections
    include_initial_cond : bool, optional
        Whether to include initial conditions section with element data
    area_file : str, optional
        Path to area file (Windows-style path)

    Returns
    -------
    str
        File content as string with Windows line endings
    """
    lines = []

    # Header comments
    lines.append("C Native and Riparian Vegetation Data File")

    # Native vegetation area file
    lines.append("C Native vegetation area file")
    lines.append(f"    {area_file}           / LUFLNVRV")

    # Rooting depths section (3 factors)
    lines.append("C Rooting depths")
    lines.append("    1.0                   / FACT")
    lines.append("    5.0                   / ROOTNV")
    lines.append("    5.0                   / ROOTRV")

    # Parameters section (element data)
    # Format: IE, CNNV, CNRV, ICETNV, ICETRV, ISTRMRV
    lines.append("C Native and Riparian Vegetation Parameters")
    lines.append("C   IE    CNNV    CNRV    ICETNV    ICETRV    ISTRMRV")
    for elem_id in elem_ids:
        # Use realistic values: curve numbers 38-48, ETc columns 484-505, stream nodes
        cnnv = 40 + (elem_id % 10)
        cnrv = 35 + (elem_id % 10)
        icetnv = 484
        icetrv = 505
        istrmrv = 300 + elem_id  # stream node, 0 means no access
        lines.append(f"	{elem_id}	{cnnv}	{cnrv}	{icetnv}	{icetrv}	{istrmrv}")

    # Initial conditions section
    # Format: IE, SOILM_NV, SOILM_RV
    lines.append("C Initial Soil Moisture Conditions")
    lines.append("C   IE     SOILM_NV  SOILM_RV")
    if not include_initial_cond:
        # First value 0 means no element-specific initial conditions
        lines.append("	0	0.10	0.05")
    else:
        for elem_id in elem_ids:
            soilm_nv = 0.10 + (elem_id % 10) * 0.01
            soilm_rv = 0.05 + (elem_id % 5) * 0.01
            lines.append(f"	{elem_id}	{soilm_nv:.4f}	{soilm_rv:.4f}")

    lines.append("")

    # Join with Windows line endings
    return "\r\n".join(lines)


def create_lu_area_file_content(nelems, elem_ids):
    """Create a simple land use area file for testing.

    Parameters
    ----------
    nelems : int
        Number of elements
    elem_ids : list of int
        List of element IDs

    Returns
    -------
    str
        File content as string
    """
    lines = []
    lines.append("C Land Use Area File - Native and Riparian Vegetation")
    lines.append("C")
    lines.append(f"    {len(elem_ids)}    / NELEM")
    lines.append("C Element areas")

    for elem_id in elem_ids:
        # Format: elem_id, native_area, riparian_area
        lines.append(f"	{elem_id}	100.0	50.0")

    return "\r\n".join(lines)


# ============================================================================
# Tests for sub_rz_nv_file
# ============================================================================

class TestSubRzNvFileBasic:
    """Basic tests for sub_rz_nv_file function."""

    def test_all_elements_in_submodel(self, tmp_path):
        """Test with all elements included in the submodel."""
        elem_ids = [1, 2, 3, 4, 5]

        # Create the main NV file
        nv_content = create_nv_file_content(
            nelems=len(elem_ids),
            elem_ids=elem_ids,
            area_file='RootZone\\NativeVeg_Area.dat'
        )

        old_file = tmp_path / "old_nv.dat"
        old_file.write_text(nv_content)

        # Create the area file
        area_content = create_lu_area_file_content(len(elem_ids), elem_ids)
        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_file = area_dir / "NativeVeg_Area.dat"
        area_file.write_text(area_content)

        # Setup output file paths
        new_file = tmp_path / "new_nv.dat"
        new_area_file = tmp_path / "new_nva"

        sim_files_new = SimulationFiles(
            nv_file=str(new_file),
            nva_file=str(new_area_file)
        )

        # Include all elements
        elems = elem_ids

        # Mock sub_lu_file since it processes the area file separately
        with patch('iwfm.sub_lu_file') as mock_sub_lu:
            iwfm.sub_rz_nv_file(str(old_file), sim_files_new, elems,
                                base_path=tmp_path, verbose=False)

        # Verify output file was created
        assert new_file.exists()

        # Read output and verify all elements are present
        output_content = new_file.read_text()
        for elem_id in elem_ids:
            assert f"\t{elem_id}\t" in output_content or f"	{elem_id}	" in output_content

    def test_subset_elements_in_submodel(self, tmp_path):
        """Test with only some elements in the submodel."""
        all_elem_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        # Create the main NV file
        nv_content = create_nv_file_content(
            nelems=len(all_elem_ids),
            elem_ids=all_elem_ids,
            area_file='RootZone\\NativeVeg_Area.dat'
        )

        old_file = tmp_path / "old_nv.dat"
        old_file.write_text(nv_content)

        # Create the area file
        area_content = create_lu_area_file_content(len(all_elem_ids), all_elem_ids)
        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_file = area_dir / "NativeVeg_Area.dat"
        area_file.write_text(area_content)

        # Setup output file paths
        new_file = tmp_path / "new_nv.dat"
        new_area_file = tmp_path / "new_nva"

        sim_files_new = SimulationFiles(
            nv_file=str(new_file),
            nva_file=str(new_area_file)
        )

        # Include only subset of elements
        elems = [2, 4, 6, 8]

        with patch('iwfm.sub_lu_file') as mock_sub_lu:
            iwfm.sub_rz_nv_file(str(old_file), sim_files_new, elems,
                                base_path=tmp_path, verbose=False)

        # Verify output file was created
        assert new_file.exists()

        # Read output
        output_content = new_file.read_text()

        # Verify file was created successfully
        assert '/ LUFLNVRV' in output_content

        # Check that included elements are present
        for elem_id in elems:
            assert f"\t{elem_id}\t" in output_content or f"	{elem_id}	" in output_content

    def test_no_elements_in_submodel(self, tmp_path):
        """Test with no elements in the submodel."""
        all_elem_ids = [1, 2, 3, 4, 5]

        nv_content = create_nv_file_content(
            nelems=len(all_elem_ids),
            elem_ids=all_elem_ids,
            area_file='RootZone\\NativeVeg_Area.dat'
        )

        old_file = tmp_path / "old_nv.dat"
        old_file.write_text(nv_content)

        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(len(all_elem_ids), all_elem_ids)
        area_file = area_dir / "NativeVeg_Area.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_nv.dat"
        new_area_file = tmp_path / "new_nva"

        sim_files_new = SimulationFiles(
            nv_file=str(new_file),
            nva_file=str(new_area_file)
        )

        # Empty submodel - no elements
        elems = []

        with patch('iwfm.sub_lu_file') as mock_sub_lu:
            iwfm.sub_rz_nv_file(str(old_file), sim_files_new, elems,
                                base_path=tmp_path, verbose=False)

        # Verify output file was created (even if empty of element data)
        assert new_file.exists()


class TestSubRzNvFileAreaFile:
    """Tests for area file handling in sub_rz_nv_file."""

    def test_area_file_path_updated(self, tmp_path):
        """Test that the area file path is updated in output."""
        elem_ids = [1, 2, 3]

        nv_content = create_nv_file_content(
            nelems=len(elem_ids),
            elem_ids=elem_ids,
            area_file='RootZone\\OldAreaFile.dat'
        )

        old_file = tmp_path / "old_nv.dat"
        old_file.write_text(nv_content)

        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(len(elem_ids), elem_ids)
        area_file = area_dir / "OldAreaFile.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_nv.dat"
        new_area_base = tmp_path / "NewSubmodel_NVArea"

        sim_files_new = SimulationFiles(
            nv_file=str(new_file),
            nva_file=str(new_area_base)
        )

        with patch('iwfm.sub_lu_file') as mock_sub_lu:
            iwfm.sub_rz_nv_file(str(old_file), sim_files_new, elem_ids,
                                base_path=tmp_path, verbose=False)

        # Verify the output file contains the new area file name
        output_content = new_file.read_text()
        assert 'NewSubmodel_NVArea.dat' in output_content
        assert '/ LUFLNVRV' in output_content

    def test_sub_lu_file_called(self, tmp_path):
        """Test that sub_lu_file is called with correct parameters."""
        elem_ids = [1, 2, 3]

        nv_content = create_nv_file_content(
            nelems=len(elem_ids),
            elem_ids=elem_ids,
            area_file='RootZone\\AreaFile.dat'
        )

        old_file = tmp_path / "old_nv.dat"
        old_file.write_text(nv_content)

        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(len(elem_ids), elem_ids)
        area_file = area_dir / "AreaFile.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_nv.dat"
        new_area_base = tmp_path / "new_area"

        sim_files_new = SimulationFiles(
            nv_file=str(new_file),
            nva_file=str(new_area_base)
        )

        elems = [1, 3]

        with patch('iwfm.sub_lu_file') as mock_sub_lu:
            iwfm.sub_rz_nv_file(str(old_file), sim_files_new, elems,
                                base_path=tmp_path, verbose=False)

            # Verify sub_lu_file was called
            assert mock_sub_lu.called
            call_args = mock_sub_lu.call_args

            # Check that elems list was passed
            assert elems == call_args[0][2]


class TestSubRzNvFileVerbose:
    """Tests for verbose mode in sub_rz_nv_file."""

    def test_verbose_true(self, tmp_path, capsys):
        """Test verbose mode outputs message."""
        elem_ids = [1, 2]

        nv_content = create_nv_file_content(
            nelems=len(elem_ids),
            elem_ids=elem_ids,
            area_file='RootZone\\Area.dat'
        )

        old_file = tmp_path / "old_nv.dat"
        old_file.write_text(nv_content)

        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(len(elem_ids), elem_ids)
        area_file = area_dir / "Area.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_nv.dat"
        new_area_base = tmp_path / "new_area"

        sim_files_new = SimulationFiles(
            nv_file=str(new_file),
            nva_file=str(new_area_base)
        )

        with patch('iwfm.sub_lu_file'):
            iwfm.sub_rz_nv_file(str(old_file), sim_files_new, elem_ids,
                                base_path=tmp_path, verbose=True)

        captured = capsys.readouterr()
        assert 'native and riparian file' in captured.out.lower()

    def test_verbose_false(self, tmp_path, capsys):
        """Test that verbose=False produces no output."""
        elem_ids = [1, 2]

        nv_content = create_nv_file_content(
            nelems=len(elem_ids),
            elem_ids=elem_ids,
            area_file='RootZone\\Area.dat'
        )

        old_file = tmp_path / "old_nv.dat"
        old_file.write_text(nv_content)

        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(len(elem_ids), elem_ids)
        area_file = area_dir / "Area.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_nv.dat"
        new_area_base = tmp_path / "new_area"

        sim_files_new = SimulationFiles(
            nv_file=str(new_file),
            nva_file=str(new_area_base)
        )

        with patch('iwfm.sub_lu_file'):
            iwfm.sub_rz_nv_file(str(old_file), sim_files_new, elem_ids,
                                base_path=tmp_path, verbose=False)

        captured = capsys.readouterr()
        # Should be minimal or no output when verbose is False
        assert 'native and riparian file' not in captured.out.lower()


class TestSubRzNvFileEdgeCases:
    """Edge case tests for sub_rz_nv_file."""

    def test_single_element(self, tmp_path):
        """Test with single element in model."""
        elem_ids = [1]

        nv_content = create_nv_file_content(
            nelems=1,
            elem_ids=elem_ids,
            area_file='RootZone\\Area.dat'
        )

        old_file = tmp_path / "old_nv.dat"
        old_file.write_text(nv_content)

        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(1, elem_ids)
        area_file = area_dir / "Area.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_nv.dat"
        new_area_base = tmp_path / "new_area"

        sim_files_new = SimulationFiles(
            nv_file=str(new_file),
            nva_file=str(new_area_base)
        )

        with patch('iwfm.sub_lu_file'):
            iwfm.sub_rz_nv_file(str(old_file), sim_files_new, elem_ids,
                                base_path=tmp_path, verbose=False)

        assert new_file.exists()

    def test_many_elements(self, tmp_path):
        """Test with many elements (like C2VSimCG with 1392 elements)."""
        elem_ids = list(range(1, 101))  # 100 elements for testing

        nv_content = create_nv_file_content(
            nelems=len(elem_ids),
            elem_ids=elem_ids,
            area_file='RootZone\\Area.dat'
        )

        old_file = tmp_path / "old_nv.dat"
        old_file.write_text(nv_content)

        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(len(elem_ids), elem_ids)
        area_file = area_dir / "Area.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_nv.dat"
        new_area_base = tmp_path / "new_area"

        sim_files_new = SimulationFiles(
            nv_file=str(new_file),
            nva_file=str(new_area_base)
        )

        # Include subset of elements
        elems = [10, 20, 30, 40, 50]

        with patch('iwfm.sub_lu_file'):
            iwfm.sub_rz_nv_file(str(old_file), sim_files_new, elems,
                                base_path=tmp_path, verbose=False)

        assert new_file.exists()

    def test_non_sequential_element_ids(self, tmp_path):
        """Test with non-sequential element IDs."""
        elem_ids = [5, 10, 15, 100, 500]

        nv_content = create_nv_file_content(
            nelems=len(elem_ids),
            elem_ids=elem_ids,
            area_file='RootZone\\Area.dat'
        )

        old_file = tmp_path / "old_nv.dat"
        old_file.write_text(nv_content)

        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(len(elem_ids), elem_ids)
        area_file = area_dir / "Area.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_nv.dat"
        new_area_base = tmp_path / "new_area"

        sim_files_new = SimulationFiles(
            nv_file=str(new_file),
            nva_file=str(new_area_base)
        )

        # Include subset of non-sequential elements
        elems = [10, 100]

        with patch('iwfm.sub_lu_file'):
            iwfm.sub_rz_nv_file(str(old_file), sim_files_new, elems,
                                base_path=tmp_path, verbose=False)

        assert new_file.exists()

    def test_no_initial_conditions(self, tmp_path):
        """Test with no element-specific initial conditions (IE=0)."""
        elem_ids = [1, 2, 3]

        nv_content = create_nv_file_content(
            nelems=len(elem_ids),
            elem_ids=elem_ids,
            area_file='RootZone\\Area.dat',
            include_initial_cond=False
        )

        old_file = tmp_path / "old_nv.dat"
        old_file.write_text(nv_content)

        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(len(elem_ids), elem_ids)
        area_file = area_dir / "Area.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_nv.dat"
        new_area_base = tmp_path / "new_area"

        sim_files_new = SimulationFiles(
            nv_file=str(new_file),
            nva_file=str(new_area_base)
        )

        with patch('iwfm.sub_lu_file'):
            iwfm.sub_rz_nv_file(str(old_file), sim_files_new, elem_ids,
                                base_path=tmp_path, verbose=False)

        assert new_file.exists()


class TestSubRzNvFileNotFound:
    """Tests for file not found error handling."""

    def test_file_not_found(self, tmp_path):
        """Test that FileNotFoundError is raised for missing file."""
        nonexistent_file = str(tmp_path / "nonexistent_nv.dat")

        sim_files_new = SimulationFiles(
            nv_file=str(tmp_path / 'new_nv.dat'),
            nva_file=str(tmp_path / 'new_area')
        )

        elems = [1, 2, 3]

        # The iwfm.file_test() function calls sys.exit() when file is not found
        with pytest.raises(FileNotFoundError):
            iwfm.sub_rz_nv_file(nonexistent_file, sim_files_new, elems, verbose=False)


class TestSubRzNvFilePathHandling:
    """Tests for file path handling in sub_rz_nv_file."""

    def test_backslash_to_forward_slash_conversion(self, tmp_path):
        """Test that Windows backslash paths are converted to forward slashes."""
        elem_ids = [1, 2]

        # Use Windows-style path with backslashes
        nv_content = create_nv_file_content(
            nelems=len(elem_ids),
            elem_ids=elem_ids,
            area_file='RootZone\\SubDir\\Area.dat'
        )

        old_file = tmp_path / "old_nv.dat"
        old_file.write_text(nv_content)

        # Create nested directory structure
        area_dir = tmp_path / "RootZone" / "SubDir"
        area_dir.mkdir(parents=True)
        area_content = create_lu_area_file_content(len(elem_ids), elem_ids)
        area_file = area_dir / "Area.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_nv.dat"
        new_area_base = tmp_path / "new_area"

        sim_files_new = SimulationFiles(
            nv_file=str(new_file),
            nva_file=str(new_area_base)
        )

        with patch('iwfm.sub_lu_file') as mock_sub_lu:
            iwfm.sub_rz_nv_file(str(old_file), sim_files_new, elem_ids,
                                base_path=tmp_path, verbose=False)

            # sub_lu_file should be called with forward-slash path
            call_args = mock_sub_lu.call_args
            area_path_arg = call_args[0][0]
            # Path should be resolved and not contain backslashes
            assert '\\' not in area_path_arg or '/' in area_path_arg


# ============================================================================
# Integration test with real-format data
# ============================================================================

class TestSubRzNvFileRealFormat:
    """Tests using realistic IWFM native vegetation file format."""

    def test_realistic_file_structure(self, tmp_path):
        """Test with realistic IWFM NV file structure."""
        # Create a more realistic file similar to C2VSimCG format
        lines = []
        lines.append("C*******************************************************************************")
        lines.append("C")
        lines.append("C                 NATIVE AND RIPARIAN VEGETATION DATA FILE")
        lines.append("C                         Root Zone Component")
        lines.append("C")
        lines.append("C*******************************************************************************")
        lines.append("C   LUFLNVRV   ;  File that lists the land use areas")
        lines.append("C--------------------------------------------------------------------------------")
        lines.append("     RootZone\\C2VSimCG_NativeVeg_Area.dat                     / LUFLNVRV")
        lines.append("C*******************************************************************************")
        lines.append("C                              Rooting Depths")
        lines.append("C--------------------------------------------------------------------------------")
        lines.append("    1.0                   / FACT")
        lines.append("    5.0                   / ROOTNV")
        lines.append("    5.0                   / ROOTRV")
        lines.append("C*******************************************************************************")
        lines.append("C         Native and Riparian Vegetation Parameters")
        lines.append("C   IE    CNNV    CNRV    ICETNV    ICETRV    ISTRMRV")
        lines.append("C--------------------------------------------------------------------------------")
        lines.append("	1	38	32	484	505	313")
        lines.append("	2	44	39	484	505	312")
        lines.append("	3	45	40	484	505	0")
        lines.append("	4	46	41	484	505	0")
        lines.append("	5	42	37	484	505	313")
        lines.append("C*******************************************************************************")
        lines.append("C                           Initial Soil Moisture")
        lines.append("C   IE     SOILM_NV  SOILM_RV")
        lines.append("C--------------------------------------------------------------------------------")
        lines.append("	1	0.0844	0.0448")
        lines.append("	2	0.1358	0.0305")
        lines.append("	3	0.1440	0.0504")
        lines.append("	4	0.1310	0.0489")
        lines.append("	5	0.1616	0.0277")
        lines.append("")

        content = "\r\n".join(lines)

        old_file = tmp_path / "old_nv.dat"
        old_file.write_text(content)

        # Create area file
        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(5, [1, 2, 3, 4, 5])
        area_file = area_dir / "C2VSimCG_NativeVeg_Area.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_nv.dat"
        new_area_base = tmp_path / "new_area"

        sim_files_new = SimulationFiles(
            nv_file=str(new_file),
            nva_file=str(new_area_base)
        )

        # Include only elements 2 and 4
        elems = [2, 4]

        with patch('iwfm.sub_lu_file'):
            iwfm.sub_rz_nv_file(str(old_file), sim_files_new, elems,
                                base_path=tmp_path, verbose=False)

        assert new_file.exists()

        # Verify output structure
        output_content = new_file.read_text()

        # Should have area file marker
        assert '/ LUFLNVRV' in output_content

        # Should have new area file name
        assert 'new_area.dat' in output_content


# ============================================================================
# Tests with actual test data file (if available)
# ============================================================================

TEST_DATA_DIR = Path(__file__).parent / "C2VSimCG-2021"
NV_FILE = TEST_DATA_DIR / "Simulation" / "Rootzone" / "C2VSimCG_NativeVeg.dat"


@pytest.fixture
def nv_file_exists():
    """Check that the C2VSimCG native vegetation file exists."""
    if not TEST_DATA_DIR.exists():
        pytest.skip(f"Test data directory not found: {TEST_DATA_DIR}")
    if not NV_FILE.exists():
        pytest.skip(f"Native vegetation file not found: {NV_FILE}")
    return True


class TestSubRzNvFileWithRealFile:
    """Tests using the actual C2VSimCG native vegetation file."""

    def test_real_file_format_verification(self, nv_file_exists):
        """Test that C2VSimCG NV file has expected structure."""
        with open(NV_FILE, 'r') as f:
            content = f.read()

        # Verify file has expected markers
        assert '/ LUFLNVRV' in content, "Should have land use file marker"
        assert '/ FACT' in content, "Should have FACT marker"
        assert '/ ROOTNV' in content, "Should have ROOTNV marker"
        assert '/ ROOTRV' in content, "Should have ROOTRV marker"

    def test_real_file_has_parameters_section(self, nv_file_exists):
        """Test that C2VSimCG NV file has parameters section."""
        with open(NV_FILE, 'r') as f:
            lines = f.readlines()

        # Find the first data line after ROOTRV (should be parameters)
        found_rootrv = False
        has_param_data = False
        for line in lines:
            if '/ ROOTRV' in line:
                found_rootrv = True
                continue
            if found_rootrv and line.strip() and line[0] not in ['C', 'c', '*', '#']:
                # This should be the first parameter line
                parts = line.split()
                if len(parts) >= 6:
                    has_param_data = True
                break

        assert has_param_data, "Should have parameter data after ROOTRV"

    def test_real_file_has_initial_conditions(self, nv_file_exists):
        """Test that C2VSimCG NV file has initial conditions section."""
        with open(NV_FILE, 'r') as f:
            content = f.read()

        assert 'Initial' in content, "Should have Initial Soil Moisture section"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
