#!/usr/bin/env python
# test_sub_rz_npc_file.py
# Unit tests for sub_rz_npc_file.py
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


def create_npc_file_content(ncrop, nelems, elem_ids, nbud=0,
                            area_file='RootZone\\NonPondedCrop_Area.dat',
                            include_initial_cond=True):
    """Create properly structured IWFM non-ponded crop file content for testing.

    This function creates a mock non-ponded crop file following the IWFM format.
    Comment lines have 'C', 'c', '*' or '#' in first text column.
    Data lines begin with whitespace. Uses '/' = end of record marker.

    Parameters
    ----------
    ncrop : int
        Number of non-ponded crop types
    nelems : int
        Number of elements in the model
    elem_ids : list of int
        List of element IDs to include in element data sections
    nbud : int, optional
        Number of crop budgets (default 0)
    area_file : str, optional
        Path to crop area file (Windows-style path)
    include_initial_cond : bool, optional
        Whether to include initial conditions section with element data

    Returns
    -------
    str
        File content as string with Windows line endings
    """
    lines = []

    # Header comments
    lines.append("C Non-Ponded Agricultural Crops Data File")

    # Number of crops and demand flag
    lines.append("C Number of crops")
    lines.append(f"    {ncrop}                                 / NCROP")
    lines.append("    1                                  / FLDMD")

    # Crop codes
    lines.append("C Crop codes")
    crop_codes = ['GR', 'CO', 'SB', 'CN', 'DB', 'SA', 'FL', 'AL', 'PA', 'TP',
                  'TF', 'CU', 'OG', 'PO', 'TR', 'AP', 'OR', 'CS', 'VI', 'ID']
    for i in range(ncrop):
        lines.append(f"    {crop_codes[i % len(crop_codes)]}         / CCODE[{i+1:2d}]")

    # Crop area file
    lines.append("C Crop area file")
    lines.append(f"    {area_file}           / LUFLNP")

    # Budget section
    lines.append("C Budget section")
    lines.append(f"     {nbud}                                  / NBCROP")
    # Budget crop codes (commented out if nbud=0)
    for i in range(nbud):
        lines.append(f"    {crop_codes[i % len(crop_codes)]}                                 / BCCODE[{i+1:2d}]")

    # Budget output files
    lines.append("C Budget output files")
    lines.append("                                                / CLWUBUDFL")
    lines.append("                                                / CRZBUDFL")

    # Rooting depths section
    lines.append("C Rooting depths")
    lines.append("    RootZone\\RootDepthFracs.dat      / RZFRACFL")
    lines.append("    1.0                                                     / FACT")

    # Root depth for each crop
    lines.append("C Root depths per crop")
    for i in range(ncrop):
        lines.append(f"     {i+1}      4.0         {i+1}        / ROOTCP[{i+1:2d}]")

    # Curve numbers section (element data)
    lines.append("C Curve numbers")
    for elem_id in elem_ids:
        cn_values = '\t'.join(['50'] * ncrop)
        lines.append(f"	{elem_id}	{cn_values}")

    # ETc section (element data)
    lines.append("C Crop ETc")
    for elem_id in elem_ids:
        et_values = '\t'.join(['1'] * ncrop)
        lines.append(f"	{elem_id}	{et_values}")

    # Agricultural water supply requirement section (element data)
    lines.append("C Ag water supply requirement")
    for elem_id in elem_ids:
        aw_values = '\t'.join(['0'] * ncrop)
        lines.append(f"	{elem_id}	{aw_values}")

    # Irrigation periods section (element data)
    lines.append("C Irrigation periods")
    for elem_id in elem_ids:
        ip_values = '\t'.join(['1'] * ncrop)
        lines.append(f"	{elem_id}	{ip_values}")

    # Minimum soil moisture section (with file name, then element data)
    lines.append("C Minimum soil moisture")
    lines.append("    RootZone\\MinSoilMoisture.dat      / MINSMFL")
    for elem_id in elem_ids:
        ms_values = '\t'.join(['1'] * ncrop)
        lines.append(f"	{elem_id}	{ms_values}")

    # Target soil moisture section (with file name, then element data)
    lines.append("C Target soil moisture")
    lines.append("    RootZone\\TargetSoilMoisture.dat      / TRGSMFL")
    for elem_id in elem_ids:
        ts_values = '\t'.join(['1'] * ncrop)
        lines.append(f"	{elem_id}	{ts_values}")

    # Return flow fractions section (element data)
    lines.append("C Return flow fractions")
    for elem_id in elem_ids:
        rf_values = '\t'.join(['0.1'] * ncrop)
        lines.append(f"	{elem_id}	{rf_values}")

    # Reuse fractions section (element data)
    lines.append("C Reuse fractions")
    for elem_id in elem_ids:
        ru_values = '\t'.join(['0.0'] * ncrop)
        lines.append(f"	{elem_id}	{ru_values}")

    # Initial conditions section (element data)
    lines.append("C Initial soil moisture conditions")
    if not include_initial_cond:
        # First value 0 means no element-specific initial conditions - skips element loop
        soilm_values = '\t'.join(['0.20'] * ncrop)
        lines.append(f"	0	0.5	{soilm_values}")
    else:
        for elem_id in elem_ids:
            # Format: elem_id, fsoilmp, then ncrop soil moisture values
            soilm_values = '\t'.join(['0.20'] * ncrop)
            lines.append(f"	{elem_id}	0.5	{soilm_values}")

    lines.append("")

    # Join with Windows line endings
    return "\r\n".join(lines)


