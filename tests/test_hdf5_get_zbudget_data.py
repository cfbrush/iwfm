# test_hdf5_get_zbudget_data.py
# Tests for hdf5/get_zbudget_data.py - Get IWFM ZBudget data from HDF file
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

# Check if pywfm is available
try:
    import pywfm  # noqa: F401
    del pywfm
    HAS_PYWFM = True
except ImportError:
    HAS_PYWFM = False


class TestGetZbudgetDataImports:
    """Tests for get_zbudget_data imports."""

    def test_import_from_hdf5(self):
        """Test import from iwfm.hdf5."""
        from iwfm.hdf5 import get_zbudget_data
        assert callable(get_zbudget_data)

    @pytest.mark.skipif(not HAS_PYWFM, reason="pywfm not installed")
    def test_import_pywfm_directly(self):
        """Test direct module import of pywfm version."""
        from iwfm.hdf5.get_zbudget_data_pywfm import get_zbudget_data
        assert callable(get_zbudget_data)

    def test_function_has_docstring(self):
        """Test that function has documentation."""
        from iwfm.hdf5 import get_zbudget_data

        assert get_zbudget_data.__doc__ is not None
        assert 'budget' in get_zbudget_data.__doc__.lower()


class TestGetZbudgetDataSignature:
    """Tests for get_zbudget_data function signature."""

    def test_function_signature(self):
        """Test that get_zbudget_data has correct function signature."""
        from iwfm.hdf5 import get_zbudget_data
        import inspect

        sig = inspect.signature(get_zbudget_data)
        params = list(sig.parameters.keys())

        assert 'zbud_file' in params
        assert 'zone_file' in params
        assert 'area_units' in params
        assert 'area_conversion_factor' in params
        assert 'volume_units' in params
        assert 'volume_conversion_factor' in params
        assert 'logging' in params
        assert 'verbose' in params

    def test_default_conversion_factors(self):
        """Test that default conversion factors are correct."""
        from iwfm.hdf5 import get_zbudget_data
        import inspect

        sig = inspect.signature(get_zbudget_data)

        assert sig.parameters['area_conversion_factor'].default == 0.0000229568411
        assert sig.parameters['volume_conversion_factor'].default == 0.0000229568411

    def test_default_units(self):
        """Test that default units are correct."""
        from iwfm.hdf5 import get_zbudget_data
        import inspect

        sig = inspect.signature(get_zbudget_data)

        assert sig.parameters['area_units'].default == 'ACRES'
        assert sig.parameters['volume_units'].default == 'AC-FT'
        assert sig.parameters['logging'].default == False
        assert sig.parameters['verbose'].default == False


@pytest.mark.skipif(not HAS_PYWFM, reason="pywfm not installed")
class TestGetZbudgetDataWithPywfm:
    """Tests for get_zbudget_data with pywfm available."""

    def test_file_not_found(self):
        """Test that function raises for missing file."""
        from iwfm.hdf5.get_zbudget_data_pywfm import get_zbudget_data

        with pytest.raises((SystemExit, FileNotFoundError)):
            get_zbudget_data('nonexistent_zbud.hdf', 'nonexistent_zone.dat')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
