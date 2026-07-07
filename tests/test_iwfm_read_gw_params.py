# test_iwfm_read_gw_params.py
# Tests for iwfm_read_gw_params function
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

"""
Tests for iwfm.iwfm_read_gw_params function.

The iwfm_read_gw_params function reads an IWFM Simulation Groundwater file
and returns a list of groundwater parameters.

Example files used for testing:
- Groundwater file: iwfm/tests/C2VSimCG-2021/Simulation/Groundwater/C2VSimCG_Groundwater1974.dat

C2VSimCG model characteristics:
- 1,393 nodes
- 4 layers

Returns a list of 6 parameters:
- Kh: Hydraulic conductivity (horizontal)
- Ss: Specific storage
- Sy: Specific yield
- Kq: Horizontal anisotropy ratio
- Kv: Vertical hydraulic conductivity (or anisotropy ratio)
- init_cond: Initial groundwater heads

Each parameter is a 2D list: [nodes][layers]
"""

import pytest
import os
import sys
import inspect

# Add the iwfm directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from iwfm.iwfm_read_gw_params import iwfm_read_gw_params

# Path to example files
EXAMPLE_GW_FILE = os.path.join(
    os.path.dirname(__file__),
    'C2VSimCG-2021', 'Simulation', 'Groundwater', 'C2VSimCG_Groundwater1974.dat'
)

# Check if example files exist
EXAMPLE_FILES_EXIST = os.path.exists(EXAMPLE_GW_FILE)


class TestIwfmReadGwParamsFunctionExists:
    """Test that iwfm_read_gw_params function exists and has correct signature."""

    def test_function_exists(self):
        """Test that iwfm_read_gw_params function is importable."""
        assert iwfm_read_gw_params is not None

    def test_function_is_callable(self):
        """Test that iwfm_read_gw_params is callable."""
        assert callable(iwfm_read_gw_params)

    def test_function_has_docstring(self):
        """Test that iwfm_read_gw_params has a docstring."""
        assert iwfm_read_gw_params.__doc__ is not None
        assert len(iwfm_read_gw_params.__doc__) > 0

    def test_function_signature(self):
        """Test that iwfm_read_gw_params has the expected parameters."""
        sig = inspect.signature(iwfm_read_gw_params)
        params = list(sig.parameters.keys())

        assert 'gw_file' in params


@pytest.mark.skipif(not EXAMPLE_FILES_EXIST,
                    reason="Example groundwater file not available")
class TestIwfmReadGwParamsReturnValue:
    """Test the return value structure of iwfm_read_gw_params."""

    def test_returns_list(self):
        """Test that iwfm_read_gw_params returns a list."""
        result = iwfm_read_gw_params(EXAMPLE_GW_FILE)
        assert isinstance(result, list)

    def test_returns_six_parameters(self):
        """Test that result contains 6 parameters."""
        result = iwfm_read_gw_params(EXAMPLE_GW_FILE)
        assert len(result) == 6

    def test_all_parameters_are_lists(self):
        """Test that all returned parameters are lists."""
        result = iwfm_read_gw_params(EXAMPLE_GW_FILE)
        for i, param in enumerate(result):
            assert isinstance(param, list), f"Parameter {i} is not a list"


@pytest.mark.skipif(not EXAMPLE_FILES_EXIST,
                    reason="Example groundwater file not available")
class TestIwfmReadGwParamsKh:
    """Test Kh (hydraulic conductivity) parameter."""

    def test_kh_is_first_parameter(self):
        """Test that Kh is the first parameter returned."""
        result = iwfm_read_gw_params(EXAMPLE_GW_FILE)
        Kh = result[0]
        assert isinstance(Kh, list)
        assert len(Kh) > 0

    def test_kh_has_entries_for_all_nodes(self):
        """Test that Kh has entries for all nodes (1393 for C2VSimCG)."""
        result = iwfm_read_gw_params(EXAMPLE_GW_FILE)
        Kh = result[0]
        assert len(Kh) == 1393

    def test_kh_has_entries_for_all_layers(self):
        """Test that each Kh node has entries for all layers (4 for C2VSimCG)."""
        result = iwfm_read_gw_params(EXAMPLE_GW_FILE)
        Kh = result[0]
        for node_idx, node_kh in enumerate(Kh[:10]):  # Check first 10
            assert len(node_kh) == 4, f"Node {node_idx} has {len(node_kh)} layers, expected 4"

    def test_kh_values_are_numeric(self):
        """Test that Kh values are numeric."""
        result = iwfm_read_gw_params(EXAMPLE_GW_FILE)
        Kh = result[0]
        for node_kh in Kh[:10]:  # Check first 10 nodes
            for layer_val in node_kh:
                assert isinstance(layer_val, (int, float))

    def test_kh_values_are_positive(self):
        """Test that Kh values are positive (physical requirement)."""
        result = iwfm_read_gw_params(EXAMPLE_GW_FILE)
        Kh = result[0]
        for node_kh in Kh[:10]:  # Check first 10 nodes
            for layer_val in node_kh:
                assert layer_val >= 0


