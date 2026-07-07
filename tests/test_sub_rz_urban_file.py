#!/usr/bin/env python
# test_sub_rz_urban_file.py
# Unit tests for sub_rz_urban_file.py
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


def create_urban_file_content(nelems, elem_ids, include_initial_cond=True,
                              area_file='RootZone\\Urban_Area.dat'):
    """Create properly structured IWFM urban lands file content for testing.

    This function creates a mock urban lands file following the IWFM format.
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
        Path to urban area file (Windows-style path)

    Returns
    -------
    str
        File content as string with Windows line endings
    """
    lines = []

    # Header comments
    lines.append("C Urban Lands Data File")

    # Urban area file
    lines.append("C Urban area file")
    lines.append(f"    {area_file}           / LUFLU")

    # Rooting depth section (2 factors)
    lines.append("C Rooting depth")
    lines.append("    1.0                   / FACT")
    lines.append("    2.0                   / ROOTURB")

    # Urban water use files (3 file names)
    lines.append("C Urban water use files")
    lines.append("    RootZone\\Urban_Population.dat          / POPULFL")
    lines.append("    RootZone\\Urban_PerCapWaterUse.dat      / WTRUSEFL")
    lines.append("    RootZone\\Urban_WaterUseSpecs.dat       / URBSPECFL")

    # Urban parameters section (element data)
    # Format: IE, PERV, CNURB, ICPOPUL, ICWTRUSE, FRACDM, ICETURB, ICRTFURB, ICRUFURB, ICURBSPEC
    lines.append("C Urban Parameters")
    lines.append("C   IE    PERV    CNURB   ICPOPUL ICWTRUSE FRACDM ICETURB ICRTFURB ICRUFURB ICURBSPEC")
    for elem_id in elem_ids:
        perv = 0.62
        cnurb = 55 + (elem_id % 10)
        icpopul = 6
        icwtruse = 6
        fracdm = -1
        iceturb = 463
        icrtfurb = 6
        icrufurb = 6
        icurbspec = 1
        lines.append(f"	{elem_id}	{perv}	{cnurb}	{icpopul}	{icwtruse}	{fracdm}	{iceturb}	{icrtfurb}	{icrufurb}	{icurbspec}")

    # Initial conditions section
    # Format: IE, FSOILMP, SOILM
    lines.append("C Initial Soil Moisture Conditions")
    lines.append("C   IE    FSOILMP    SOILM")
    if not include_initial_cond:
        # First value 0 means no element-specific initial conditions
        lines.append("	0	0.5	0.20")
    else:
        for elem_id in elem_ids:
            fsoilmp = 0.5
            soilm = 0.15 + (elem_id % 10) * 0.01
            lines.append(f"	{elem_id}	{fsoilmp}	{soilm:.5f}")

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
    lines.append("C Land Use Area File - Urban")
    lines.append("C")
    lines.append(f"    {len(elem_ids)}    / NELEM")
    lines.append("C Element areas")

    for elem_id in elem_ids:
        # Format: elem_id, urban_area
        lines.append(f"	{elem_id}	100.0")

    return "\r\n".join(lines)


# ============================================================================
# Tests for sub_rz_urban_file
# ============================================================================

