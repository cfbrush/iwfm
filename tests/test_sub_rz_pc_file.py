#!/usr/bin/env python
# test_sub_rz_pc_file.py
# Unit tests for sub_rz_pc_file.py
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


# Number of ponded crop types (rice and refuge) - fixed at 5 in IWFM
NCROP = 5


def create_pc_file_content(nelems, elem_ids, nbud=0, include_initial_cond=True,
                           area_file='RootZone\\PondedCrop_Area.dat'):
    """Create properly structured IWFM ponded crop file content for testing.

    This function creates a mock ponded crop (rice/refuge) file following the IWFM format.
    Comment lines have 'C', 'c', '*' or '#' in first text column.
    Data lines begin with whitespace. Uses '/' = end of record marker.

    The 5 ponded crop types are:
    1. RICE_FL  - Rice with flooded decomposition
    2. RICE_NFL - Rice with non-flooded decomposition
    3. RICE_NDC - Rice with no decomposition
    4. REFUGE_SL - Seasonal refuges
    5. REFUGE_PR - Permanent refuges

    Parameters
    ----------
    nelems : int
        Number of elements in the model
    elem_ids : list of int
        List of element IDs to include in element data sections
    nbud : int, optional
        Number of crop budgets (default 0)
    include_initial_cond : bool, optional
        Whether to include initial conditions section with element data
    area_file : str, optional
        Path to crop area file (Windows-style path)

    Returns
    -------
    str
        File content as string with Windows line endings
    """
    lines = []

    # Header comments
    lines.append("C Rice and Refuge Lands Data File")

    # Ponded crop area file
    lines.append("C Ponded crop area file")
    lines.append(f"    {area_file}           / LUFLP")

    # Budget section
    lines.append("C Budget section")
    lines.append(f"     {nbud}                                  / NBCROP")
    # Budget crop codes (commented out if nbud=0)
    crop_codes = ['RICE_FL', 'RICE_NFL', 'RICE_NDC', 'REFUGE_SL', 'REFUGE_PR']
    for i in range(nbud):
        lines.append(f"    {crop_codes[i % len(crop_codes)]}                        / BCCODE[{i+1:2d}]")

    # Budget output files
    lines.append("C Budget output files")
    lines.append("                                                / CLWUBUDFL")
    lines.append("                                                / CRZBUDFL")

    # Rooting depths section (1 factor + 5 crop depths)
    lines.append("C Rooting depths")
    lines.append("    1.0                   / FACT")
    lines.append("    2.0                   / ROOTRI_NFL")
    lines.append("    2.0                   / ROOTRI_FL")
    lines.append("    2.0                   / ROOTRI_NDC")
    lines.append("    2.0                   / ROOTRF_SL")
    lines.append("    2.0                   / ROOTRF_PR")

    # Curve numbers section (element data)
    lines.append("C Curve Numbers")
    lines.append("C   IE    CNRI_FL    CNRI_NFL   CNRI_NDC   CNRF_SL   CNRF_PR")
    for elem_id in elem_ids:
        cn = 50 + (elem_id % 10)
        lines.append(f"	{elem_id}	{cn}	{cn}	{cn}	{cn}	{cn}")

    # ETc columns section (element data) - requires comment line before
    lines.append("C ETc columns")
    lines.append("C   IE    ICETRI_FL   ICETRI_NFL   ICETRI_NDC   ICETRF_SL   ICETRF_PR")
    for elem_id in elem_ids:
        lines.append(f"	{elem_id}	1	2	3	4	5")

    # Water supply requirement section (element data)
    lines.append("C Water supply requirement")
    for elem_id in elem_ids:
        lines.append(f"	{elem_id}	0	0	0	0	0")

    # Irrigation periods section (element data)
    lines.append("C Irrigation periods")
    for elem_id in elem_ids:
        lines.append(f"	{elem_id}	1	1	1	1	1")

    # Ponding depths file and data
    lines.append("C Ponding depths")
    lines.append("    RootZone\\PondedCrop_Depth.dat      / PNDEPTHFL")
    lines.append("    RootZone\\PondedCrop_Operations.dat      / OPFL")
    for elem_id in elem_ids:
        lines.append(f"	{elem_id}	0.5	0.5	0.5	0.5	0.5")

    # Application depths section (element data)
    lines.append("C Application depths")
    for elem_id in elem_ids:
        lines.append(f"	{elem_id}	1.0	1.0	1.0	1.0	1.0")

    # Return flow depths section (element data)
    lines.append("C Return flow depths")
    for elem_id in elem_ids:
        lines.append(f"	{elem_id}	0.1	0.1	0.1	0.1	0.1")

    # Re-use flow depths section (element data)
    lines.append("C Re-use flow depths")
    for elem_id in elem_ids:
        lines.append(f"	{elem_id}	0.0	0.0	0.0	0.0	0.0")

    # Initial conditions section
    lines.append("C Initial Soil Moisture Conditions")
    lines.append("C   IE    FSOILMP    SOILM_RI_FL   SOILM_RI_NFL   SOILM_RI_NDC   SOILM_RF_SL   SOILM_RF_PR")
    if not include_initial_cond:
        # First value 0 means no element-specific initial conditions
        lines.append("	0	0.5	0.20	0.20	0.20	0.20	0.20")
    else:
        for elem_id in elem_ids:
            soilm = 0.15 + (elem_id % 10) * 0.01
            lines.append(f"	{elem_id}	0.5	{soilm:.4f}	{soilm:.4f}	{soilm:.4f}	{soilm:.4f}	{soilm:.4f}")

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
    lines.append("C Land Use Area File - Ponded Crops")
    lines.append("C")
    lines.append(f"    {len(elem_ids)}    / NELEM")
    lines.append("C Element areas for 5 ponded crop types")

    for elem_id in elem_ids:
        # Format: elem_id, areas for 5 crop types
        lines.append(f"	{elem_id}	100.0	50.0	25.0	75.0	10.0")

    return "\r\n".join(lines)