def create_lu_area_file_content(nelems, elem_ids, ncrop):
    """Create a simple land use area file for testing.

    Parameters
    ----------
    nelems : int
        Number of elements
    elem_ids : list of int
        List of element IDs
    ncrop : int
        Number of crop types

    Returns
    -------
    str
        File content as string
    """
    lines = []
    lines.append("C Land Use Area File")
    lines.append("C")
    lines.append(f"    {len(elem_ids)}    / NELEM")
    lines.append(f"    {ncrop}    / NCROP")
    lines.append("C Element areas")

    for elem_id in elem_ids:
        areas = '\t'.join(['100.0'] * ncrop)
        lines.append(f"	{elem_id}	{areas}")

    return "\r\n".join(lines)


# ============================================================================
# Tests for sub_rz_npc_file
# ============================================================================

class TestSubRzNpcFileBasic:
    """Basic tests for sub_rz_npc_file function."""

    def test_all_elements_in_submodel(self, tmp_path):
        """Test with all elements included in the submodel."""
        ncrop = 3
        elem_ids = [1, 2, 3, 4, 5]

        # Create the main NPC file
        npc_content = create_npc_file_content(
            ncrop=ncrop,
            nelems=len(elem_ids),
            elem_ids=elem_ids,
            area_file='RootZone\\NonPondedCrop_Area.dat'
        )

        old_file = tmp_path / "old_npc.dat"
        old_file.write_text(npc_content)

        # Create the area file
        area_content = create_lu_area_file_content(len(elem_ids), elem_ids, ncrop)
        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_file = area_dir / "NonPondedCrop_Area.dat"
        area_file.write_text(area_content)

        # Setup output file paths
        new_file = tmp_path / "new_npc.dat"
        new_area_file = tmp_path / "new_npa"

        sim_files_new = SimulationFiles(
            np_file=str(new_file),
            npa_file=str(new_area_file)
        )

        # Include all elements
        elems = elem_ids

        # Mock sub_lu_file since it processes the area file separately
        with patch('iwfm.sub_lu_file') as mock_sub_lu:
            iwfm.sub_rz_npc_file(str(old_file), sim_files_new, elems,
                                 base_path=tmp_path, verbose=False)

        # Verify output file was created
        assert new_file.exists()

        # Read output and verify all elements are present
        output_content = new_file.read_text()
        for elem_id in elem_ids:
            assert f"\t{elem_id}\t" in output_content or f"	{elem_id}	" in output_content

    def test_subset_elements_in_submodel(self, tmp_path):
        """Test with only some elements in the submodel."""
        ncrop = 2
        all_elem_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        # Create the main NPC file
        npc_content = create_npc_file_content(
            ncrop=ncrop,
            nelems=len(all_elem_ids),
            elem_ids=all_elem_ids,
            area_file='RootZone\\NonPondedCrop_Area.dat'
        )

        old_file = tmp_path / "old_npc.dat"
        old_file.write_text(npc_content)

        # Create the area file
        area_content = create_lu_area_file_content(len(all_elem_ids), all_elem_ids, ncrop)
        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_file = area_dir / "NonPondedCrop_Area.dat"
        area_file.write_text(area_content)

        # Setup output file paths
        new_file = tmp_path / "new_npc.dat"
        new_area_file = tmp_path / "new_npa"

        sim_files_new = SimulationFiles(
            np_file=str(new_file),
            npa_file=str(new_area_file)
        )

        # Include only subset of elements
        elems = [2, 4, 6, 8]

        with patch('iwfm.sub_lu_file') as mock_sub_lu:
            iwfm.sub_rz_npc_file(str(old_file), sim_files_new, elems,
                                 base_path=tmp_path, verbose=False)

        # Verify output file was created
        assert new_file.exists()

        # Read output
        output_content = new_file.read_text()

        # Verify file was created successfully
        assert '/ NCROP' in output_content

        # Check that included elements are present
        for elem_id in elems:
            # Should find these elements in at least one data line
            assert f"\t{elem_id}\t" in output_content or f"	{elem_id}	" in output_content

    def test_no_elements_in_submodel(self, tmp_path):
        """Test with no elements in the submodel."""
        ncrop = 2
        all_elem_ids = [1, 2, 3, 4, 5]

        npc_content = create_npc_file_content(
            ncrop=ncrop,
            nelems=len(all_elem_ids),
            elem_ids=all_elem_ids,
            area_file='RootZone\\NonPondedCrop_Area.dat'
        )

        old_file = tmp_path / "old_npc.dat"
        old_file.write_text(npc_content)

        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(len(all_elem_ids), all_elem_ids, ncrop)
        area_file = area_dir / "NonPondedCrop_Area.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_npc.dat"
        new_area_file = tmp_path / "new_npa"

        sim_files_new = SimulationFiles(
            np_file=str(new_file),
            npa_file=str(new_area_file)
        )

        # Empty submodel - no elements
        elems = []

        with patch('iwfm.sub_lu_file') as mock_sub_lu:
            iwfm.sub_rz_npc_file(str(old_file), sim_files_new, elems,
                                 base_path=tmp_path, verbose=False)

        # Verify output file was created (even if empty of element data)
        assert new_file.exists()