class TestSubRzUrbanFileBasic:
    """Basic tests for sub_rz_urban_file function."""

    def test_all_elements_in_submodel(self, tmp_path):
        """Test with all elements included in the submodel."""
        elem_ids = [1, 2, 3, 4, 5]

        # Create the main urban file
        urban_content = create_urban_file_content(
            nelems=len(elem_ids),
            elem_ids=elem_ids,
            area_file='RootZone\\Urban_Area.dat'
        )

        old_file = tmp_path / "old_urban.dat"
        old_file.write_text(urban_content)

        # Create the area file
        area_content = create_lu_area_file_content(len(elem_ids), elem_ids)
        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_file = area_dir / "Urban_Area.dat"
        area_file.write_text(area_content)

        # Setup output file paths
        new_file = tmp_path / "new_urban.dat"
        new_area_file = tmp_path / "new_ura"

        sim_files_new = SimulationFiles(
            ur_file=str(new_file),
            ura_file=str(new_area_file)
        )

        # Include all elements
        elems = elem_ids

        # Mock sub_lu_file since it processes the area file separately
        with patch('iwfm.sub_lu_file') as mock_sub_lu:
            iwfm.sub_rz_urban_file(str(old_file), sim_files_new, elems,
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

        # Create the main urban file
        urban_content = create_urban_file_content(
            nelems=len(all_elem_ids),
            elem_ids=all_elem_ids,
            area_file='RootZone\\Urban_Area.dat'
        )

        old_file = tmp_path / "old_urban.dat"
        old_file.write_text(urban_content)

        # Create the area file
        area_content = create_lu_area_file_content(len(all_elem_ids), all_elem_ids)
        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_file = area_dir / "Urban_Area.dat"
        area_file.write_text(area_content)

        # Setup output file paths
        new_file = tmp_path / "new_urban.dat"
        new_area_file = tmp_path / "new_ura"

        sim_files_new = SimulationFiles(
            ur_file=str(new_file),
            ura_file=str(new_area_file)
        )

        # Include only subset of elements
        elems = [2, 4, 6, 8]

        with patch('iwfm.sub_lu_file') as mock_sub_lu:
            iwfm.sub_rz_urban_file(str(old_file), sim_files_new, elems,
                                   base_path=tmp_path, verbose=False)

        # Verify output file was created
        assert new_file.exists()

        # Read output
        output_content = new_file.read_text()

        # Verify file was created successfully
        assert '/ LUFLU' in output_content

        # Check that included elements are present
        for elem_id in elems:
            assert f"\t{elem_id}\t" in output_content or f"	{elem_id}	" in output_content

    def test_no_elements_in_submodel(self, tmp_path):
        """Test with no elements in the submodel."""
        all_elem_ids = [1, 2, 3, 4, 5]

        urban_content = create_urban_file_content(
            nelems=len(all_elem_ids),
            elem_ids=all_elem_ids,
            area_file='RootZone\\Urban_Area.dat'
        )

        old_file = tmp_path / "old_urban.dat"
        old_file.write_text(urban_content)

        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(len(all_elem_ids), all_elem_ids)
        area_file = area_dir / "Urban_Area.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_urban.dat"
        new_area_file = tmp_path / "new_ura"

        sim_files_new = SimulationFiles(
            ur_file=str(new_file),
            ura_file=str(new_area_file)
        )

        # Empty submodel - no elements
        elems = []

        with patch('iwfm.sub_lu_file') as mock_sub_lu:
            iwfm.sub_rz_urban_file(str(old_file), sim_files_new, elems,
                                   base_path=tmp_path, verbose=False)

        # Verify output file was created (even if empty of element data)
        assert new_file.exists()


class TestSubRzUrbanFileAreaFile:
    """Tests for area file handling in sub_rz_urban_file."""

    def test_area_file_path_updated(self, tmp_path):
        """Test that the area file path is updated in output."""
        elem_ids = [1, 2, 3]

        urban_content = create_urban_file_content(
            nelems=len(elem_ids),
            elem_ids=elem_ids,
            area_file='RootZone\\OldAreaFile.dat'
        )

        old_file = tmp_path / "old_urban.dat"
        old_file.write_text(urban_content)

        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(len(elem_ids), elem_ids)
        area_file = area_dir / "OldAreaFile.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_urban.dat"
        new_area_base = tmp_path / "NewSubmodel_UrbanArea"

        sim_files_new = SimulationFiles(
            ur_file=str(new_file),
            ura_file=str(new_area_base)
        )

        with patch('iwfm.sub_lu_file') as mock_sub_lu:
            iwfm.sub_rz_urban_file(str(old_file), sim_files_new, elem_ids,
                                   base_path=tmp_path, verbose=False)

        # Verify the output file contains the new area file name
        output_content = new_file.read_text()
        assert 'NewSubmodel_UrbanArea.dat' in output_content
        assert '/ LUFLU' in output_content

    def test_sub_lu_file_called(self, tmp_path):
        """Test that sub_lu_file is called with correct parameters."""
        elem_ids = [1, 2, 3]

        urban_content = create_urban_file_content(
            nelems=len(elem_ids),
            elem_ids=elem_ids,
            area_file='RootZone\\AreaFile.dat'
        )

        old_file = tmp_path / "old_urban.dat"
        old_file.write_text(urban_content)

        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(len(elem_ids), elem_ids)
        area_file = area_dir / "AreaFile.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_urban.dat"
        new_area_base = tmp_path / "new_area"

        sim_files_new = SimulationFiles(
            ur_file=str(new_file),
            ura_file=str(new_area_base)
        )

        elems = [1, 3]

        with patch('iwfm.sub_lu_file') as mock_sub_lu:
            iwfm.sub_rz_urban_file(str(old_file), sim_files_new, elems,
                                   base_path=tmp_path, verbose=False)

            # Verify sub_lu_file was called
            assert mock_sub_lu.called
            call_args = mock_sub_lu.call_args

            # Check that elems list was passed
            assert elems == call_args[0][2]


class TestSubRzUrbanFileVerbose:
    """Tests for verbose mode in sub_rz_urban_file."""

    def test_verbose_true(self, tmp_path, capsys):
        """Test verbose mode outputs message."""
        elem_ids = [1, 2]

        urban_content = create_urban_file_content(
            nelems=len(elem_ids),
            elem_ids=elem_ids,
            area_file='RootZone\\Area.dat'
        )

        old_file = tmp_path / "old_urban.dat"
        old_file.write_text(urban_content)

        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(len(elem_ids), elem_ids)
        area_file = area_dir / "Area.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_urban.dat"
        new_area_base = tmp_path / "new_area"

        sim_files_new = SimulationFiles(
            ur_file=str(new_file),
            ura_file=str(new_area_base)
        )

        with patch('iwfm.sub_lu_file'):
            iwfm.sub_rz_urban_file(str(old_file), sim_files_new, elem_ids,
                                   base_path=tmp_path, verbose=True)

        captured = capsys.readouterr()
        assert 'urban file' in captured.out.lower()

    def test_verbose_false(self, tmp_path, capsys):
        """Test that verbose=False produces no output."""
        elem_ids = [1, 2]

        urban_content = create_urban_file_content(
            nelems=len(elem_ids),
            elem_ids=elem_ids,
            area_file='RootZone\\Area.dat'
        )

        old_file = tmp_path / "old_urban.dat"
        old_file.write_text(urban_content)

        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(len(elem_ids), elem_ids)
        area_file = area_dir / "Area.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_urban.dat"
        new_area_base = tmp_path / "new_area"

        sim_files_new = SimulationFiles(
            ur_file=str(new_file),
            ura_file=str(new_area_base)
        )

        with patch('iwfm.sub_lu_file'):
            iwfm.sub_rz_urban_file(str(old_file), sim_files_new, elem_ids,
                                   base_path=tmp_path, verbose=False)

        captured = capsys.readouterr()
        # Should be minimal or no output when verbose is False
        assert 'urban file' not in captured.out.lower()


class TestSubRzUrbanFileEdgeCases:
    """Edge case tests for sub_rz_urban_file."""

    def test_single_element(self, tmp_path):
        """Test with single element in model."""
        elem_ids = [1]

        urban_content = create_urban_file_content(
            nelems=1,
            elem_ids=elem_ids,
            area_file='RootZone\\Area.dat'
        )

        old_file = tmp_path / "old_urban.dat"
        old_file.write_text(urban_content)

        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(1, elem_ids)
        area_file = area_dir / "Area.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_urban.dat"
        new_area_base = tmp_path / "new_area"

        sim_files_new = SimulationFiles(
            ur_file=str(new_file),
            ura_file=str(new_area_base)
        )

        with patch('iwfm.sub_lu_file'):
            iwfm.sub_rz_urban_file(str(old_file), sim_files_new, elem_ids,
                                   base_path=tmp_path, verbose=False)

        assert new_file.exists()

    def test_many_elements(self, tmp_path):
        """Test with many elements (like C2VSimCG with 1392 elements)."""
        elem_ids = list(range(1, 101))  # 100 elements for testing

        urban_content = create_urban_file_content(
            nelems=len(elem_ids),
            elem_ids=elem_ids,
            area_file='RootZone\\Area.dat'
        )

        old_file = tmp_path / "old_urban.dat"
        old_file.write_text(urban_content)

        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(len(elem_ids), elem_ids)
        area_file = area_dir / "Area.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_urban.dat"
        new_area_base = tmp_path / "new_area"

        sim_files_new = SimulationFiles(
            ur_file=str(new_file),
            ura_file=str(new_area_base)
        )

        # Include subset of elements
        elems = [10, 20, 30, 40, 50]

        with patch('iwfm.sub_lu_file'):
            iwfm.sub_rz_urban_file(str(old_file), sim_files_new, elems,
                                   base_path=tmp_path, verbose=False)

        assert new_file.exists()

    def test_non_sequential_element_ids(self, tmp_path):
        """Test with non-sequential element IDs."""
        elem_ids = [5, 10, 15, 100, 500]

        urban_content = create_urban_file_content(
            nelems=len(elem_ids),
            elem_ids=elem_ids,
            area_file='RootZone\\Area.dat'
        )

        old_file = tmp_path / "old_urban.dat"
        old_file.write_text(urban_content)

        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(len(elem_ids), elem_ids)
        area_file = area_dir / "Area.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_urban.dat"
        new_area_base = tmp_path / "new_area"

        sim_files_new = SimulationFiles(
            ur_file=str(new_file),
            ura_file=str(new_area_base)
        )

        # Include subset of non-sequential elements
        elems = [10, 100]

        with patch('iwfm.sub_lu_file'):
            iwfm.sub_rz_urban_file(str(old_file), sim_files_new, elems,
                                   base_path=tmp_path, verbose=False)

        assert new_file.exists()

    def test_no_initial_conditions(self, tmp_path):
        """Test with no element-specific initial conditions (IE=0)."""
        elem_ids = [1, 2, 3]

        urban_content = create_urban_file_content(
            nelems=len(elem_ids),
            elem_ids=elem_ids,
            area_file='RootZone\\Area.dat',
            include_initial_cond=False
        )

        old_file = tmp_path / "old_urban.dat"
        old_file.write_text(urban_content)

        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(len(elem_ids), elem_ids)
        area_file = area_dir / "Area.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_urban.dat"
        new_area_base = tmp_path / "new_area"

        sim_files_new = SimulationFiles(
            ur_file=str(new_file),
            ura_file=str(new_area_base)
        )

        with patch('iwfm.sub_lu_file'):
            iwfm.sub_rz_urban_file(str(old_file), sim_files_new, elem_ids,
                                   base_path=tmp_path, verbose=False)

        assert new_file.exists()


class TestSubRzUrbanFileNotFound:
    """Tests for file not found error handling."""

    def test_file_not_found(self, tmp_path):
        """Test that FileNotFoundError is raised for missing file."""
        nonexistent_file = str(tmp_path / "nonexistent_urban.dat")

        sim_files_new = SimulationFiles(
            ur_file=str(tmp_path / 'new_urban.dat'),
            ura_file=str(tmp_path / 'new_area')
        )

        elems = [1, 2, 3]

        # The iwfm.file_test() function calls sys.exit() when file is not found
        with pytest.raises(FileNotFoundError):
            iwfm.sub_rz_urban_file(nonexistent_file, sim_files_new, elems, verbose=False)


class TestSubRzUrbanFilePathHandling:
    """Tests for file path handling in sub_rz_urban_file."""

    def test_backslash_to_forward_slash_conversion(self, tmp_path):
        """Test that Windows backslash paths are converted to forward slashes."""
        elem_ids = [1, 2]

        # Use Windows-style path with backslashes
        urban_content = create_urban_file_content(
            nelems=len(elem_ids),
            elem_ids=elem_ids,
            area_file='RootZone\\SubDir\\Area.dat'
        )

        old_file = tmp_path / "old_urban.dat"
        old_file.write_text(urban_content)

        # Create nested directory structure
        area_dir = tmp_path / "RootZone" / "SubDir"
        area_dir.mkdir(parents=True)
        area_content = create_lu_area_file_content(len(elem_ids), elem_ids)
        area_file = area_dir / "Area.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_urban.dat"
        new_area_base = tmp_path / "new_area"

        sim_files_new = SimulationFiles(
            ur_file=str(new_file),
            ura_file=str(new_area_base)
        )

        with patch('iwfm.sub_lu_file') as mock_sub_lu:
            iwfm.sub_rz_urban_file(str(old_file), sim_files_new, elem_ids,
                                   base_path=tmp_path, verbose=False)

            # sub_lu_file should be called with forward-slash path
            call_args = mock_sub_lu.call_args
            area_path_arg = call_args[0][0]
            # Path should be resolved and not contain backslashes
            assert '\\' not in area_path_arg or '/' in area_path_arg


# ============================================================================
# Integration test with real-format data
# ============================================================================

class TestSubRzUrbanFileRealFormat:
    """Tests using realistic IWFM urban file format."""

    def test_realistic_file_structure(self, tmp_path):
        """Test with realistic IWFM urban file structure."""
        # Create a more realistic file similar to C2VSimCG format
        lines = []
        lines.append("C*******************************************************************************")
        lines.append("C")
        lines.append("C                        URBAN LANDS DATA FILE")
        lines.append("C                         Root Zone Component")
        lines.append("C")
        lines.append("C*******************************************************************************")
        lines.append("C   LUFLU   ;  File that lists the urban areas")
        lines.append("C--------------------------------------------------------------------------------")
        lines.append("     RootZone\\C2VSimCG_Urban_Area.dat              / LUFLU")
        lines.append("C*******************************************************************************")
        lines.append("C                              Rooting Depth")
        lines.append("C--------------------------------------------------------------------------------")
        lines.append("    1.0                   / FACT")
        lines.append("    2.0                   / ROOTURB")
        lines.append("C*******************************************************************************")
        lines.append("C                  Urban Water Use Files")
        lines.append("C--------------------------------------------------------------------------------")
        lines.append("    RootZone\\C2VSimCG_Urban_Population.dat          / POPULFL")
        lines.append("    RootZone\\C2VSimCG_Urban_PerCapWaterUse.dat      / WTRUSEFL")
        lines.append("    RootZone\\C2VSimCG_Urban_WaterUseSpecs.dat       / URBSPECFL")
        lines.append("C*******************************************************************************")
        lines.append("C                  Urban Parameters")
        lines.append("C   IE    PERV    CNURB   ICPOPUL ICWTRUSE FRACDM ICETURB ICRTFURB ICRUFURB ICURBSPEC")
        lines.append("C--------------------------------------------------------------------------------")
        lines.append("	1	0.62	58	6	6	-1	463	6	6	1")
        lines.append("	2	0.62	61	10	10	-1	463	6	6	1")
        lines.append("	3	0.62	61	10	10	-1	463	6	6	1")
        lines.append("	4	0.62	61	10	10	-1	463	6	6	1")
        lines.append("	5	0.62	60	10	10	-1	463	6	6	1")
        lines.append("C*******************************************************************************")
        lines.append("C                           Initial Soil Moisture")
        lines.append("C   IE    FSOILMP    SOILM")
        lines.append("C--------------------------------------------------------------------------------")
        lines.append("	1	0.5	0.19344")
        lines.append("	2	0.5	0.22071")
        lines.append("	3	0.5	0.23707")
        lines.append("	4	0.5	0.22046")
        lines.append("	5	0.5	0.25669")
        lines.append("")

        content = "\r\n".join(lines)

        old_file = tmp_path / "old_urban.dat"
        old_file.write_text(content)

        # Create area file
        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(5, [1, 2, 3, 4, 5])
        area_file = area_dir / "C2VSimCG_Urban_Area.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_urban.dat"
        new_area_base = tmp_path / "new_area"

        sim_files_new = SimulationFiles(
            ur_file=str(new_file),
            ura_file=str(new_area_base)
        )

        # Include only elements 2 and 4
        elems = [2, 4]

        with patch('iwfm.sub_lu_file'):
            iwfm.sub_rz_urban_file(str(old_file), sim_files_new, elems,
                                   base_path=tmp_path, verbose=False)

        assert new_file.exists()

        # Verify output structure
        output_content = new_file.read_text()

        # Should have area file marker
        assert '/ LUFLU' in output_content

        # Should have new area file name
        assert 'new_area.dat' in output_content


# ============================================================================
# Tests with actual test data file (if available)
# ============================================================================

TEST_DATA_DIR = Path(__file__).parent / "C2VSimCG-2021"
URBAN_FILE = TEST_DATA_DIR / "Simulation" / "Rootzone" / "C2VSimCG_Urban.dat"


@pytest.fixture
def urban_file_exists():
    """Check that the C2VSimCG urban file exists."""
    if not TEST_DATA_DIR.exists():
        pytest.skip(f"Test data directory not found: {TEST_DATA_DIR}")
    if not URBAN_FILE.exists():
        pytest.skip(f"Urban file not found: {URBAN_FILE}")
    return True


class TestSubRzUrbanFileWithRealFile:
    """Tests using the actual C2VSimCG urban file."""

    def test_real_file_format_verification(self, urban_file_exists):
        """Test that C2VSimCG urban file has expected structure."""
        with open(URBAN_FILE, 'r') as f:
            content = f.read()

        # Verify file has expected markers
        assert '/ LUFLU' in content, "Should have land use file marker"
        assert '/ FACT' in content, "Should have FACT marker"
        assert '/ ROOTURB' in content, "Should have ROOTURB marker"

    def test_real_file_has_water_use_files(self, urban_file_exists):
        """Test that C2VSimCG urban file has water use file section."""
        with open(URBAN_FILE, 'r') as f:
            content = f.read()

        # Verify water use files are present
        assert '/ POPULFL' in content, "Should have population file marker"
        assert '/ WTRUSEFL' in content, "Should have water use file marker"
        assert '/ URBSPECFL' in content, "Should have urban specs file marker"

    def test_real_file_has_initial_conditions(self, urban_file_exists):
        """Test that C2VSimCG urban file has initial conditions section."""
        with open(URBAN_FILE, 'r') as f:
            content = f.read()

        assert 'Initial' in content, "Should have Initial Soil Moisture section"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
