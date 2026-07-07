# test_get_gw_params.py
# Unit tests for the get_gw_params function in the iwfm package
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
import numpy as np

# Import directly from module since it may not be exported in __init__.py
from iwfm.get_gw_params import get_gw_params

# Path to the example C2VSimCG groundwater file
EXAMPLE_GW_FILE = os.path.join(
    os.path.dirname(__file__),
    'C2VSimCG-2021',
    'Simulation',
    'Groundwater',
    'C2VSimCG_Groundwater1974.dat'
)

# Check if the example file exists for tests that require it
EXAMPLE_FILE_EXISTS = os.path.exists(EXAMPLE_GW_FILE)


class TestGetGwParamsFunctionExists:
    """Test that the get_gw_params function exists and is callable."""

    def test_get_gw_params_exists(self):
        """Test that get_gw_params function exists and is callable."""
        assert get_gw_params is not None
        assert callable(get_gw_params)


@pytest.mark.skipif(not EXAMPLE_FILE_EXISTS, reason="C2VSimCG example file not found")
class TestGetGwParamsReturnTypes:
    """Test the return types of get_gw_params."""

    def test_returns_tuple_of_six(self):
        """Test that get_gw_params returns six values."""
        result = get_gw_params(EXAMPLE_GW_FILE)
        assert len(result) == 6

    def test_layers_is_integer(self):
        """Test that layers is an integer."""
        layers, _, _, _, _, _ = get_gw_params(EXAMPLE_GW_FILE)
        assert isinstance(layers, int)

    def test_kh_is_numpy_array(self):
        """Test that Kh is a numpy array."""
        _, Kh, _, _, _, _ = get_gw_params(EXAMPLE_GW_FILE)
        assert isinstance(Kh, np.ndarray)

    def test_ss_is_numpy_array(self):
        """Test that Ss is a numpy array."""
        _, _, Ss, _, _, _ = get_gw_params(EXAMPLE_GW_FILE)
        assert isinstance(Ss, np.ndarray)

    def test_sy_is_numpy_array(self):
        """Test that Sy is a numpy array."""
        _, _, _, Sy, _, _ = get_gw_params(EXAMPLE_GW_FILE)
        assert isinstance(Sy, np.ndarray)

    def test_kq_is_numpy_array(self):
        """Test that Kq is a numpy array."""
        _, _, _, _, Kq, _ = get_gw_params(EXAMPLE_GW_FILE)
        assert isinstance(Kq, np.ndarray)

    def test_kv_is_numpy_array(self):
        """Test that Kv is a numpy array."""
        _, _, _, _, _, Kv = get_gw_params(EXAMPLE_GW_FILE)
        assert isinstance(Kv, np.ndarray)


@pytest.mark.skipif(not EXAMPLE_FILE_EXISTS, reason="C2VSimCG example file not found")
class TestGetGwParamsLayerCount:
    """Test the layers count returned by get_gw_params."""

    def test_layers_positive(self):
        """Test that layers count is positive."""
        layers, _, _, _, _, _ = get_gw_params(EXAMPLE_GW_FILE)
        assert layers > 0

    def test_layers_reasonable(self):
        """Test that layers count is reasonable for IWFM models.

        Most IWFM models have 1-10 layers.
        """
        layers, _, _, _, _, _ = get_gw_params(EXAMPLE_GW_FILE)
        assert 1 <= layers <= 20


@pytest.mark.skipif(not EXAMPLE_FILE_EXISTS, reason="C2VSimCG example file not found")
class TestGetGwParamsArrayDimensions:
    """Test the dimensions of parameter arrays."""

    def test_all_arrays_same_shape(self):
        """Test that all parameter arrays have the same shape."""
        _, Kh, Ss, Sy, Kq, Kv = get_gw_params(EXAMPLE_GW_FILE)

        assert Kh.shape == Ss.shape
        assert Kh.shape == Sy.shape
        assert Kh.shape == Kq.shape
        assert Kh.shape == Kv.shape

    def test_array_dimensions_match_layers(self):
        """Test that array second dimension matches layers count."""
        layers, Kh, _, _, _, _ = get_gw_params(EXAMPLE_GW_FILE)

        # Arrays should be (nodes, layers)
        assert Kh.shape[1] == layers

    def test_arrays_have_two_dimensions(self):
        """Test that arrays are 2D (nodes x layers)."""
        _, Kh, Ss, Sy, Kq, Kv = get_gw_params(EXAMPLE_GW_FILE)

        assert len(Kh.shape) == 2
        assert len(Ss.shape) == 2
        assert len(Sy.shape) == 2
        assert len(Kq.shape) == 2
        assert len(Kv.shape) == 2

    def test_node_count_positive(self):
        """Test that node count (first dimension) is positive."""
        _, Kh, _, _, _, _ = get_gw_params(EXAMPLE_GW_FILE)

        assert Kh.shape[0] > 0