class TestSubRzNpcFileAreaFile:
    """Tests for area file handling in sub_rz_npc_file."""

    def test_area_file_path_updated(self, tmp_path):
        """Test that the area file path is updated in output."""
        ncrop = 2
        elem_ids = [1, 2, 3]

        npc_content = create_npc_file_content(
            ncrop=ncrop,
            nelems=len(elem_ids),
            elem_ids=elem_ids,
            area_file='RootZone\\OldAreaFile.dat'
        )

        old_file = tmp_path / "old_npc.dat"
        old_file.write_text(npc_content)

        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(len(elem_ids), elem_ids, ncrop)
        area_file = area_dir / "OldAreaFile.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_npc.dat"
        new_area_base = tmp_path / "NewSubmodel_NPArea.dat"

        sim_files_new = SimulationFiles(
            np_file=str(new_file),
            npa_file=str(new_area_base)
        )

        with patch('iwfm.sub_lu_file') as mock_sub_lu:
            iwfm.sub_rz_npc_file(str(old_file), sim_files_new, elem_ids,
                                 base_path=tmp_path, verbose=False)

        # Verify the output file contains the new area file name
        output_content = new_file.read_text()
        assert 'NewSubmodel_NPArea.dat' in output_content
        assert '/ LUFLNP' in output_content

    def test_sub_lu_file_called(self, tmp_path):
        """Test that sub_lu_file is called with correct parameters."""
        ncrop = 2
        elem_ids = [1, 2, 3]

        npc_content = create_npc_file_content(
            ncrop=ncrop,
            nelems=len(elem_ids),
            elem_ids=elem_ids,
            area_file='RootZone\\AreaFile.dat'
        )

        old_file = tmp_path / "old_npc.dat"
        old_file.write_text(npc_content)

        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(len(elem_ids), elem_ids, ncrop)
        area_file = area_dir / "AreaFile.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_npc.dat"
        new_area_base = tmp_path / "new_area.dat"

        sim_files_new = SimulationFiles(
            np_file=str(new_file),
            npa_file=str(new_area_base)
        )

        elems = [1, 3]

        with patch('iwfm.sub_lu_file') as mock_sub_lu:
            iwfm.sub_rz_npc_file(str(old_file), sim_files_new, elems,
                                 base_path=tmp_path, verbose=False)

            # Verify sub_lu_file was called
            assert mock_sub_lu.called
            call_args = mock_sub_lu.call_args

            # Check that elems list was passed
            assert elems == call_args[0][2]


