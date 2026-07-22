#!/usr/bin/env python
# test_iwfm_read_rz_file_names.py
# Unit tests for iwfm_read_rz_file_names.py
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

import tempfile
import os
import pytest


def create_rz_file(rzconv, rzitermx, factcn, gwuptk, agnpfl, pfl, urbfl, nvrvfl):
    """Create IWFM RootZone file for testing.

    Parameters
    ----------
    rzconv : float
        Convergence criteria for iterative soil moisture accounting
    rzitermx : int
        Maximum number of iterations
    factcn : float
        Conversion factor (inches to simulation unit)
    gwuptk : int
        Flag for groundwater uptake (0 or 1)
    agnpfl : str
        Non-ponded agricultural crop data file
    pfl : str
        Rice/refuge data file
    urbfl : str
        Urban lands data file
    nvrvfl : str
        Native/riparian vegetation lands data file

    Returns
    -------
    str
        File contents
    """
    content = "C IWFM Root Zone Data File\n"
    content += "C\n"
    content += f" {rzconv}                                     / RZCONV\n"
    content += f" {rzitermx}                                           / RZITERMX\n"
    content += f" {factcn}                                       / FACTCN\n"
    content += f" {gwuptk}                                              / GWUPTK\n"
    content += "C\n"
    content += f" {agnpfl}            / AGNPFL\n"
    content += "C\n"
    content += f" {pfl}               / PFL\n"
    content += "C\n"
    content += f" {urbfl}                    / URBFL\n"
    content += "C\n"
    content += f" {nvrvfl}                / NVRVFL\n"
    content += "C\n"

    return content