@pytest.mark.skipif(not EXAMPLE_FILES_EXIST,
                    reason="Example groundwater file not available")
class TestIwfmReadGwParamsSs:
    """Test Ss (specific storage) parameter."""

    def test_ss_is_second_parameter(self):
        """Test that Ss is the second parameter returned."""
        result = iwfm_read_gw_params(EXAMPLE_GW_FILE)
        Ss = result[1]
        assert isinstance(Ss, list)
        assert len(Ss) > 0

    def test_ss_has_entries_for_all_nodes(self):
        """Test that Ss has entries for all nodes."""
        result = iwfm_read_gw_params(EXAMPLE_GW_FILE)
        Ss = result[1]
        assert len(Ss) == 1393

    def test_ss_values_are_non_negative(self):
        """Test that Ss values are non-negative."""
        result = iwfm_read_gw_params(EXAMPLE_GW_FILE)
        Ss = result[1]
        for node_ss in Ss[:10]:  # Check first 10 nodes
            for layer_val in node_ss:
                assert layer_val >= 0


@pytest.mark.skipif(not EXAMPLE_FILES_EXIST,
                    reason="Example groundwater file not available")
class TestIwfmReadGwParamsSy:
    """Test Sy (specific yield) parameter."""

    def test_sy_is_third_parameter(self):
        """Test that Sy is the third parameter returned."""
        result = iwfm_read_gw_params(EXAMPLE_GW_FILE)
        Sy = result[2]
        assert isinstance(Sy, list)
        assert len(Sy) > 0

    def test_sy_has_entries_for_all_nodes(self):
        """Test that Sy has entries for all nodes."""
        result = iwfm_read_gw_params(EXAMPLE_GW_FILE)
        Sy = result[2]
        assert len(Sy) == 1393

    def test_sy_values_in_valid_range(self):
        """Test that Sy values are in valid range (0 to 1)."""
        result = iwfm_read_gw_params(EXAMPLE_GW_FILE)
        Sy = result[2]
        for node_sy in Sy[:10]:  # Check first 10 nodes
            for layer_val in node_sy:
                assert 0 <= layer_val <= 1, f"Sy value {layer_val} out of range [0, 1]"


@pytest.mark.skipif(not EXAMPLE_FILES_EXIST,
                    reason="Example groundwater file not available")
class TestIwfmReadGwParamsKq:
    """Test Kq (horizontal anisotropy ratio) parameter."""

    def test_kq_is_fourth_parameter(self):
        """Test that Kq is the fourth parameter returned."""
        result = iwfm_read_gw_params(EXAMPLE_GW_FILE)
        Kq = result[3]
        assert isinstance(Kq, list)
        assert len(Kq) > 0

    def test_kq_has_entries_for_all_nodes(self):
        """Test that Kq has entries for all nodes."""
        result = iwfm_read_gw_params(EXAMPLE_GW_FILE)
        Kq = result[3]
        assert len(Kq) == 1393


@pytest.mark.skipif(not EXAMPLE_FILES_EXIST,
                    reason="Example groundwater file not available")
class TestIwfmReadGwParamsKv:
    """Test Kv (vertical hydraulic conductivity/anisotropy) parameter."""

    def test_kv_is_fifth_parameter(self):
        """Test that Kv is the fifth parameter returned."""
        result = iwfm_read_gw_params(EXAMPLE_GW_FILE)
        Kv = result[4]
        assert isinstance(Kv, list)
        assert len(Kv) > 0

    def test_kv_has_entries_for_all_nodes(self):
        """Test that Kv has entries for all nodes."""
        result = iwfm_read_gw_params(EXAMPLE_GW_FILE)
        Kv = result[4]
        assert len(Kv) == 1393

    def test_kv_values_are_non_negative(self):
        """Test that Kv values are non-negative."""
        result = iwfm_read_gw_params(EXAMPLE_GW_FILE)
        Kv = result[4]
        for node_kv in Kv[:10]:  # Check first 10 nodes
            for layer_val in node_kv:
                assert layer_val >= 0


@pytest.mark.skipif(not EXAMPLE_FILES_EXIST,
                    reason="Example groundwater file not available")