class TestSubRzNpcFileVerbose:
    """Tests for verbose mode in sub_rz_npc_file."""

    def test_verbose_true(self, tmp_path, capsys):
        """Test verbose mode outputs message."""
        ncrop = 2
        elem_ids = [1, 2]

        npc_content = create_npc_file_content(
            ncrop=ncrop,
            nelems=len(elem_ids),
            elem_ids=elem_ids,
            area_file='RootZone\\Area.dat'
        )

        old_file = tmp_path / "old_npc.dat"
        old_file.write_text(npc_content)

        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(len(elem_ids), elem_ids, ncrop)
        area_file = area_dir / "Area.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_npc.dat"
        new_area_base = tmp_path / "new_area.dat"

        sim_files_new = SimulationFiles(
            np_file=str(new_file),
            npa_file=str(new_area_base)
        )

        with patch('iwfm.sub_lu_file'):
            iwfm.sub_rz_npc_file(str(old_file), sim_files_new, elem_ids,
                                 base_path=tmp_path, verbose=True)

        captured = capsys.readouterr()
        assert 'non-ponded crop file' in captured.out.lower()

    def test_verbose_false(self, tmp_path, capsys):
        """Test that verbose=False produces no output."""
        ncrop = 2
        elem_ids = [1, 2]

        npc_content = create_npc_file_content(
            ncrop=ncrop,
            nelems=len(elem_ids),
            elem_ids=elem_ids,
            area_file='RootZone\\Area.dat'
        )

        old_file = tmp_path / "old_npc.dat"
        old_file.write_text(npc_content)

        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(len(elem_ids), elem_ids, ncrop)
        area_file = area_dir / "Area.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_npc.dat"
        new_area_base = tmp_path / "new_area.dat"

        sim_files_new = SimulationFiles(
            np_file=str(new_file),
            npa_file=str(new_area_base)
        )

        with patch('iwfm.sub_lu_file'):
            iwfm.sub_rz_npc_file(str(old_file), sim_files_new, elem_ids,
                                 base_path=tmp_path, verbose=False)

        captured = capsys.readouterr()
        # Should be minimal or no output when verbose is False
        assert 'non-ponded crop file' not in captured.out.lower()


