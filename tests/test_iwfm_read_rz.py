#!/usr/bin/env python
# test_iwfm_read_rz.py
# Unit tests for iwfm_read_rz.py
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
import iwfm


class TestIwfmReadRz:
    """Tests for iwfm_read_rz function"""

    def test_basic_rootzone_file(self):
        """Test reading a basic rootzone file with all 7 file references"""
        # Create test file content following IWFM format convention
        # Note: Data lines MUST start with whitespace to avoid being treated as comments
        # The first 4 data lines after comments are parameters, then come the file names
        content = """C Root zone main file
C IWFM Version 2015
C Comment line 3
C Comment line 4
 PARAM1  ! First parameter
 PARAM2  ! Second parameter
 PARAM3  ! Third parameter
 1  ! GWUPTK flag
 npc_crops.dat       ! Non-ponded crops file
 ponded_crops.dat    ! Ponded crops file
 urban_data.dat      ! Urban file
 native_veg.dat      ! Native and riparian vegetation file
 return_flow.dat     ! Return flow file
 reuse_data.dat      ! Reuse file
 irrigation.dat      ! Irrigation period file
"""

        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            # Read the file
            result = iwfm.iwfm_read_rz(temp_file)

            # Verify all expected keys are present
            expected_keys = ['np_file', 'p_file', 'ur_file', 'nr_file',
                           'rf_file', 'ru_file', 'ir_file']
            assert set(result.keys()) == set(expected_keys), \
                f"Expected keys {expected_keys}, got {list(result.keys())}"

            # Verify correct file names
            assert result['np_file'] == 'npc_crops.dat'
            assert result['p_file'] == 'ponded_crops.dat'
            assert result['ur_file'] == 'urban_data.dat'
            assert result['nr_file'] == 'native_veg.dat'
            assert result['rf_file'] == 'return_flow.dat'
            assert result['ru_file'] == 'reuse_data.dat'
            assert result['ir_file'] == 'irrigation.dat'

        finally:
            # Clean up temporary file
            os.unlink(temp_file)

    def test_rootzone_file_with_inline_comments(self):
        """Test that inline comments are properly ignored"""
        content = """C Root zone main file
C IWFM Version 2015
C Comment line 3
C Comment line 4
 PARAM1
 PARAM2
 PARAM3
 1
 file1.dat    ! This is an inline comment with extra text
 file2.dat    ! Another comment
 file3.dat    ! Comment
 file4.dat    ! Comment
 file5.dat    ! Comment
 file6.dat    ! Comment
 file7.dat    ! Comment
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            result = iwfm.iwfm_read_rz(temp_file)

            # Verify only the filename is captured, not the comment
            assert result['np_file'] == 'file1.dat'
            assert result['p_file'] == 'file2.dat'
            assert result['ur_file'] == 'file3.dat'

        finally:
            os.unlink(temp_file)

    def test_rootzone_file_with_extra_comments(self):
        """Test reading file with extra comment lines between data"""
        content = """C Root zone main file
C IWFM Version 2015
C Comment line 3
C Comment line 4
 PARAM1
 PARAM2
 PARAM3
 1
 file1.dat
C Extra comment line here
 file2.dat
 file3.dat
C Another comment
 file4.dat
 file5.dat
 file6.dat
 file7.dat
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            result = iwfm.iwfm_read_rz(temp_file)

            # skip_ahead should handle the extra comment lines
            assert result['np_file'] == 'file1.dat'
            assert result['p_file'] == 'file2.dat'
            assert result['ur_file'] == 'file3.dat'
            assert result['nr_file'] == 'file4.dat'

        finally:
            os.unlink(temp_file)

    def test_rootzone_file_with_paths(self):
        """Test reading file with relative/absolute paths"""
        content = """C Root zone main file
C IWFM Version 2015
C Comment line 3
C Comment line 4
 PARAM1
 PARAM2
 PARAM3
 1
 ./data/npc_crops.dat
 ../input/ponded_crops.dat
 /absolute/path/urban.dat
 relative/native.dat
 return.dat
 reuse.dat
 irrigation.dat
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            result = iwfm.iwfm_read_rz(temp_file)

            # Verify paths are captured correctly
            assert result['np_file'] == './data/npc_crops.dat'
            assert result['p_file'] == '../input/ponded_crops.dat'
            assert result['ur_file'] == '/absolute/path/urban.dat'
            assert result['nr_file'] == 'relative/native.dat'

        finally:
            os.unlink(temp_file)

    def test_rootzone_file_with_whitespace_variations(self):
        """Test handling of various whitespace patterns"""
        content = """C Root zone main file
C IWFM Version 2015
C Comment line 3
C Comment line 4
 PARAM1
 PARAM2
 PARAM3
 1
 file1.dat
  file2.dat
\tfile3.dat
 \tfile4.dat
   file5.dat