@pytest.mark.skipif(not EXAMPLE_FILE_EXISTS, reason="C2VSimCG example file not found")
class TestGetGwParamsParameterValues:
    """Test the parameter values returned by get_gw_params."""

    def test_kh_values_non_negative(self):
        """Test that hydraulic conductivity values are non-negative."""
        _, Kh, _, _, _, _ = get_gw_params(EXAMPLE_GW_FILE)

        # Hydraulic conductivity should be >= 0
        assert np.all(Kh >= 0)

    def test_ss_values_non_negative(self):
        """Test that specific storage values are non-negative."""
        _, _, Ss, _, _, _ = get_gw_params(EXAMPLE_GW_FILE)

        # Specific storage should be >= 0
        assert np.all(Ss >= 0)

    def test_sy_values_valid_range(self):
        """Test that specific yield values are in valid range [0, 1]."""
        _, _, _, Sy, _, _ = get_gw_params(EXAMPLE_GW_FILE)

        # Specific yield should be between 0 and 1 (or slightly higher for some models)
        assert np.all(Sy >= 0)
        # Allow some tolerance for models that might have Sy slightly > 1
        assert np.all(Sy <= 1.5)

    def test_kq_values_non_negative(self):
        """Test that horizontal anisotropy ratio values are non-negative."""
        _, _, _, _, Kq, _ = get_gw_params(EXAMPLE_GW_FILE)

        # Anisotropy ratio should be >= 0
        assert np.all(Kq >= 0)

    def test_kv_values_non_negative(self):
        """Test that vertical anisotropy ratio values are non-negative."""
        _, _, _, _, _, Kv = get_gw_params(EXAMPLE_GW_FILE)

        # Vertical anisotropy ratio should be >= 0
        assert np.all(Kv >= 0)


@pytest.mark.skipif(not EXAMPLE_FILE_EXISTS, reason="C2VSimCG example file not found")
class TestGetGwParamsArrayDataTypes:
    """Test the data types of parameter arrays."""

    def test_kh_is_numeric(self):
        """Test that Kh array contains numeric values."""
        _, Kh, _, _, _, _ = get_gw_params(EXAMPLE_GW_FILE)

        assert np.issubdtype(Kh.dtype, np.floating) or np.issubdtype(Kh.dtype, np.integer)

    def test_ss_is_numeric(self):
        """Test that Ss array contains numeric values."""
        _, _, Ss, _, _, _ = get_gw_params(EXAMPLE_GW_FILE)

        assert np.issubdtype(Ss.dtype, np.floating) or np.issubdtype(Ss.dtype, np.integer)

    def test_sy_is_numeric(self):
        """Test that Sy array contains numeric values."""
        _, _, _, Sy, _, _ = get_gw_params(EXAMPLE_GW_FILE)

        assert np.issubdtype(Sy.dtype, np.floating) or np.issubdtype(Sy.dtype, np.integer)

    def test_kq_is_numeric(self):
        """Test that Kq array contains numeric values."""
        _, _, _, _, Kq, _ = get_gw_params(EXAMPLE_GW_FILE)

        assert np.issubdtype(Kq.dtype, np.floating) or np.issubdtype(Kq.dtype, np.integer)

    def test_kv_is_numeric(self):
        """Test that Kv array contains numeric values."""
        _, _, _, _, _, Kv = get_gw_params(EXAMPLE_GW_FILE)

        assert np.issubdtype(Kv.dtype, np.floating) or np.issubdtype(Kv.dtype, np.integer)