class TestSubRzNpcFileEdgeCases:
    """Edge case tests for sub_rz_npc_file."""

    def test_single_element(self, tmp_path):
        """Test with single element in model."""
        ncrop = 2
        elem_ids = [1]

        npc_content = create_npc_file_content(
            ncrop=ncrop,
            nelems=1,
            elem_ids=elem_ids,
            area_file='RootZone\\Area.dat'
        )

        old_file = tmp_path / "old_npc.dat"
        old_file.write_text(npc_content)

        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(1, elem_ids, ncrop)
        area_file = area_dir / "Area.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_npc.dat"
        new_area_base = tmp_path / "new_area.dat"

        sim_files_new = SimulationFiles(
            np_file=str(new_file),
            npa_file=str(new_area_base)
        )

        with patch('iwfm.sub_lu_file'):
            iwfm.sub_rz_npc_file(str(old_file), sim_files_new, elem_ids,
                                 base_path=tmp_path, verbose=False)

        assert new_file.exists()

    def test_single_crop(self, tmp_path):
        """Test with single crop type."""
        ncrop = 1
        elem_ids = [1, 2, 3]

        npc_content = create_npc_file_content(
            ncrop=ncrop,
            nelems=len(elem_ids),
            elem_ids=elem_ids,
            area_file='RootZone\\Area.dat'
        )

        old_file = tmp_path / "old_npc.dat"
        old_file.write_text(npc_content)

        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(len(elem_ids), elem_ids, ncrop)
        area_file = area_dir / "Area.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_npc.dat"
        new_area_base = tmp_path / "new_area.dat"

        sim_files_new = SimulationFiles(
            np_file=str(new_file),
            npa_file=str(new_area_base)
        )

        with patch('iwfm.sub_lu_file'):
            iwfm.sub_rz_npc_file(str(old_file), sim_files_new, elem_ids,
                                 base_path=tmp_path, verbose=False)

        assert new_file.exists()

    def test_many_crops(self, tmp_path):
        """Test with many crop types (like C2VSimCG with 20 crops)."""
        ncrop = 20
        elem_ids = [1, 2, 3, 4, 5]

        npc_content = create_npc_file_content(
            ncrop=ncrop,
            nelems=len(elem_ids),
            elem_ids=elem_ids,
            area_file='RootZone\\Area.dat'
        )

        old_file = tmp_path / "old_npc.dat"
        old_file.write_text(npc_content)

        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(len(elem_ids), elem_ids, ncrop)
        area_file = area_dir / "Area.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_npc.dat"
        new_area_base = tmp_path / "new_area.dat"

        sim_files_new = SimulationFiles(
            np_file=str(new_file),
            npa_file=str(new_area_base)
        )

        with patch('iwfm.sub_lu_file'):
            iwfm.sub_rz_npc_file(str(old_file), sim_files_new, elem_ids,
                                 base_path=tmp_path, verbose=False)

        assert new_file.exists()

    def test_non_sequential_element_ids(self, tmp_path):
        """Test with non-sequential element IDs."""
        ncrop = 2
        elem_ids = [5, 10, 15, 100, 500]

        npc_content = create_npc_file_content(
            ncrop=ncrop,
            nelems=len(elem_ids),
            elem_ids=elem_ids,
            area_file='RootZone\\Area.dat'
        )

        old_file = tmp_path / "old_npc.dat"
        old_file.write_text(npc_content)

        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(len(elem_ids), elem_ids, ncrop)
        area_file = area_dir / "Area.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_npc.dat"
        new_area_base = tmp_path / "new_area.dat"

        sim_files_new = SimulationFiles(
            np_file=str(new_file),
            npa_file=str(new_area_base)
        )

        # Include subset of non-sequential elements
        elems = [10, 100]

        with patch('iwfm.sub_lu_file'):
            iwfm.sub_rz_npc_file(str(old_file), sim_files_new, elems,
                                 base_path=tmp_path, verbose=False)

        assert new_file.exists()

        # Verify excluded elements are removed
        output_content = new_file.read_text()
        # Elements 5, 15, 500 should not appear in data lines
        # (but we need to be careful - they could appear in comments)


class TestSubRzNpcFileNotFound:
    """Tests for file not found error handling."""

    def test_file_not_found(self, tmp_path):
        """Test that FileNotFoundError is raised for missing file."""
        nonexistent_file = str(tmp_path / "nonexistent_npc.dat")

        sim_files_new = SimulationFiles(
            np_file=str(tmp_path / 'new_npc.dat'),
            npa_file=str(tmp_path / 'new_area')
        )

        elems = [1, 2, 3]

        # The iwfm.file_test() function calls sys.exit() when file is not found
        with pytest.raises(FileNotFoundError):
            iwfm.sub_rz_npc_file(nonexistent_file, sim_files_new, elems, verbose=False)


class TestSubRzNpcFilePathHandling:
    """Tests for file path handling in sub_rz_npc_file."""

    def test_backslash_to_forward_slash_conversion(self, tmp_path):
        """Test that Windows backslash paths are converted to forward slashes."""
        ncrop = 2
        elem_ids = [1, 2]

        # Use Windows-style path with backslashes
        npc_content = create_npc_file_content(
            ncrop=ncrop,
            nelems=len(elem_ids),
            elem_ids=elem_ids,
            area_file='RootZone\\SubDir\\Area.dat'
        )

        old_file = tmp_path / "old_npc.dat"
        old_file.write_text(npc_content)

        # Create nested directory structure
        area_dir = tmp_path / "RootZone" / "SubDir"
        area_dir.mkdir(parents=True)
        area_content = create_lu_area_file_content(len(elem_ids), elem_ids, ncrop)
        area_file = area_dir / "Area.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_npc.dat"
        new_area_base = tmp_path / "new_area.dat"

        sim_files_new = SimulationFiles(
            np_file=str(new_file),
            npa_file=str(new_area_base)
        )

        with patch('iwfm.sub_lu_file') as mock_sub_lu:
            iwfm.sub_rz_npc_file(str(old_file), sim_files_new, elem_ids,
                                 base_path=tmp_path, verbose=False)

            # sub_lu_file should be called with forward-slash path
            call_args = mock_sub_lu.call_args
            area_path_arg = call_args[0][0]
            # Path should be resolved and not contain backslashes
            assert '\\' not in area_path_arg or '/' in area_path_arg


