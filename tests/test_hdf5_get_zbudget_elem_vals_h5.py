# test_hdf5_get_zbudget_elem_vals_h5.py
# Tests for hdf5/get_zbudget_elem_vals_h5.py - h5py-based zone budget element values reader
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

try:
    import h5py  # noqa: F401
    del h5py
    HAS_H5PY = True
except ImportError:
    HAS_H5PY = False

TEST_DATA_DIR = os.path.dirname(__file__)
TEST_ZBUDGET_FILE = os.path.join(TEST_DATA_DIR, 'C2VSimCG-2021', 'Results', 'C2VSimCG_GW_ZBudget.hdf')
TEST_ZONE_FILE = os.path.join(TEST_DATA_DIR, 'C2VSimCG-2021', 'ZBudget', 'C2VSimCG_ZBudget_SRs.dat')


class TestGetZbudgetElemValsH5Imports:
    """Imports for get_zbudget_elem_vals_h5."""

    def test_import_from_hdf5(self):
        """get_zbudget_elem_vals importable from iwfm.hdf5."""
        from iwfm.hdf5 import get_zbudget_elem_vals
        assert callable(get_zbudget_elem_vals)

    @pytest.mark.skipif(not HAS_H5PY, reason="h5py not installed")
    def test_import_directly(self):
        """h5 module importable directly."""
        from iwfm.hdf5.get_zbudget_elem_vals_h5 import get_zbudget_elem_vals
        assert callable(get_zbudget_elem_vals)

    @pytest.mark.skipif(not HAS_H5PY, reason="h5py not installed")
    def test_function_has_docstring(self):
        """Function has docstring referencing zone or budget."""
        from iwfm.hdf5.get_zbudget_elem_vals_h5 import get_zbudget_elem_vals

        assert get_zbudget_elem_vals.__doc__ is not None
        doc = get_zbudget_elem_vals.__doc__.lower()
        assert 'zone' in doc or 'element' in doc


class TestGetZbudgetElemValsH5Signature:
    """Function signature checks."""

    @pytest.mark.skipif(not HAS_H5PY, reason="h5py not installed")
    def test_function_signature(self):
        """Required parameters present."""
        from iwfm.hdf5.get_zbudget_elem_vals_h5 import get_zbudget_elem_vals
        import inspect

        sig = inspect.signature(get_zbudget_elem_vals)
        params = list(sig.parameters.keys())

        assert 'zbud_file' in params
        assert 'zones_file' in params
        assert 'col_ids' in params
        assert 'area_conversion_factor' in params
        assert 'volume_conversion_factor' in params
        assert 'area_units' in params
        assert 'volume_units' in params
        assert 'verbose' in params

    @pytest.mark.skipif(not HAS_H5PY, reason="h5py not installed")
    def test_default_conversion_factors(self):
        """Defaults match plan-specified values."""
        from iwfm.hdf5.get_zbudget_elem_vals_h5 import get_zbudget_elem_vals
        import inspect

        sig = inspect.signature(get_zbudget_elem_vals)

        assert sig.parameters['area_conversion_factor'].default == 0.0000229568411
        assert sig.parameters['volume_conversion_factor'].default == 0.0000229568411
        assert sig.parameters['area_units'].default == 'ACRES'
        assert sig.parameters['volume_units'].default == 'ACRE-FEET'
        assert sig.parameters['verbose'].default is False


class TestGetZbudgetElemValsH5ErrorPaths:
    """Error path tests (no fixtures required)."""

    @pytest.mark.skipif(not HAS_H5PY, reason="h5py not installed")
    def test_missing_zbud_file_raises(self, tmp_path):
        """Nonexistent zbudget file raises (FileNotFoundError or OSError)."""
        from iwfm.hdf5.get_zbudget_elem_vals_h5 import get_zbudget_elem_vals

        bogus_zbud = str(tmp_path / 'does_not_exist.hdf')
        zones = tmp_path / 'zones.dat'
        zones.write_text('# placeholder\n')

        with pytest.raises((FileNotFoundError, OSError, SystemExit)):
            get_zbudget_elem_vals(bogus_zbud, str(zones), col_ids=[1])

    @pytest.mark.skipif(not HAS_H5PY, reason="h5py not installed")
    def test_missing_zones_file_raises(self, tmp_path):
        """Nonexistent zones file raises."""
        from iwfm.hdf5.get_zbudget_elem_vals_h5 import get_zbudget_elem_vals

        zbud = tmp_path / 'placeholder.hdf'
        zbud.write_bytes(b'')  # invalid HDF5 but exists
        bogus_zones = str(tmp_path / 'does_not_exist.dat')

        with pytest.raises((FileNotFoundError, OSError, SystemExit)):
            get_zbudget_elem_vals(str(zbud), bogus_zones, col_ids=[1])


@pytest.mark.skipif(not HAS_H5PY, reason="h5py not installed")
@pytest.mark.skipif(
    not (os.path.exists(TEST_ZBUDGET_FILE) and os.path.exists(TEST_ZONE_FILE)),
    reason="Test data not available"
)
class TestGetZbudgetElemValsH5WithRealData:
    """End-to-end tests against real C2VSimCG-2021 HDF5 fixture (skipped when absent)."""

    def test_returns_two_lists(self):
        """Returns (dates, zone_data) tuple of two lists."""
        from iwfm.hdf5.get_zbudget_elem_vals_h5 import get_zbudget_elem_vals

        dates, zone_data = get_zbudget_elem_vals(
            TEST_ZBUDGET_FILE, TEST_ZONE_FILE, col_ids=[1])

        assert isinstance(dates, list)
        assert isinstance(zone_data, list)

    def test_dates_nonempty(self):
        """Dates list is nonempty for a real fixture."""
        from iwfm.hdf5.get_zbudget_elem_vals_h5 import get_zbudget_elem_vals

        dates, _ = get_zbudget_elem_vals(
            TEST_ZBUDGET_FILE, TEST_ZONE_FILE, col_ids=[1])
        assert len(dates) > 0

    def test_zone_data_first_field_is_zone_id(self):
        """Each zone_data row starts with zone id (1-indexed int)."""
        from iwfm.hdf5.get_zbudget_elem_vals_h5 import get_zbudget_elem_vals

        _, zone_data = get_zbudget_elem_vals(
            TEST_ZBUDGET_FILE, TEST_ZONE_FILE, col_ids=[1])
        if zone_data:
            assert isinstance(zone_data[0][0], int)
            assert zone_data[0][0] >= 1

    def test_col_ids_count_matches_data_width(self):
        """Each zone row has 1 + len(col_ids) entries (zone_id + one sum per col)."""
        from iwfm.hdf5.get_zbudget_elem_vals_h5 import get_zbudget_elem_vals

        col_ids = [1, 2]
        _, zone_data = get_zbudget_elem_vals(
            TEST_ZBUDGET_FILE, TEST_ZONE_FILE, col_ids=col_ids)
        if zone_data:
            assert len(zone_data[0]) == 1 + len(col_ids)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