class TestIwfmReadGwParamsInitCond:
    """Test init_cond (initial conditions) parameter."""

    def test_init_cond_is_sixth_parameter(self):
        """Test that init_cond is the sixth parameter returned."""
        result = iwfm_read_gw_params(EXAMPLE_GW_FILE)
        init_cond = result[5]
        assert isinstance(init_cond, list)
        assert len(init_cond) > 0

    def test_init_cond_has_entries_for_all_nodes(self):
        """Test that init_cond has entries for all nodes."""
        result = iwfm_read_gw_params(EXAMPLE_GW_FILE)
        init_cond = result[5]
        assert len(init_cond) == 1393

    def test_init_cond_includes_node_id(self):
        """Test that init_cond includes node ID as first element."""
        result = iwfm_read_gw_params(EXAMPLE_GW_FILE)
        init_cond = result[5]

        # Each entry should have node_id followed by layer values
        # So length should be 1 + number_of_layers = 5 for C2VSimCG
        assert len(init_cond[0]) == 5  # node_id + 4 layers

    def test_init_cond_node_ids_sequential(self):
        """Test that init_cond node IDs are sequential."""
        result = iwfm_read_gw_params(EXAMPLE_GW_FILE)
        init_cond = result[5]

        # First node should be 1
        assert init_cond[0][0] == 1
        # Last node should be 1393
        assert init_cond[-1][0] == 1393

    def test_init_cond_head_values_reasonable(self):
        """Test that initial head values are reasonable."""
        result = iwfm_read_gw_params(EXAMPLE_GW_FILE)
        init_cond = result[5]

        for node_ic in init_cond[:10]:  # Check first 10 nodes
            # Skip first element (node_id), check head values
            for head in node_ic[1:]:
                # Heads should be reasonable (not extremely negative or high)
                # Typical range for California Central Valley is -100 to 1000 ft
                assert -500 < head < 2000, f"Head value {head} seems unreasonable"


@pytest.mark.skipif(not EXAMPLE_FILES_EXIST,
                    reason="Example groundwater file not available")
class TestIwfmReadGwParamsC2VSimCGSpecific:
    """Test C2VSimCG-specific expectations for iwfm_read_gw_params."""

    def test_c2vsimcg_node_count(self):
        """Test that C2VSimCG has 1393 nodes."""
        result = iwfm_read_gw_params(EXAMPLE_GW_FILE)
        Kh = result[0]
        assert len(Kh) == 1393

    def test_c2vsimcg_layer_count(self):
        """Test that C2VSimCG has 4 layers."""
        result = iwfm_read_gw_params(EXAMPLE_GW_FILE)
        Kh = result[0]
        assert len(Kh[0]) == 4

    def test_all_parameters_same_node_count(self):
        """Test that all parameters have same number of nodes."""
        result = iwfm_read_gw_params(EXAMPLE_GW_FILE)

        Kh = result[0]
        Ss = result[1]
        Sy = result[2]
        Kq = result[3]
        Kv = result[4]
        init_cond = result[5]

        assert len(Kh) == len(Ss) == len(Sy) == len(Kq) == len(Kv) == len(init_cond)

    def test_all_parameters_same_layer_count(self):
        """Test that all parameters have same number of layers per node."""
        result = iwfm_read_gw_params(EXAMPLE_GW_FILE)

        Kh = result[0]
        Ss = result[1]
        Sy = result[2]
        Kq = result[3]
        Kv = result[4]

        # Check first few nodes
        for i in range(10):
            layers_kh = len(Kh[i])
            assert len(Ss[i]) == layers_kh
            assert len(Sy[i]) == layers_kh
            assert len(Kq[i]) == layers_kh
            assert len(Kv[i]) == layers_kh


@pytest.mark.skipif(not EXAMPLE_FILES_EXIST,
                    reason="Example groundwater file not available")
class TestIwfmReadGwParamsDataIntegrity:
    """Test data integrity of iwfm_read_gw_params results."""

    def test_consistent_results(self):
        """Test that results are consistent for same input."""
        result1 = iwfm_read_gw_params(EXAMPLE_GW_FILE)
        result2 = iwfm_read_gw_params(EXAMPLE_GW_FILE)

        # Check Kh values match
        for i in range(10):
            for j in range(4):
                assert result1[0][i][j] == result2[0][i][j]

    def test_no_none_values_in_parameters(self):
        """Test that there are no None values in parameters."""
        result = iwfm_read_gw_params(EXAMPLE_GW_FILE)

        for param_idx, param in enumerate(result[:5]):  # First 5 are 2D arrays
            for node_idx, node_vals in enumerate(param[:10]):
                for layer_idx, val in enumerate(node_vals):
                    assert val is not None, f"None found at param {param_idx}, node {node_idx}, layer {layer_idx}"

    def test_parameter_values_vary(self):
        """Test that parameter values vary across nodes (not all same)."""
        result = iwfm_read_gw_params(EXAMPLE_GW_FILE)
        Kh = result[0]

        # Collect all first-layer Kh values
        kh_layer1 = [node_kh[0] for node_kh in Kh]

        # Should have some variation
        unique_values = set(kh_layer1)
        assert len(unique_values) > 1, "All Kh values are identical"


class TestIwfmReadGwParamsErrorHandling:
    """Test error handling in iwfm_read_gw_params."""

    def test_nonexistent_file_raises_error(self):
        """Test that nonexistent file raises an error."""
        with pytest.raises(FileNotFoundError):
            iwfm_read_gw_params('/nonexistent/groundwater.dat')