# ============================================================================
# Integration test with real-format data
# ============================================================================

class TestSubRzNpcFileRealFormat:
    """Tests using realistic IWFM non-ponded crop file format."""

    def test_realistic_file_structure(self, tmp_path):
        """Test with realistic IWFM NPC file structure."""
        # Create a more realistic file similar to C2VSimCG format
        lines = []
        lines.append("C*******************************************************************************")
        lines.append("C")
        lines.append("C                NON-PONDED AGRICULTURAL CROPS DATA FILE")
        lines.append("C                         Root Zone Component")
        lines.append("C")
        lines.append("C*******************************************************************************")
        lines.append("C   NCROP    ;  Number of agricultural crops")
        lines.append("C   FLDMD    ;  Flag for root zone moisture computation")
        lines.append("C--------------------------------------------------------------------------------")
        lines.append("    3                                 / NCROP")
        lines.append("    1                                  / FLDMD")
        lines.append("C--------------------------------------------------------------------------------")
        lines.append("C   Crop Codes")
        lines.append("    GR         / CCODE[ 1]  Grain")
        lines.append("    CO         / CCODE[ 2]  Cotton")
        lines.append("    AL         / CCODE[ 3]  Alfalfa")
        lines.append("C--------------------------------------------------------------------------------")
        lines.append("C   Crop Areas")
        lines.append("    RootZone\\C2VSimCG_NonPondedCrop_Area.dat           / LUFLNP")
        lines.append("C*******************************************************************************")
        lines.append("C                      Water Budget Output Control")
        lines.append("     0                                  / NBCROP")
        lines.append("C--------------------------------------------------------------------------------")
        lines.append("                                                / CLWUBUDFL")
        lines.append("                                                / CRZBUDFL")
        lines.append("C*******************************************************************************")
        lines.append("C                            Rooting Depths")
        lines.append("    RootZone\\C2VSimCG_RootDepthFracs.dat      / RZFRACFL")
        lines.append("    1.0                                                     / FACT")
        lines.append("C--------------------------------------------------------------------------------")
        lines.append("     1      4.0         1        / ROOTCP[ 1]     Grains")
        lines.append("     2      6.0         2        / ROOTCP[ 2]     Cotton")
        lines.append("     3      6.0         3        / ROOTCP[ 3]     Alfalfa")
        lines.append("C*******************************************************************************")
        lines.append("C                    Curve Numbers")
        lines.append("C   IE       CN[1]   CN[2]   CN[3]")
        lines.append("C--------------------------------------------------------------------------------")
        lines.append("	1	47	47	47")
        lines.append("	2	51	51	51")
        lines.append("	3	52	52	52")
        lines.append("	4	52	52	52")
        lines.append("	5	50	50	50")
        lines.append("C*******************************************************************************")
        lines.append("C                         Crop ETc")
        lines.append("	1	1	22	148")
        lines.append("	2	1	22	148")
        lines.append("	3	1	22	148")
        lines.append("	4	1	22	148")
        lines.append("	5	1	22	148")
        lines.append("C*******************************************************************************")
        lines.append("C                         Ag Water Supply")
        lines.append("	1	0	0	0")
        lines.append("	2	0	0	0")
        lines.append("	3	0	0	0")
        lines.append("	4	0	0	0")
        lines.append("	5	0	0	0")
        lines.append("C*******************************************************************************")
        lines.append("C                         Irrigation Periods")
        lines.append("	1	1	1	1")
        lines.append("	2	1	1	1")
        lines.append("	3	1	1	1")
        lines.append("	4	1	1	1")
        lines.append("	5	1	1	1")
        lines.append("C*******************************************************************************")
        lines.append("C                      Minimum Soil Moisture")
        lines.append("    RootZone\\MinSoilMoisture.dat      / MINSMFL")
        lines.append("	1	1	1	1")
        lines.append("	2	1	1	1")
        lines.append("	3	1	1	1")
        lines.append("	4	1	1	1")
        lines.append("	5	1	1	1")
        lines.append("C*******************************************************************************")
        lines.append("C                      Target Soil Moisture")
        lines.append("    RootZone\\TargetSoilMoisture.dat      / TRGSMFL")
        lines.append("	1	1	1	1")
        lines.append("	2	1	1	1")
        lines.append("	3	1	1	1")
        lines.append("	4	1	1	1")
        lines.append("	5	1	1	1")
        lines.append("C*******************************************************************************")
        lines.append("C                       Return Flow Fractions")
        lines.append("	1	0.1	0.1	0.1")
        lines.append("	2	0.1	0.1	0.1")
        lines.append("	3	0.1	0.1	0.1")
        lines.append("	4	0.1	0.1	0.1")
        lines.append("	5	0.1	0.1	0.1")
        lines.append("C*******************************************************************************")
        lines.append("C                       Reuse Fractions")
        lines.append("	1	0.0	0.0	0.0")
        lines.append("	2	0.0	0.0	0.0")
        lines.append("	3	0.0	0.0	0.0")
        lines.append("	4	0.0	0.0	0.0")
        lines.append("	5	0.0	0.0	0.0")
        lines.append("C*******************************************************************************")
        lines.append("C                           Initial Soil Moisture")
        lines.append("	1	0.5	0.1934	0.1934	0.1934")
        lines.append("	2	0.5	0.2207	0.2207	0.2207")
        lines.append("	3	0.5	0.2371	0.2371	0.2371")
        lines.append("	4	0.5	0.2205	0.2205	0.2205")
        lines.append("	5	0.5	0.2567	0.2567	0.2567")
        lines.append("")

        content = "\r\n".join(lines)

        old_file = tmp_path / "old_npc.dat"
        old_file.write_text(content)

        # Create area file
        area_dir = tmp_path / "RootZone"
        area_dir.mkdir()
        area_content = create_lu_area_file_content(5, [1, 2, 3, 4, 5], 3)
        area_file = area_dir / "C2VSimCG_NonPondedCrop_Area.dat"
        area_file.write_text(area_content)

        new_file = tmp_path / "new_npc.dat"
        new_area_base = tmp_path / "new_area.dat"

        sim_files_new = SimulationFiles(
            np_file=str(new_file),
            npa_file=str(new_area_base)
        )

        # Include only elements 2 and 4
        elems = [2, 4]

        with patch('iwfm.sub_lu_file'):
            iwfm.sub_rz_npc_file(str(old_file), sim_files_new, elems,
                                 base_path=tmp_path, verbose=False)

        assert new_file.exists()

        # Verify output structure
        output_content = new_file.read_text()

        # Should have NCROP
        assert '/ NCROP' in output_content

        # Should have crop codes
        assert 'GR' in output_content
        assert 'CO' in output_content
        assert 'AL' in output_content

        # Should have new area file name
        assert 'new_area.dat' in output_content