class TestIwfmReadRzFileNames:
    """Tests for iwfm_read_rz_file_names function"""

    def test_basic_file_with_all_components(self):
        """Test reading basic rootzone file with all four component files"""
        content = create_rz_file(
            0.00000001,
            2000,
            0.083333,
            0,
            "NonPondedCrop.dat",
            "PondedCrop.dat",
            "Urban.dat",
            "NativeVeg.dat"
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_rz_file_names import iwfm_read_rz_file_names

            npc, pc, ur, nv = iwfm_read_rz_file_names(temp_file, verbose=False)

            # Verify file names are read correctly
            assert os.path.basename(npc) == "NonPondedCrop.dat"
            assert os.path.basename(pc) == "PondedCrop.dat"
            assert os.path.basename(ur) == "Urban.dat"
            assert os.path.basename(nv) == "NativeVeg.dat"

        finally:
            os.unlink(temp_file)

    def test_file_with_rootzone_prefix(self):
        """Test handling of 'RootZone/' prefix in file names"""
        content = create_rz_file(
            0.00000001,
            2000,
            0.083333,
            0,
            "RootZone/NonPondedCrop.dat",
            "RootZone/PondedCrop.dat",
            "RootZone/Urban.dat",
            "RootZone/NativeVeg.dat"
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_rz_file_names import iwfm_read_rz_file_names

            npc, pc, ur, nv = iwfm_read_rz_file_names(temp_file, verbose=False)

            # Verify RootZone/ prefix is removed
            assert os.path.basename(npc) == "NonPondedCrop.dat"
            assert os.path.basename(pc) == "PondedCrop.dat"
            assert os.path.basename(ur) == "Urban.dat"
            assert os.path.basename(nv) == "NativeVeg.dat"

        finally:
            os.unlink(temp_file)

    def test_windows_backslash_paths(self):
        """Test handling of Windows backslash paths"""
        content = create_rz_file(
            0.00000001,
            2000,
            0.083333,
            0,
            "RootZone\\NonPondedCrop.dat",
            "RootZone\\PondedCrop.dat",
            "RootZone\\Urban.dat",
            "RootZone\\NativeVeg.dat"
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_rz_file_names import iwfm_read_rz_file_names

            npc, pc, ur, nv = iwfm_read_rz_file_names(temp_file, verbose=False)

            # Verify backslashes are converted and RootZone/ prefix removed
            assert os.path.basename(npc) == "NonPondedCrop.dat"
            assert os.path.basename(pc) == "PondedCrop.dat"
            assert os.path.basename(ur) == "Urban.dat"
            assert os.path.basename(nv) == "NativeVeg.dat"

        finally:
            os.unlink(temp_file)

    def test_paths_resolved_to_rz_directory(self):
        """Test that file paths are resolved relative to rootzone file directory"""
        content = create_rz_file(
            0.00000001,
            2000,
            0.083333,
            0,
            "NonPondedCrop.dat",
            "PondedCrop.dat",
            "Urban.dat",
            "NativeVeg.dat"
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_rz_file_names import iwfm_read_rz_file_names

            npc, pc, ur, nv = iwfm_read_rz_file_names(temp_file, verbose=False)

            temp_dir = os.path.dirname(temp_file)

            # Verify paths are in the same directory as the rootzone file
            assert os.path.dirname(npc) == temp_dir
            assert os.path.dirname(pc) == temp_dir
            assert os.path.dirname(ur) == temp_dir
            assert os.path.dirname(nv) == temp_dir

        finally:
            os.unlink(temp_file)

    def test_different_parameter_values(self):
        """Test with different parameter values"""
        content = create_rz_file(
            0.0001,
            5000,
            1.0,
            1,
            "AgCrop.dat",
            "Rice.dat",
            "City.dat",
            "Native.dat"
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_rz_file_names import iwfm_read_rz_file_names

            npc, pc, ur, nv = iwfm_read_rz_file_names(temp_file, verbose=False)

            # Verify file names
            assert os.path.basename(npc) == "AgCrop.dat"
            assert os.path.basename(pc) == "Rice.dat"
            assert os.path.basename(ur) == "City.dat"
            assert os.path.basename(nv) == "Native.dat"

        finally:
            os.unlink(temp_file)

    def test_comment_lines_skipped(self):
        """Test that comment lines are properly skipped"""
        content = "C IWFM Root Zone Data File\n"
        content += "c This is a comment\n"
        content += "* Another comment\n"
        content += "# Hash comment\n"
        content += " 0.00000001                                     / RZCONV\n"
        content += "C More comments\n"
        content += " 2000                                           / RZITERMX\n"
        content += "c Another comment\n"
        content += " 0.083333                                       / FACTCN\n"
        content += "* Comment\n"
        content += " 0                                              / GWUPTK\n"
        content += "# Comment\n"
        content += " NonPondedCrop.dat            / AGNPFL\n"
        content += "C\n"
        content += " PondedCrop.dat               / PFL\n"
        content += "C\n"
        content += " Urban.dat                    / URBFL\n"
        content += "C\n"
        content += " NativeVeg.dat                / NVRVFL\n"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_rz_file_names import iwfm_read_rz_file_names

            npc, pc, ur, nv = iwfm_read_rz_file_names(temp_file, verbose=False)

            # Should read correctly despite comment lines
            assert os.path.basename(npc) == "NonPondedCrop.dat"
            assert os.path.basename(pc) == "PondedCrop.dat"
            assert os.path.basename(ur) == "Urban.dat"
            assert os.path.basename(nv) == "NativeVeg.dat"

        finally:
            os.unlink(temp_file)

    def test_real_file_format(self):
        """Test with format matching real IWFM C2VSimCG file"""
        content = "C*****************************************************************************\n"
        content += "C                  INTEGRATED WATER FLOW MODEL (IWFM)\n"
        content += "C*****************************************************************************\n"
        content += "C\n"
        content += " 0.00000001                                     / RZCONV\n"
        content += " 2000                                           / RZITERMX\n"
        content += " 0.083333                                       / FACTCN\n"
        content += " 0                                              / GWUPTK\n"
        content += " RootZone\\C2VSimCG_NonPondedCrop.dat            / AGNPFL\n"
        content += " RootZone\\C2VSimCG_PondedCrop.dat               / PFL\n"
        content += " RootZone\\C2VSimCG_Urban.dat                    / URBFL\n"
        content += " RootZone\\C2VSimCG_NativeVeg.dat                / NVRVFL\n"
        content += "C\n"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_rz_file_names import iwfm_read_rz_file_names

            npc, pc, ur, nv = iwfm_read_rz_file_names(temp_file, verbose=False)

            # Verify file names
            assert os.path.basename(npc) == "C2VSimCG_NonPondedCrop.dat"
            assert os.path.basename(pc) == "C2VSimCG_PondedCrop.dat"
            assert os.path.basename(ur) == "C2VSimCG_Urban.dat"
            assert os.path.basename(nv) == "C2VSimCG_NativeVeg.dat"

        finally:
            os.unlink(temp_file)

    def test_long_filenames(self):
        """Test handling of long file names"""
        long_npc = "Very_Long_NonPonded_Crop_File_Name_With_Many_Characters.dat"
        long_pc = "Very_Long_Ponded_Crop_File_Name_With_Many_Characters.dat"

        content = create_rz_file(
            0.00000001,
            2000,
            0.083333,
            0,
            long_npc,
            long_pc,
            "Urban.dat",
            "NativeVeg.dat"
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_rz_file_names import iwfm_read_rz_file_names

            npc, pc, ur, nv = iwfm_read_rz_file_names(temp_file, verbose=False)

            # Verify long file names are read correctly
            assert os.path.basename(npc) == long_npc
            assert os.path.basename(pc) == long_pc

        finally:
            os.unlink(temp_file)

    def test_return_tuple_structure(self):
        """Test that function returns tuple of 4 strings"""
        content = create_rz_file(
            0.00000001,
            2000,
            0.083333,
            0,
            "NonPondedCrop.dat",
            "PondedCrop.dat",
            "Urban.dat",
            "NativeVeg.dat"
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_rz_file_names import iwfm_read_rz_file_names

            result = iwfm_read_rz_file_names(temp_file, verbose=False)

            # Verify return type
            assert isinstance(result, tuple)
            assert len(result) == 4

            # Verify all elements are strings
            for item in result:
                assert isinstance(item, str)

        finally:
            os.unlink(temp_file)

    def test_verbose_mode(self):
        """Test verbose mode doesn't affect functionality"""
        content = create_rz_file(
            0.00000001,
            2000,
            0.083333,
            0,
            "NonPondedCrop.dat",
            "PondedCrop.dat",
            "Urban.dat",
            "NativeVeg.dat"
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_rz_file_names import iwfm_read_rz_file_names

            # Test with verbose=True
            npc, pc, ur, nv = iwfm_read_rz_file_names(temp_file, verbose=True)

            # Verify file names are still read correctly
            assert os.path.basename(npc) == "NonPondedCrop.dat"
            assert os.path.basename(pc) == "PondedCrop.dat"
            assert os.path.basename(ur) == "Urban.dat"
            assert os.path.basename(nv) == "NativeVeg.dat"

        finally:
            os.unlink(temp_file)

    def test_mixed_path_formats(self):
        """Test handling of mixed path formats"""
        content = create_rz_file(
            0.00000001,
            2000,
            0.083333,
            0,
            "RootZone/NonPondedCrop.dat",
            "RootZone\\PondedCrop.dat",
            "Urban.dat",
            "Data/NativeVeg.dat"
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_read_rz_file_names import iwfm_read_rz_file_names

            npc, pc, ur, nv = iwfm_read_rz_file_names(temp_file, verbose=False)

            # Verify file names (RootZone/ prefix removed, backslashes converted)
            assert os.path.basename(npc) == "NonPondedCrop.dat"
            assert os.path.basename(pc) == "PondedCrop.dat"
            assert os.path.basename(ur) == "Urban.dat"
            # Data/ prefix is NOT removed (only RootZone/ is special)
            assert "NativeVeg.dat" in nv

        finally:
            os.unlink(temp_file)


class TestRootzoneVersionGuard:
    """v5.0 rootzone files (restructured file list) are refused; 4.x and
    untagged files proceed."""

    def test_v5_raises(self, tmp_path):
        from iwfm.iwfm_read_rz_file_names import iwfm_read_rz_file_names
        content = '#5.0\n' + create_rz_file(
            0.01, 30, 1.0, 1, 'npc.dat', 'pc.dat', 'urban.dat', 'nv.dat')
        rz_file = tmp_path / 'RootZone.dat'
        rz_file.write_text(content)
        with pytest.raises(NotImplementedError, match="version '5.0'"):
            iwfm_read_rz_file_names(str(rz_file))

    def test_v4_tag_accepted(self, tmp_path):
        from iwfm.iwfm_read_rz_file_names import iwfm_read_rz_file_names
        content = '#4.13\n' + create_rz_file(
            0.01, 30, 1.0, 1, 'npc.dat', 'pc.dat', 'urban.dat', 'nv.dat')
        rz_file = tmp_path / 'RootZone.dat'
        rz_file.write_text(content)
        npc, pc, ur, nv = iwfm_read_rz_file_names(str(rz_file))
        assert npc.endswith('npc.dat')

    def test_iwfm_read_rz_v5_raises(self, tmp_path):
        from iwfm.iwfm_read_rz import iwfm_read_rz
        content = '#5.0\n' + create_rz_file(
            0.01, 30, 1.0, 1, 'npc.dat', 'pc.dat', 'urban.dat', 'nv.dat')
        rz_file = tmp_path / 'RootZone.dat'
        rz_file.write_text(content)
        with pytest.raises(NotImplementedError, match="version '5.0'"):
            iwfm_read_rz(str(rz_file))
