# test_hdf5_get_budget_data.py
# Tests for hdf5/get_budget_data_pywfm.py - Get IWFM Budget data from HDF file using pywfm
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


class TestGetBudgetDataImports:
    """Tests for get_budget_data imports."""

    def test_import_from_hdf5(self):
        """Test import from iwfm.hdf5."""
        from iwfm.hdf5 import get_budget_data
        assert callable(get_budget_data)

    @pytest.mark.skipif(not HAS_PYWFM, reason="pywfm not installed")
    def test_import_pywfm_directly(self):
        """Test direct module import of pywfm version."""
        from iwfm.hdf5.get_budget_data_pywfm import get_budget_data
        assert callable(get_budget_data)

    def test_function_has_docstring(self):
        """Test that function has documentation."""
        from iwfm.hdf5 import get_budget_data

        assert get_budget_data.__doc__ is not None
        assert 'budget' in get_budget_data.__doc__.lower()


class TestGetBudgetDataSignature:
    """Tests for get_budget_data function signature."""

    def test_function_signature(self):
        """Test that get_budget_data has correct function signature."""
        from iwfm.hdf5 import get_budget_data
        import inspect

        sig = inspect.signature(get_budget_data)
        params = list(sig.parameters.keys())

        assert 'bud_file' in params
        assert 'area_conversion_factor' in params
        assert 'volume_conversion_factor' in params
        assert 'verbose' in params

    def test_default_conversion_factors(self):
        """Test that default conversion factors are correct."""
        from iwfm.hdf5 import get_budget_data
        import inspect

        sig = inspect.signature(get_budget_data)

        # 0.0000229568411 converts sq ft to acres
        assert sig.parameters['area_conversion_factor'].default == 0.0000229568411
        assert sig.parameters['volume_conversion_factor'].default == 0.0000229568411

    def test_default_units(self):
        """Test that default units are correct."""
        from iwfm.hdf5 import get_budget_data
        import inspect

        sig = inspect.signature(get_budget_data)

        assert sig.parameters['area_units'].default == "ACRES"
        assert sig.parameters['volume_units'].default == "ACRE-FEET"
        assert sig.parameters['verbose'].default == False


@pytest.mark.skipif(not HAS_PYWFM, reason="pywfm not installed")
class TestGetBudgetDataWithPywfm:
    """Tests for get_budget_data with pywfm available."""

    def test_file_not_found(self):
        """Test that function raises for missing file."""
        from iwfm.hdf5.get_budget_data_pywfm import get_budget_data

        with pytest.raises((SystemExit, FileNotFoundError)):
            get_budget_data('nonexistent_file.hdf')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