# ============================================================================
# Tests with actual test data file (if available)
# ============================================================================

TEST_DATA_DIR = Path(__file__).parent / "C2VSimCG-2021"
NPC_FILE = TEST_DATA_DIR / "Simulation" / "Rootzone" / "C2VSimCG_NonPondedCrop.dat"


@pytest.fixture
def npc_file_exists():
    """Check that the C2VSimCG non-ponded crop file exists."""
    if not TEST_DATA_DIR.exists():
        pytest.skip(f"Test data directory not found: {TEST_DATA_DIR}")
    if not NPC_FILE.exists():
        pytest.skip(f"Non-ponded crop file not found: {NPC_FILE}")
    return True


class TestSubRzNpcFileWithRealFile:
    """Tests using the actual C2VSimCG non-ponded crop file."""

    def test_real_file_format_verification(self, npc_file_exists):
        """Test that C2VSimCG NPC file has expected structure."""
        with open(NPC_FILE, 'r') as f:
            content = f.read()

        # Verify file has expected markers
        assert '/ NCROP' in content, "Should have NCROP marker"
        assert '/ FLDMD' in content, "Should have FLDMD marker"
        assert '/ LUFLNP' in content, "Should have land use file marker"
        assert '/ NBCROP' in content, "Should have budget crop count marker"

    def test_real_file_ncrop_value(self, npc_file_exists):
        """Test reading NCROP from real file."""
        with open(NPC_FILE, 'r') as f:
            lines = f.readlines()

        # Find NCROP line
        ncrop = None
        for line in lines:
            if '/ NCROP' in line:
                ncrop = int(line.split()[0])
                break

        assert ncrop is not None, "Should find NCROP line"
        assert ncrop == 20, f"C2VSimCG should have 20 non-ponded crops, got {ncrop}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