\t\tfile6.dat
      file7.dat
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            result = iwfm.iwfm_read_rz(temp_file)

            # All should be read correctly regardless of leading whitespace type
            assert result['np_file'] == 'file1.dat'
            assert result['p_file'] == 'file2.dat'
            assert result['ur_file'] == 'file3.dat'
            assert result['nr_file'] == 'file4.dat'
            assert result['rf_file'] == 'file5.dat'
            assert result['ru_file'] == 'file6.dat'
            assert result['ir_file'] == 'file7.dat'

        finally:
            os.unlink(temp_file)

    def test_return_type(self):
        """Test that function returns a RootzoneFiles dataclass"""
        content = """C Root zone main file
C IWFM Version 2015
C Comment line 3
C Comment line 4
 PARAM1
 PARAM2
 PARAM3
 1
 file1.dat
 file2.dat
 file3.dat
 file4.dat
 file5.dat
 file6.dat
 file7.dat
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            from iwfm.iwfm_dataclasses import RootzoneFiles

            result = iwfm.iwfm_read_rz(temp_file)

            assert isinstance(result, RootzoneFiles), \
                f"Expected RootzoneFiles, got {type(result)}"
            assert len(result) == 7, \
                f"Expected 7 entries, got {len(result)}"

        finally:
            os.unlink(temp_file)

    def test_file_not_found(self):
        """Test error handling for non-existent file"""
        with pytest.raises(FileNotFoundError):
            iwfm.iwfm_read_rz('/nonexistent/path/to/file.dat')

    def test_real_world_example(self):
        """Test with realistic IWFM rootzone file content from C2VSimCG"""
        # Based on actual C2VSimCG_RootZone.dat file structure
        # Using raw string to handle Windows-style backslash paths
        content = r"""C Root zone main file
C IWFM Rootzone Package v4.11
C Developed by the Bay-Delta Office, California Department of Water Resources
C
      0.00000001                                     / RZCONV
      2000                                           / RZITERMX
      0.083333                                       / FACTCN
      0                                              / GWUPTK
      RootZone\C2VSimCG_NonPondedCrop.dat            / AGNPFL
      RootZone\C2VSimCG_PondedCrop.dat               / PFL
      RootZone\C2VSimCG_Urban.dat                    / URBFL
      RootZone\C2VSimCG_NativeVeg.dat                / NVRVFL
      RootZone\C2VSimCG_ReturnFlowFrac.dat           / RFFL
      RootZone\C2VSimCG_ReuseFrac.dat                / RUFL
      RootZone\C2VSimCG_IrrPeriod.dat                / IPFL
C
C Additional configuration below...
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            result = iwfm.iwfm_read_rz(temp_file)

            # Verify realistic file names are captured (with paths)
            assert result['np_file'] == r'RootZone\C2VSimCG_NonPondedCrop.dat'
            assert result['p_file'] == r'RootZone\C2VSimCG_PondedCrop.dat'
            assert result['ur_file'] == r'RootZone\C2VSimCG_Urban.dat'
            assert result['nr_file'] == r'RootZone\C2VSimCG_NativeVeg.dat'
            assert result['rf_file'] == r'RootZone\C2VSimCG_ReturnFlowFrac.dat'
            assert result['ru_file'] == r'RootZone\C2VSimCG_ReuseFrac.dat'
            assert result['ir_file'] == r'RootZone\C2VSimCG_IrrPeriod.dat'

        finally:
            os.unlink(temp_file)

    def test_with_actual_c2vsimcg_file(self):
        """Test with actual C2VSimCG rootzone file if it exists"""
        test_file = '/Volumes/MinEx/Documents/Dropbox/work/Programing/repos/iwfm-py/iwfm-tests/C2VSimCG-2021/Simulation/RootZone/C2VSimCG_RootZone.dat'

        if not os.path.exists(test_file):
            pytest.skip(f"Test file not found: {test_file}")

        result = iwfm.iwfm_read_rz(test_file)

        # Verify all expected keys are present
        expected_keys = ['np_file', 'p_file', 'ur_file', 'nr_file',
                       'rf_file', 'ru_file', 'ir_file']
        assert set(result.keys()) == set(expected_keys)

        # Verify the actual file paths from C2VSimCG
        assert result['np_file'] == r'RootZone\C2VSimCG_NonPondedCrop.dat'
        assert result['p_file'] == r'RootZone\C2VSimCG_PondedCrop.dat'
        assert result['ur_file'] == r'RootZone\C2VSimCG_Urban.dat'
        assert result['nr_file'] == r'RootZone\C2VSimCG_NativeVeg.dat'
        assert result['rf_file'] == r'RootZone\C2VSimCG_ReturnFlowFrac.dat'
        assert result['ru_file'] == r'RootZone\C2VSimCG_ReuseFrac.dat'
        assert result['ir_file'] == r'RootZone\C2VSimCG_IrrPeriod.dat'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