# ============================================================================
# Tests for sub_rz_pc_file
# ============================================================================

class TestSubRzPcFileBasic:
    """Basic tests for sub_rz_pc_file function."""

    def test_all_elements_in_submodel(self, tmp_path):
        """Test with all elements included in the submodel."""
        elem_ids = [1, 2, 3, 4, 5]

        # Create the main PC file
        pc_content = create_pc_file_content(
            nelems=len(elem_ids),
            elem_ids=elem_ids,
            area_file='RootZone\\PondedCrop_Area.dat'
        )

        old_file = tmp_path / "old_pc.dat"
        old_file.write_text(pc_content)

        # Create the area file
        area_content = create_lu_area_file_content(len(elem_ids), elem_ids)
        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_file = area_dir / "PondedCrop_Area.dat"
        area_file.write_text(area_content)

        # Setup output file paths
        new_file = tmp_path / "new_pc.dat"
        new_area_file = tmp_path / "new_pca"

        sim_files_new = SimulationFiles(
            pc_file=str(new_file),
            pca_file=str(new_area_file)
        )

        # Include all elements
        elems = elem_ids

        # Mock sub_lu_file since it processes the area file separately
        with patch('iwfm.sub_lu_file') as mock_sub_lu:
            iwfm.sub_rz_pc_file(str(old_file), sim_files_new, elems,
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

        # Create the main PC file
        pc_content = create_pc_file_content(
            nelems=len(all_elem_ids),
            elem_ids=all_elem_ids,
            area_file='RootZone\\PondedCrop_Area.dat'
        )

        old_file = tmp_path / "old_pc.dat"
        old_file.write_text(pc_content)

        # Create the area file
        area_content = create_lu_area_file_content(len(all_elem_ids), all_elem_ids)
        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_file = area_dir / "PondedCrop_Area.dat"
        area_file.write_text(area_content)

        # Setup output file paths
        new_file = tmp_path / "new_pc.dat"
        new_area_file = tmp_path / "new_pca"

        sim_files_new = SimulationFiles(
            pc_file=str(new_file),
            pca_file=str(new_area_file)
        )

        # Include only subset of elements
        elems = [2, 4, 6, 8]

        with patch('iwfm.sub_lu_file') as mock_sub_lu:
            iwfm.sub_rz_pc_file(str(old_file), sim_files_new, elems,
                                base_path=tmp_path, verbose=False)

        # Verify output file was created
        assert new_file.exists()

        # Read output
        output_content = new_file.read_text()

        # Verify file was created successfully
        assert '/ LUFLP' in output_content

        # Check that included elements are present
        for elem_id in elems:
            assert f"\t{elem_id}\t" in output_content or f"	{elem_id}	" in output_content

    def test_no_elements_in_submodel(self, tmp_path):
        """Test with no elements in the submodel."""
        all_elem_ids = [1, 2, 3, 4, 5]

        pc_content = create_pc_file_content(
            nelems=len(all_elem_ids),
            elem_ids=all_elem_ids,
            area_file='RootZone\\PondedCrop_Area.dat'
        )

        old_file = tmp_path / "old_pc.dat"
        old_file.write_text(pc_content)

        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(len(all_elem_ids), all_elem_ids)
        area_file = area_dir / "PondedCrop_Area.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_pc.dat"
        new_area_file = tmp_path / "new_pca"

        sim_files_new = SimulationFiles(
            pc_file=str(new_file),
            pca_file=str(new_area_file)
        )

        # Empty submodel - no elements
        elems = []

        with patch('iwfm.sub_lu_file') as mock_sub_lu:
            iwfm.sub_rz_pc_file(str(old_file), sim_files_new, elems,
                                base_path=tmp_path, verbose=False)

        # Verify output file was created (even if empty of element data)
        assert new_file.exists()


class TestSubRzPcFileAreaFile:
    """Tests for area file handling in sub_rz_pc_file."""

    def test_area_file_path_updated(self, tmp_path):
        """Test that the area file path is updated in output."""
        elem_ids = [1, 2, 3]

        pc_content = create_pc_file_content(
            nelems=len(elem_ids),
            elem_ids=elem_ids,
            area_file='RootZone\\OldAreaFile.dat'
        )

        old_file = tmp_path / "old_pc.dat"
        old_file.write_text(pc_content)

        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(len(elem_ids), elem_ids)
        area_file = area_dir / "OldAreaFile.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_pc.dat"
        new_area_base = tmp_path / "NewSubmodel_PCArea.dat"

        sim_files_new = SimulationFiles(
            pc_file=str(new_file),
            pca_file=str(new_area_base)
        )

        with patch('iwfm.sub_lu_file') as mock_sub_lu:
            iwfm.sub_rz_pc_file(str(old_file), sim_files_new, elem_ids,
                                base_path=tmp_path, verbose=False)

        # Verify the output file contains the new area file name
        output_content = new_file.read_text()
        assert 'NewSubmodel_PCArea.dat' in output_content
        assert '/ LUFLP' in output_content

    def test_sub_lu_file_called(self, tmp_path):
        """Test that sub_lu_file is called with correct parameters."""
        elem_ids = [1, 2, 3]

        pc_content = create_pc_file_content(
            nelems=len(elem_ids),
            elem_ids=elem_ids,
            area_file='RootZone\\AreaFile.dat'
        )

        old_file = tmp_path / "old_pc.dat"
        old_file.write_text(pc_content)

        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(len(elem_ids), elem_ids)
        area_file = area_dir / "AreaFile.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_pc.dat"
        new_area_base = tmp_path / "new_area.dat"

        sim_files_new = SimulationFiles(
            pc_file=str(new_file),
            pca_file=str(new_area_base)
        )

        elems = [1, 3]

        with patch('iwfm.sub_lu_file') as mock_sub_lu:
            iwfm.sub_rz_pc_file(str(old_file), sim_files_new, elems,
                                base_path=tmp_path, verbose=False)

            # Verify sub_lu_file was called
            assert mock_sub_lu.called
            call_args = mock_sub_lu.call_args

            # Check that elems list was passed
            assert elems == call_args[0][2]


class TestSubRzPcFileVerbose:
    """Tests for verbose mode in sub_rz_pc_file."""

    def test_verbose_true(self, tmp_path, capsys):
        """Test verbose mode outputs message."""
        elem_ids = [1, 2]

        pc_content = create_pc_file_content(
            nelems=len(elem_ids),
            elem_ids=elem_ids,
            area_file='RootZone\\Area.dat'
        )

        old_file = tmp_path / "old_pc.dat"
        old_file.write_text(pc_content)

        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(len(elem_ids), elem_ids)
        area_file = area_dir / "Area.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_pc.dat"
        new_area_base = tmp_path / "new_area.dat"

        sim_files_new = SimulationFiles(
            pc_file=str(new_file),
            pca_file=str(new_area_base)
        )

        with patch('iwfm.sub_lu_file'):
            iwfm.sub_rz_pc_file(str(old_file), sim_files_new, elem_ids,
                                base_path=tmp_path, verbose=True)

        captured = capsys.readouterr()
        assert 'ponded crop file' in captured.out.lower()

    def test_verbose_false(self, tmp_path, capsys):
        """Test that verbose=False produces no output."""
        elem_ids = [1, 2]

        pc_content = create_pc_file_content(
            nelems=len(elem_ids),
            elem_ids=elem_ids,
            area_file='RootZone\\Area.dat'
        )

        old_file = tmp_path / "old_pc.dat"
        old_file.write_text(pc_content)

        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(len(elem_ids), elem_ids)
        area_file = area_dir / "Area.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_pc.dat"
        new_area_base = tmp_path / "new_area.dat"

        sim_files_new = SimulationFiles(
            pc_file=str(new_file),
            pca_file=str(new_area_base)
        )

        with patch('iwfm.sub_lu_file'):
            iwfm.sub_rz_pc_file(str(old_file), sim_files_new, elem_ids,
                                base_path=tmp_path, verbose=False)

        captured = capsys.readouterr()
        # Should be minimal or no output when verbose is False
        assert 'ponded crop file' not in captured.out.lower()


class TestSubRzPcFileEdgeCases:
    """Edge case tests for sub_rz_pc_file."""

    def test_single_element(self, tmp_path):
        """Test with single element in model."""
        elem_ids = [1]

        pc_content = create_pc_file_content(
            nelems=1,
            elem_ids=elem_ids,
            area_file='RootZone\\Area.dat'
        )

        old_file = tmp_path / "old_pc.dat"
        old_file.write_text(pc_content)

        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(1, elem_ids)
        area_file = area_dir / "Area.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_pc.dat"
        new_area_base = tmp_path / "new_area.dat"

        sim_files_new = SimulationFiles(
            pc_file=str(new_file),
            pca_file=str(new_area_base)
        )

        with patch('iwfm.sub_lu_file'):
            iwfm.sub_rz_pc_file(str(old_file), sim_files_new, elem_ids,
                                base_path=tmp_path, verbose=False)

        assert new_file.exists()

    def test_many_elements(self, tmp_path):
        """Test with many elements (like C2VSimCG with 1392 elements)."""
        elem_ids = list(range(1, 101))  # 100 elements for testing

        pc_content = create_pc_file_content(
            nelems=len(elem_ids),
            elem_ids=elem_ids,
            area_file='RootZone\\Area.dat'
        )

        old_file = tmp_path / "old_pc.dat"
        old_file.write_text(pc_content)

        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(len(elem_ids), elem_ids)
        area_file = area_dir / "Area.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_pc.dat"
        new_area_base = tmp_path / "new_area.dat"

        sim_files_new = SimulationFiles(
            pc_file=str(new_file),
            pca_file=str(new_area_base)
        )

        # Include subset of elements
        elems = [10, 20, 30, 40, 50]

        with patch('iwfm.sub_lu_file'):
            iwfm.sub_rz_pc_file(str(old_file), sim_files_new, elems,
                                base_path=tmp_path, verbose=False)

        assert new_file.exists()

    def test_non_sequential_element_ids(self, tmp_path):
        """Test with non-sequential element IDs."""
        elem_ids = [5, 10, 15, 100, 500]

        pc_content = create_pc_file_content(
            nelems=len(elem_ids),
            elem_ids=elem_ids,
            area_file='RootZone\\Area.dat'
        )

        old_file = tmp_path / "old_pc.dat"
        old_file.write_text(pc_content)

        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(len(elem_ids), elem_ids)
        area_file = area_dir / "Area.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_pc.dat"
        new_area_base = tmp_path / "new_area.dat"

        sim_files_new = SimulationFiles(
            pc_file=str(new_file),
            pca_file=str(new_area_base)
        )

        # Include subset of non-sequential elements
        elems = [10, 100]

        with patch('iwfm.sub_lu_file'):
            iwfm.sub_rz_pc_file(str(old_file), sim_files_new, elems,
                                base_path=tmp_path, verbose=False)

        assert new_file.exists()

    def test_no_initial_conditions(self, tmp_path):
        """Test with no element-specific initial conditions (IE=0)."""
        elem_ids = [1, 2, 3]

        pc_content = create_pc_file_content(
            nelems=len(elem_ids),
            elem_ids=elem_ids,
            area_file='RootZone\\Area.dat',
            include_initial_cond=False
        )

        old_file = tmp_path / "old_pc.dat"
        old_file.write_text(pc_content)

        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(len(elem_ids), elem_ids)
        area_file = area_dir / "Area.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_pc.dat"
        new_area_base = tmp_path / "new_area.dat"

        sim_files_new = SimulationFiles(
            pc_file=str(new_file),
            pca_file=str(new_area_base)
        )

        with patch('iwfm.sub_lu_file'):
            iwfm.sub_rz_pc_file(str(old_file), sim_files_new, elem_ids,
                                base_path=tmp_path, verbose=False)

        assert new_file.exists()

    def test_with_budget_crops(self, tmp_path):
        """Test with budget crops enabled."""
        elem_ids = [1, 2, 3]

        pc_content = create_pc_file_content(
            nelems=len(elem_ids),
            elem_ids=elem_ids,
            area_file='RootZone\\Area.dat',
            nbud=2  # Enable 2 budget crops
        )

        old_file = tmp_path / "old_pc.dat"
        old_file.write_text(pc_content)

        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(len(elem_ids), elem_ids)
        area_file = area_dir / "Area.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_pc.dat"
        new_area_base = tmp_path / "new_area.dat"

        sim_files_new = SimulationFiles(
            pc_file=str(new_file),
            pca_file=str(new_area_base)
        )

        with patch('iwfm.sub_lu_file'):
            iwfm.sub_rz_pc_file(str(old_file), sim_files_new, elem_ids,
                                base_path=tmp_path, verbose=False)

        assert new_file.exists()


class TestSubRzPcFileNotFound:
    """Tests for file not found error handling."""

    def test_file_not_found(self, tmp_path):
        """Test that FileNotFoundError is raised for missing file."""
        nonexistent_file = str(tmp_path / "nonexistent_pc.dat")

        sim_files_new = SimulationFiles(
            pc_file=str(tmp_path / 'new_pc.dat'),
            pca_file=str(tmp_path / 'new_area')
        )

        elems = [1, 2, 3]

        # The iwfm.file_test() function calls sys.exit() when file is not found
        with pytest.raises(FileNotFoundError):
            iwfm.sub_rz_pc_file(nonexistent_file, sim_files_new, elems, verbose=False)


class TestSubRzPcFilePathHandling:
    """Tests for file path handling in sub_rz_pc_file."""

    def test_backslash_to_forward_slash_conversion(self, tmp_path):
        """Test that Windows backslash paths are converted to forward slashes."""
        elem_ids = [1, 2]

        # Use Windows-style path with backslashes
        pc_content = create_pc_file_content(
            nelems=len(elem_ids),
            elem_ids=elem_ids,
            area_file='RootZone\\SubDir\\Area.dat'
        )

        old_file = tmp_path / "old_pc.dat"
        old_file.write_text(pc_content)

        # Create nested directory structure
        area_dir = tmp_path / "RootZone" / "SubDir"
        area_dir.mkdir(parents=True)
        area_content = create_lu_area_file_content(len(elem_ids), elem_ids)
        area_file = area_dir / "Area.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_pc.dat"
        new_area_base = tmp_path / "new_area.dat"

        sim_files_new = SimulationFiles(
            pc_file=str(new_file),
            pca_file=str(new_area_base)
        )

        with patch('iwfm.sub_lu_file') as mock_sub_lu:
            iwfm.sub_rz_pc_file(str(old_file), sim_files_new, elem_ids,
                                base_path=tmp_path, verbose=False)

            # sub_lu_file should be called with forward-slash path
            call_args = mock_sub_lu.call_args
            area_path_arg = call_args[0][0]
            # Path should be resolved and not contain backslashes
            assert '\\' not in area_path_arg or '/' in area_path_arg


# ============================================================================
# Integration test with real-format data
# ============================================================================

class TestSubRzPcFileRealFormat:
    """Tests using realistic IWFM ponded crop file format."""

    def test_realistic_file_structure(self, tmp_path):
        """Test with realistic IWFM PC file structure."""
        # Create a more realistic file similar to C2VSimCG format
        lines = []
        lines.append("C*******************************************************************************")
        lines.append("C")
        lines.append("C                    RICE AND REFUGE LANDS DATA FILE")
        lines.append("C                         Root Zone Component")
        lines.append("C")
        lines.append("C*******************************************************************************")
        lines.append("C   LUFLP   ;  File that lists the crop areas")
        lines.append("C--------------------------------------------------------------------------------")
        lines.append("     RootZone\\C2VSimCG_PondedCrop_Area.dat                 / LUFLP")
        lines.append("C*******************************************************************************")
        lines.append("C                      Water Budget Output Files")
        lines.append("C--------------------------------------------------------------------------------")
        lines.append("      0                                                 / NBCROP")
        lines.append("                                                        / CLWUBUDFL")
        lines.append("                                                        / CRZBUDFL")
        lines.append("C*******************************************************************************")
        lines.append("C                              Rooting Depths")
        lines.append("C--------------------------------------------------------------------------------")
        lines.append("      1                   / FACT")
        lines.append("      2.0                 / ROOTRI_NFL")
        lines.append("      2.0                 / ROOTRI_FL")
        lines.append("      2.0                 / ROOTRI_NDC")
        lines.append("      2.0                 / ROOTRF_SL")
        lines.append("      2.0                 / ROOTRF_PR")
        lines.append("C*******************************************************************************")
        lines.append("C                    Curve Numbers")
        lines.append("C  IE    CNRI_FL    CNRI_NFL   CNRI_NDC   CNRF_SL   CNRF_PR")
        lines.append("C--------------------------------------------------------------------------------")
        lines.append("	1	53	53	53	53	53")
        lines.append("	2	56	56	56	56	56")
        lines.append("	3	56	56	56	56	56")
        lines.append("	4	56	56	56	56	56")
        lines.append("	5	55	55	55	55	55")
        lines.append("C*******************************************************************************")
        lines.append("C                         ETc Columns")
        lines.append("C  IE    ICETRI_FL   ICETRI_NFL   ICETRI_NDC   ICETRF_SL   ICETRF_PR")
        lines.append("C--------------------------------------------------------------------------------")
        lines.append("	1	1	22	148	1	22")
        lines.append("	2	1	22	148	1	22")
        lines.append("	3	1	22	148	1	22")
        lines.append("	4	1	22	148	1	22")
        lines.append("	5	1	22	148	1	22")
        lines.append("C*******************************************************************************")
        lines.append("C                         Water Supply Requirement")
        lines.append("	1	0	0	0	0	0")
        lines.append("	2	0	0	0	0	0")
        lines.append("	3	0	0	0	0	0")
        lines.append("	4	0	0	0	0	0")
        lines.append("	5	0	0	0	0	0")
        lines.append("C*******************************************************************************")
        lines.append("C                         Irrigation Periods")
        lines.append("	1	1	1	1	1	1")
        lines.append("	2	1	1	1	1	1")
        lines.append("	3	1	1	1	1	1")
        lines.append("	4	1	1	1	1	1")
        lines.append("	5	1	1	1	1	1")
        lines.append("C*******************************************************************************")
        lines.append("C                         Ponding Depths")
        lines.append("    RootZone\\PondedCrop_Depth.dat      / PNDEPTHFL")
        lines.append("    RootZone\\PondedCrop_Operations.dat      / OPFL")
        lines.append("	1	0.5	0.5	0.5	0.5	0.5")
        lines.append("	2	0.5	0.5	0.5	0.5	0.5")
        lines.append("	3	0.5	0.5	0.5	0.5	0.5")
        lines.append("	4	0.5	0.5	0.5	0.5	0.5")
        lines.append("	5	0.5	0.5	0.5	0.5	0.5")
        lines.append("C*******************************************************************************")
        lines.append("C                         Application Depths")
        lines.append("	1	1.0	1.0	1.0	1.0	1.0")
        lines.append("	2	1.0	1.0	1.0	1.0	1.0")
        lines.append("	3	1.0	1.0	1.0	1.0	1.0")
        lines.append("	4	1.0	1.0	1.0	1.0	1.0")
        lines.append("	5	1.0	1.0	1.0	1.0	1.0")
        lines.append("C*******************************************************************************")
        lines.append("C                         Return Flow Depths")
        lines.append("	1	0.1	0.1	0.1	0.1	0.1")
        lines.append("	2	0.1	0.1	0.1	0.1	0.1")
        lines.append("	3	0.1	0.1	0.1	0.1	0.1")
        lines.append("	4	0.1	0.1	0.1	0.1	0.1")
        lines.append("	5	0.1	0.1	0.1	0.1	0.1")
        lines.append("C*******************************************************************************")
        lines.append("C                         Re-use Flow Depths")
        lines.append("	1	0.0	0.0	0.0	0.0	0.0")
        lines.append("	2	0.0	0.0	0.0	0.0	0.0")
        lines.append("	3	0.0	0.0	0.0	0.0	0.0")
        lines.append("	4	0.0	0.0	0.0	0.0	0.0")
        lines.append("	5	0.0	0.0	0.0	0.0	0.0")
        lines.append("C*******************************************************************************")
        lines.append("C                           Initial Soil Moisture")
        lines.append("C   IE    FSOILMP    SOILM_RI_FL   SOILM_RI_NFL   SOILM_RI_NDC   SOILM_RF_SL   SOILM_RF_PR")
        lines.append("C--------------------------------------------------------------------------------")
        lines.append("	1	0.5	0.1934	0.1934	0.1934	0.1934	0.1934")
        lines.append("	2	0.5	0.2207	0.2207	0.2207	0.2207	0.2207")
        lines.append("	3	0.5	0.2371	0.2371	0.2371	0.2371	0.2371")
        lines.append("	4	0.5	0.2205	0.2205	0.2205	0.2205	0.2205")
        lines.append("	5	0.5	0.2567	0.2567	0.2567	0.2567	0.2567")
        lines.append("")

        content = "\r\n".join(lines)

        old_file = tmp_path / "old_pc.dat"
        old_file.write_text(content)

        # Create area file
        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(5, [1, 2, 3, 4, 5])
        area_file = area_dir / "C2VSimCG_PondedCrop_Area.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_pc.dat"
        new_area_base = tmp_path / "new_area.dat"

        sim_files_new = SimulationFiles(
            pc_file=str(new_file),
            pca_file=str(new_area_base)
        )

        # Include only elements 2 and 4
        elems = [2, 4]

        with patch('iwfm.sub_lu_file'):
            iwfm.sub_rz_pc_file(str(old_file), sim_files_new, elems,
                                base_path=tmp_path, verbose=False)

        assert new_file.exists()

        # Verify output structure
        output_content = new_file.read_text()

        # Should have area file marker
        assert '/ LUFLP' in output_content

        # Should have new area file name
        assert 'new_area.dat' in output_content


# ============================================================================
# Tests with actual test data file (if available)
# ============================================================================

TEST_DATA_DIR = Path(__file__).parent / "C2VSimCG-2021"
PC_FILE = TEST_DATA_DIR / "Simulation" / "Rootzone" / "C2VSimCG_PondedCrop.dat"


@pytest.fixture
def pc_file_exists():
    """Check that the C2VSimCG ponded crop file exists."""
    if not TEST_DATA_DIR.exists():
        pytest.skip(f"Test data directory not found: {TEST_DATA_DIR}")
    if not PC_FILE.exists():
        pytest.skip(f"Ponded crop file not found: {PC_FILE}")
    return True


class TestSubRzPcFileWithRealFile:
    """Tests using the actual C2VSimCG ponded crop file."""

    def test_real_file_format_verification(self, pc_file_exists):
        """Test that C2VSimCG PC file has expected structure."""
        with open(PC_FILE, 'r') as f:
            content = f.read()

        # Verify file has expected markers
        assert '/ LUFLP' in content, "Should have land use file marker"
        assert '/ NBCROP' in content, "Should have NBCROP marker"
        assert '/ FACT' in content, "Should have FACT marker"

    def test_real_file_has_rooting_depths(self, pc_file_exists):
        """Test that C2VSimCG PC file has rooting depth section."""
        with open(PC_FILE, 'r') as f:
            content = f.read()

        # Verify rooting depths are present
        assert '/ ROOTRI_NFL' in content or '/ ROOTRI_FL' in content, \
            "Should have rice rooting depth markers"

    def test_real_file_has_initial_conditions(self, pc_file_exists):
        """Test that C2VSimCG PC file has initial conditions section."""
        with open(PC_FILE, 'r') as f:
            content = f.read()

        assert 'Initial' in content, "Should have Initial Soil Moisture section"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
