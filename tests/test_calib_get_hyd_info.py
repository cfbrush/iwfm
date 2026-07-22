# test_calib_get_hyd_info.py
# Unit tests for calib/get_hyd_info.py - Unpack control variables for hydrograph type
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


class TestGetHydInfo:
    """Tests for get_hyd_info function"""

    def create_mock_main_file(self, tmp_path, nout=3, hyd_names=None, hyd_file_name='test_hyd.out'):
        """Create a mock IWFM main file for testing.
        
        The file format has:
        - Skip lines at the beginning
        - Line with NOUT (number of hydrographs)
        - Skip lines
        - Hydrograph output file name
        - Lines with hydrograph definitions
        """
        if hyd_names is None:
            hyd_names = [f'HYD_{i:03d}' for i in range(1, nout + 1)]
        
        main_file = tmp_path / 'main_input.dat'
        hyd_file = tmp_path / hyd_file_name
        
        # Create hydrograph output file (must exist)
        hyd_file.write_text('# Hydrograph output file\n')
        
        lines = []
        # First 5 lines are skipped
        for i in range(6):
            lines.append(f'# Comment line {i}')
        
        # After skips[0] lines: NOUT
        lines.append(f'{nout}  # Number of hydrographs')
        
        # After skips[1] lines: hydrograph file name
        lines.append(f'{hyd_file}  # Hydrograph output file')
        
        # Hydrograph definitions - one per line
        # Format depends on colid, but typically: ID  Node  Layer  Name  ...
        for i, name in enumerate(hyd_names):
            lines.append(f'{i+1}  100  1  {name}  0.0  0.0')
        
        main_file.write_text('\n'.join(lines))
        return str(main_file), str(hyd_file)

    def test_returns_tuple(self, tmp_path):
        """Test that function returns a tuple of (hyd_file, hyd_names)."""
        from iwfm.calib.get_hyd_info import get_hyd_info

        main_file, hyd_file = self.create_mock_main_file(tmp_path, nout=2)
        
        # Create file_dict with correct structure
        # Index 0: main file, Index 8: colid, Index 9: skips
        file_dict = {
            'Groundwater': [main_file, None, None, None, None, None, None, None, 3, [0, 1]]
        }
        
        result = get_hyd_info('Groundwater', file_dict)
        
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_function_signature(self):
        """Test function has correct parameters."""
        from iwfm.calib.get_hyd_info import get_hyd_info
        import inspect
        
        sig = inspect.signature(get_hyd_info)
        params = list(sig.parameters.keys())
        
        assert 'ftype' in params
        assert 'file_dict' in params

    def test_function_has_docstring(self):
        """Test that function has documentation."""
        from iwfm.calib.get_hyd_info import get_hyd_info
        
        assert get_hyd_info.__doc__ is not None
        assert 'hyd_file' in get_hyd_info.__doc__
        assert 'hyd_names' in get_hyd_info.__doc__


class TestGetHydInfoFileDict:
    """Tests for file_dict structure handling."""

    def test_extracts_main_file_from_dict(self):
        """Test that main_file is extracted from file_dict[ftype][0]."""
        from iwfm.calib import get_hyd_info as module
        import inspect
        
        source = inspect.getsource(module)
        assert 'file_dict[ftype][0]' in source

    def test_extracts_colid_from_dict(self):
        """Test that colid is extracted from file_dict[ftype][8]."""
        from iwfm.calib import get_hyd_info as module
        import inspect
        
        source = inspect.getsource(module)
        assert 'file_dict[ftype][8]' in source

    def test_extracts_skips_from_dict(self):
        """Test that skips is extracted from file_dict[ftype][9]."""
        from iwfm.calib import get_hyd_info as module
        import inspect
        
        source = inspect.getsource(module)
        assert 'file_dict[ftype][9]' in source


class TestGetHydInfoTileDrains:
    """Tests for special Tile drains handling."""

    def test_tile_drains_special_handling(self):
        """Test that 'Tile drains' ftype has special handling."""
        from iwfm.calib import get_hyd_info as module
        import inspect
        
        source = inspect.getsource(module)
        assert "ftype == 'Tile drains'" in source

    def test_tile_drains_skips_extra_sections(self):
        """Test that Tile drains skips tile drain params and subsurface irrigation."""
        from iwfm.calib import get_hyd_info as module
        import inspect
        
        source = inspect.getsource(module)
        # Should have special logic for tile drain sections
        assert 'td_no' in source or 'tile drain' in source.lower()
        assert 'sd_no' in source or 'subsurface' in source.lower()


class TestGetHydInfoImports:
    """Tests for function imports."""

    def test_import_from_calib(self):
        """Test import from iwfm.calib."""
        from iwfm.calib import get_hyd_info
        assert callable(get_hyd_info)

    def test_import_directly(self):
        """Test direct module import."""
        from iwfm.calib.get_hyd_info import get_hyd_info
        assert callable(get_hyd_info)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])


class TestGetHydInfoSubsidenceVersionGuard:
    """v5.0 subsidence files are refused; untagged/v4 files proceed."""

    def test_v5_subsidence_raises(self, tmp_path):
        from iwfm.calib.get_hyd_info import get_hyd_info
        main_file = tmp_path / 'Subsidence.dat'
        main_file.write_text('#5.0\nC comment\n  1  / NOUTS\n')
        file_dict = {'Subsidence': [str(main_file), '', '', '', '', True,
                                    True, 0, 5, [5, 2]]}
        with pytest.raises(NotImplementedError, match="version '5.0'"):
            get_hyd_info('Subsidence', file_dict)