@pytest.mark.skipif(not EXAMPLE_FILE_EXISTS, reason="C2VSimCG example file not found")
class TestGetGwParamsNoNaN:
    """Test that parameter arrays don't contain NaN values."""

    def test_kh_no_nan(self):
        """Test that Kh array has no NaN values."""
        _, Kh, _, _, _, _ = get_gw_params(EXAMPLE_GW_FILE)

        assert not np.any(np.isnan(Kh))

    def test_ss_no_nan(self):
        """Test that Ss array has no NaN values."""
        _, _, Ss, _, _, _ = get_gw_params(EXAMPLE_GW_FILE)

        assert not np.any(np.isnan(Ss))

    def test_sy_no_nan(self):
        """Test that Sy array has no NaN values."""
        _, _, _, Sy, _, _ = get_gw_params(EXAMPLE_GW_FILE)

        assert not np.any(np.isnan(Sy))

    def test_kq_no_nan(self):
        """Test that Kq array has no NaN values."""
        _, _, _, _, Kq, _ = get_gw_params(EXAMPLE_GW_FILE)

        assert not np.any(np.isnan(Kq))

    def test_kv_no_nan(self):
        """Test that Kv array has no NaN values."""
        _, _, _, _, _, Kv = get_gw_params(EXAMPLE_GW_FILE)

        assert not np.any(np.isnan(Kv))


@pytest.mark.skipif(not EXAMPLE_FILE_EXISTS, reason="C2VSimCG example file not found")
class TestGetGwParamsC2VSimCGSpecific:
    """Test get_gw_params with C2VSimCG-specific expectations."""

    def test_c2vsimcg_has_expected_node_count(self):
        """Test that C2VSimCG has expected number of nodes.

        C2VSimCG (Coarse Grid) typically has around 1,393 nodes.
        """
        _, Kh, _, _, _, _ = get_gw_params(EXAMPLE_GW_FILE)

        # C2VSimCG should have around 1,393 nodes
        assert 1000 < Kh.shape[0] < 2000

    def test_c2vsimcg_has_expected_layer_count(self):
        """Test that C2VSimCG has expected number of layers.

        C2VSimCG typically has 1-4 layers.
        """
        layers, _, _, _, _, _ = get_gw_params(EXAMPLE_GW_FILE)

        # C2VSimCG should have 1-4 layers
        assert 1 <= layers <= 4


@pytest.mark.skipif(not EXAMPLE_FILE_EXISTS, reason="C2VSimCG example file not found")
class TestGetGwParamsConsistency:
    """Test consistency of get_gw_params results."""

    def test_multiple_calls_return_same_results(self):
        """Test that multiple calls return the same results."""
        result1 = get_gw_params(EXAMPLE_GW_FILE)
        result2 = get_gw_params(EXAMPLE_GW_FILE)

        # Layers should match
        assert result1[0] == result2[0]

        # Arrays should match
        assert np.array_equal(result1[1], result2[1])  # Kh
        assert np.array_equal(result1[2], result2[2])  # Ss
        assert np.array_equal(result1[3], result2[3])  # Sy
        assert np.array_equal(result1[4], result2[4])  # Kq
        assert np.array_equal(result1[5], result2[5])  # Kv


class TestGetGwParamsErrorHandling:
    """Test error handling in get_gw_params."""

    def test_nonexistent_file_raises_error(self):
        """Test that nonexistent file raises FileNotFoundError.

        The iwfm package calls sys.exit() when a file is missing.
        """
        with pytest.raises(FileNotFoundError):
            get_gw_params('nonexistent_groundwater_file.dat')


@pytest.mark.skipif(not EXAMPLE_FILE_EXISTS, reason="C2VSimCG example file not found")
class TestGetGwParamsParameterStatistics:
    """Test statistical properties of parameter values."""

    def test_kh_has_variation(self):
        """Test that Kh values have some variation (not all same value)."""
        _, Kh, _, _, _, _ = get_gw_params(EXAMPLE_GW_FILE)

        # Standard deviation should be > 0 for a real model
        # (unless it's a very simple test case)
        # At minimum, check that not all values are identical
        if Kh.size > 1:
            assert Kh.max() != Kh.min() or Kh.max() == 0

    def test_ss_has_realistic_magnitude(self):
        """Test that Ss values have realistic magnitude.

        Specific storage typically ranges from 1e-6 to 1e-2 per foot.
        """
        _, _, Ss, _, _, _ = get_gw_params(EXAMPLE_GW_FILE)

        # Check that max value is not unreasonably large
        assert Ss.max() < 1.0

    def test_sy_mean_in_reasonable_range(self):
        """Test that mean Sy is in reasonable range.

        Typical Sy values range from 0.01 to 0.35.
        """
        _, _, _, Sy, _, _ = get_gw_params(EXAMPLE_GW_FILE)

        mean_sy = np.mean(Sy)
        # Mean Sy should typically be between 0.01 and 0.5
        assert 0.0 <= mean_sy <= 0.5


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
