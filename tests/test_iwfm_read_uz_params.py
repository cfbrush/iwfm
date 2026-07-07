# test_iwfm_read_uz_params.py
# Tests for iwfm_read_uz_params function
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
Tests for iwfm.iwfm_read_uz_params function.

The iwfm_read_uz_params function reads an IWFM Simulation Unsaturated Zone file
and returns a list of unsaturated zone parameters.

Example files used for testing:
- Unsaturated Zone file: iwfm/tests/C2VSimCG-2021/Simulation/C2VSimCG_Unsat.dat

C2VSimCG model characteristics:
- 1,392 elements
- 2 layers

Returns a list of 6 parameters:
- pd: Thickness of unsaturated layer [L]
- pn: Total porosity [L/L]
- pi: Pore size distribution index [dimensionless]
- pk: Hydraulic conductivity [L/T]
- prhc: Method to represent hydraulic conductivity vs. moisture content curve (1=Campbell, 2=van Genucten-Mualem)
- ic: Initial conditions (moisture content)

Each parameter (except ic) is a 2D list: [elements][layers]
"""

import pytest
import os
import sys
import inspect

# Add the iwfm directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from iwfm.iwfm_read_uz_params import iwfm_read_uz_params

# Path to example files
EXAMPLE_UZ_FILE = os.path.join(
    os.path.dirname(__file__),
    'C2VSimCG-2021', 'Simulation', 'C2VSimCG_Unsat.dat'
)

# Check if example files exist
EXAMPLE_FILES_EXIST = os.path.exists(EXAMPLE_UZ_FILE)


class TestIwfmReadUzParamsFunctionExists:
    """Test that iwfm_read_uz_params function exists and has correct signature."""

    def test_function_exists(self):
        """Test that iwfm_read_uz_params function is importable."""
        assert iwfm_read_uz_params is not None

    def test_function_is_callable(self):
        """Test that iwfm_read_uz_params is callable."""
        assert callable(iwfm_read_uz_params)

    def test_function_has_docstring(self):
        """Test that iwfm_read_uz_params has a docstring."""
        assert iwfm_read_uz_params.__doc__ is not None
        assert len(iwfm_read_uz_params.__doc__) > 0

    def test_function_signature(self):
        """Test that iwfm_read_uz_params has the expected parameters."""
        sig = inspect.signature(iwfm_read_uz_params)
        params = list(sig.parameters.keys())

        assert 'uz_file' in params
        assert 'verbose' in params

    def test_verbose_default_is_false(self):
        """Test that verbose parameter defaults to False."""
        sig = inspect.signature(iwfm_read_uz_params)
        verbose_param = sig.parameters.get('verbose')

        assert verbose_param is not None
        assert verbose_param.default is False


@pytest.mark.skipif(not EXAMPLE_FILES_EXIST,
                    reason="Example unsaturated zone file not available")
class TestIwfmReadUzParamsReturnValue:
    """Test the return value structure of iwfm_read_uz_params."""

    def test_returns_list(self):
        """Test that iwfm_read_uz_params returns a list."""
        result = iwfm_read_uz_params(EXAMPLE_UZ_FILE)
        assert isinstance(result, list)

    def test_returns_six_parameters(self):
        """Test that result contains 6 parameters."""
        result = iwfm_read_uz_params(EXAMPLE_UZ_FILE)
        assert len(result) == 6

    def test_all_parameters_are_lists(self):
        """Test that all returned parameters are lists."""
        result = iwfm_read_uz_params(EXAMPLE_UZ_FILE)
        for i, param in enumerate(result):
            assert isinstance(param, list), f"Parameter {i} is not a list"


@pytest.mark.skipif(not EXAMPLE_FILES_EXIST,
                    reason="Example unsaturated zone file not available")
class TestIwfmReadUzParamsPd:
    """Test pd (unsaturated layer thickness) parameter."""

    def test_pd_is_first_parameter(self):
        """Test that pd is the first parameter returned."""
        result = iwfm_read_uz_params(EXAMPLE_UZ_FILE)
        pd = result[0]
        assert isinstance(pd, list)
        assert len(pd) > 0

    def test_pd_has_entries_for_all_elements(self):
        """Test that pd has entries for all elements (1392 for C2VSimCG)."""
        result = iwfm_read_uz_params(EXAMPLE_UZ_FILE)
        pd = result[0]
        assert len(pd) == 1392

    def test_pd_has_entries_for_all_layers(self):
        """Test that each pd element has entries for all layers (2 for C2VSimCG)."""
        result = iwfm_read_uz_params(EXAMPLE_UZ_FILE)
        pd = result[0]
        for elem_idx, elem_pd in enumerate(pd[:10]):  # Check first 10
            assert len(elem_pd) == 2, f"Element {elem_idx} has {len(elem_pd)} layers, expected 2"

    def test_pd_values_are_numeric(self):
        """Test that pd values are numeric."""
        result = iwfm_read_uz_params(EXAMPLE_UZ_FILE)
        pd = result[0]
        for elem_pd in pd[:10]:  # Check first 10 elements
            for layer_val in elem_pd:
                assert isinstance(layer_val, (int, float))

    def test_pd_values_are_positive(self):
        """Test that pd values are positive (physical requirement)."""
        result = iwfm_read_uz_params(EXAMPLE_UZ_FILE)
        pd = result[0]
        for elem_pd in pd[:10]:  # Check first 10 elements
            for layer_val in elem_pd:
                assert layer_val >= 0

    def test_pd_first_element_values(self):
        """Test first element pd values match expected (21.10 for both layers)."""
        result = iwfm_read_uz_params(EXAMPLE_UZ_FILE)
        pd = result[0]
        # From file: element 1 has pd=21.10 for both layers
        assert abs(pd[0][0] - 21.10) < 0.01
        assert abs(pd[0][1] - 21.10) < 0.01


@pytest.mark.skipif(not EXAMPLE_FILES_EXIST,
                    reason="Example unsaturated zone file not available")
class TestIwfmReadUzParamsPn:
    """Test pn (total porosity) parameter."""

    def test_pn_is_second_parameter(self):
        """Test that pn is the second parameter returned."""
        result = iwfm_read_uz_params(EXAMPLE_UZ_FILE)
        pn = result[1]
        assert isinstance(pn, list)
        assert len(pn) > 0

    def test_pn_has_entries_for_all_elements(self):
        """Test that pn has entries for all elements."""
        result = iwfm_read_uz_params(EXAMPLE_UZ_FILE)
        pn = result[1]
        assert len(pn) == 1392

    def test_pn_values_in_valid_range(self):
        """Test that pn (porosity) values are in valid range (0 to 1)."""
        result = iwfm_read_uz_params(EXAMPLE_UZ_FILE)
        pn = result[1]
        for elem_pn in pn[:10]:  # Check first 10 elements
            for layer_val in elem_pn:
                assert 0 <= layer_val <= 1, f"Porosity value {layer_val} out of range [0, 1]"

    def test_pn_first_element_values(self):
        """Test first element pn values match expected."""
        result = iwfm_read_uz_params(EXAMPLE_UZ_FILE)
        pn = result[1]
        # From file: element 1 has pn=0.11953 (layer 1), 0.11987 (layer 2)
        assert abs(pn[0][0] - 0.11953) < 0.0001
        assert abs(pn[0][1] - 0.11987) < 0.0001


@pytest.mark.skipif(not EXAMPLE_FILES_EXIST,
                    reason="Example unsaturated zone file not available")
class TestIwfmReadUzParamsPi:
    """Test pi (pore size distribution index) parameter."""

    def test_pi_is_third_parameter(self):
        """Test that pi is the third parameter returned."""
        result = iwfm_read_uz_params(EXAMPLE_UZ_FILE)
        pi = result[2]
        assert isinstance(pi, list)
        assert len(pi) > 0

    def test_pi_has_entries_for_all_elements(self):
        """Test that pi has entries for all elements."""
        result = iwfm_read_uz_params(EXAMPLE_UZ_FILE)
        pi = result[2]
        assert len(pi) == 1392

    def test_pi_values_are_positive(self):
        """Test that pi values are positive."""
        result = iwfm_read_uz_params(EXAMPLE_UZ_FILE)
        pi = result[2]
        for elem_pi in pi[:10]:  # Check first 10 elements
            for layer_val in elem_pi:
                assert layer_val >= 0

    def test_pi_first_element_values(self):
        """Test first element pi values match expected (0.4 for both layers)."""
        result = iwfm_read_uz_params(EXAMPLE_UZ_FILE)
        pi = result[2]
        # From file: element 1 has pi=0.4 for both layers
        assert abs(pi[0][0] - 0.4) < 0.01
        assert abs(pi[0][1] - 0.4) < 0.01


@pytest.mark.skipif(not EXAMPLE_FILES_EXIST,
                    reason="Example unsaturated zone file not available")
class TestIwfmReadUzParamsPk:
    """Test pk (hydraulic conductivity) parameter."""

    def test_pk_is_fourth_parameter(self):
        """Test that pk is the fourth parameter returned."""
        result = iwfm_read_uz_params(EXAMPLE_UZ_FILE)
        pk = result[3]
        assert isinstance(pk, list)
        assert len(pk) > 0

    def test_pk_has_entries_for_all_elements(self):
        """Test that pk has entries for all elements."""
        result = iwfm_read_uz_params(EXAMPLE_UZ_FILE)
        pk = result[3]
        assert len(pk) == 1392

    def test_pk_values_are_positive(self):
        """Test that pk values are positive (physical requirement)."""
        result = iwfm_read_uz_params(EXAMPLE_UZ_FILE)
        pk = result[3]
        for elem_pk in pk[:10]:  # Check first 10 elements
            for layer_val in elem_pk:
                assert layer_val >= 0

    def test_pk_first_element_values(self):
        """Test first element pk values match expected."""
        result = iwfm_read_uz_params(EXAMPLE_UZ_FILE)
        pk = result[3]
        # From file: element 1 has pk=0.99997 (layer 1), 1.00010 (layer 2)
        assert abs(pk[0][0] - 0.99997) < 0.0001
        assert abs(pk[0][1] - 1.00010) < 0.0001


@pytest.mark.skipif(not EXAMPLE_FILES_EXIST,
                    reason="Example unsaturated zone file not available")
class TestIwfmReadUzParamsPrhc:
    """Test prhc (hydraulic conductivity method) parameter."""

    def test_prhc_is_fifth_parameter(self):
        """Test that prhc is the fifth parameter returned."""
        result = iwfm_read_uz_params(EXAMPLE_UZ_FILE)
        prhc = result[4]
        assert isinstance(prhc, list)
        assert len(prhc) > 0

    def test_prhc_has_entries_for_all_elements(self):
        """Test that prhc has entries for all elements."""
        result = iwfm_read_uz_params(EXAMPLE_UZ_FILE)
        prhc = result[4]
        assert len(prhc) == 1392

    def test_prhc_values_are_valid_method(self):
        """Test that prhc values are valid methods (1 or 2)."""
        result = iwfm_read_uz_params(EXAMPLE_UZ_FILE)
        prhc = result[4]
        for elem_prhc in prhc[:10]:  # Check first 10 elements
            for layer_val in elem_prhc:
                assert layer_val in [1, 2], f"PRHC value {layer_val} not in [1, 2]"

    def test_prhc_first_element_values(self):
        """Test first element prhc values match expected (1 for both layers)."""
        result = iwfm_read_uz_params(EXAMPLE_UZ_FILE)
        prhc = result[4]
        # From file: element 1 has prhc=1 for both layers (Campbell's equation)
        assert prhc[0][0] == 1
        assert prhc[0][1] == 1


@pytest.mark.skipif(not EXAMPLE_FILES_EXIST,
                    reason="Example unsaturated zone file not available")
class TestIwfmReadUzParamsIc:
    """Test ic (initial conditions) parameter."""

    def test_ic_is_sixth_parameter(self):
        """Test that ic is the sixth parameter returned."""
        result = iwfm_read_uz_params(EXAMPLE_UZ_FILE)
        ic = result[5]
        assert isinstance(ic, list)
        assert len(ic) > 0

    def test_ic_has_entries_for_all_elements(self):
        """Test that ic has entries for all elements."""
        result = iwfm_read_uz_params(EXAMPLE_UZ_FILE)
        ic = result[5]
        assert len(ic) == 1392

    def test_ic_includes_element_id(self):
        """Test that ic includes element ID as first element."""
        result = iwfm_read_uz_params(EXAMPLE_UZ_FILE)
        ic = result[5]

        # Each entry should have element_id followed by layer values
        # So length should be 1 + number_of_layers = 3 for C2VSimCG
        assert len(ic[0]) == 3  # element_id + 2 layers

    def test_ic_element_ids_sequential(self):
        """Test that ic element IDs are sequential."""
        result = iwfm_read_uz_params(EXAMPLE_UZ_FILE)
        ic = result[5]

        # First element should be 1
        assert ic[0][0] == 1
        # Last element should be 1392
        assert ic[-1][0] == 1392

    def test_ic_moisture_values_in_valid_range(self):
        """Test that ic moisture values are in valid range (0 to porosity)."""
        result = iwfm_read_uz_params(EXAMPLE_UZ_FILE)
        ic = result[5]

        for elem_ic in ic[:10]:  # Check first 10 elements
            # Skip first element (element_id), check moisture values
            for moisture in elem_ic[1:]:
                # Moisture content should be between 0 and porosity (which is < 1)
                assert 0 <= moisture <= 1, f"Moisture value {moisture} out of range [0, 1]"


@pytest.mark.skipif(not EXAMPLE_FILES_EXIST,
                    reason="Example unsaturated zone file not available")
class TestIwfmReadUzParamsC2VSimCGSpecific:
    """Test C2VSimCG-specific expectations for iwfm_read_uz_params."""

    def test_c2vsimcg_element_count(self):
        """Test that C2VSimCG has 1392 elements."""
        result = iwfm_read_uz_params(EXAMPLE_UZ_FILE)
        pd = result[0]
        assert len(pd) == 1392

    def test_c2vsimcg_layer_count(self):
        """Test that C2VSimCG has 2 layers."""
        result = iwfm_read_uz_params(EXAMPLE_UZ_FILE)
        pd = result[0]
        assert len(pd[0]) == 2

    def test_all_parameters_same_element_count(self):
        """Test that all parameters have same number of elements."""
        result = iwfm_read_uz_params(EXAMPLE_UZ_FILE)

        pd = result[0]
        pn = result[1]
        pi = result[2]
        pk = result[3]
        prhc = result[4]
        ic = result[5]

        assert len(pd) == len(pn) == len(pi) == len(pk) == len(prhc) == len(ic)

    def test_all_parameters_same_layer_count(self):
        """Test that all parameters have same number of layers per element."""
        result = iwfm_read_uz_params(EXAMPLE_UZ_FILE)

        pd = result[0]
        pn = result[1]
        pi = result[2]
        pk = result[3]
        prhc = result[4]

        # Check first few elements
        for i in range(10):
            layers_pd = len(pd[i])
            assert len(pn[i]) == layers_pd
            assert len(pi[i]) == layers_pd
            assert len(pk[i]) == layers_pd
            assert len(prhc[i]) == layers_pd


@pytest.mark.skipif(not EXAMPLE_FILES_EXIST,
                    reason="Example unsaturated zone file not available")
class TestIwfmReadUzParamsDataIntegrity:
    """Test data integrity of iwfm_read_uz_params results."""

    def test_consistent_results(self):
        """Test that results are consistent for same input."""
        result1 = iwfm_read_uz_params(EXAMPLE_UZ_FILE)
        result2 = iwfm_read_uz_params(EXAMPLE_UZ_FILE)

        # Check pd values match
        for i in range(10):
            for j in range(2):
                assert result1[0][i][j] == result2[0][i][j]

    def test_no_none_values_in_parameters(self):
        """Test that there are no None values in parameters."""
        result = iwfm_read_uz_params(EXAMPLE_UZ_FILE)

        for param_idx, param in enumerate(result[:5]):  # First 5 are 2D arrays
            for elem_idx, elem_vals in enumerate(param[:10]):
                for layer_idx, val in enumerate(elem_vals):
                    assert val is not None, f"None found at param {param_idx}, elem {elem_idx}, layer {layer_idx}"

    def test_parameter_values_vary(self):
        """Test that parameter values vary across elements (not all same)."""
        result = iwfm_read_uz_params(EXAMPLE_UZ_FILE)
        pn = result[1]  # porosity

        # Collect all first-layer pn values
        pn_layer1 = [elem_pn[0] for elem_pn in pn]

        # Should have some variation
        unique_values = set(pn_layer1)
        assert len(unique_values) > 1, "All porosity values are identical"


@pytest.mark.skipif(not EXAMPLE_FILES_EXIST,
                    reason="Example unsaturated zone file not available")
class TestIwfmReadUzParamsVerbose:
    """Test verbose parameter of iwfm_read_uz_params."""

    def test_verbose_false_no_output(self, capsys):
        """Test that verbose=False produces no stdout output."""
        iwfm_read_uz_params(EXAMPLE_UZ_FILE, verbose=False)
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_verbose_true_produces_output(self, capsys):
        """Test that verbose=True produces stdout output."""
        iwfm_read_uz_params(EXAMPLE_UZ_FILE, verbose=True)
        captured = capsys.readouterr()
        assert len(captured.out) > 0


class TestIwfmReadUzParamsErrorHandling:
    """Test error handling in iwfm_read_uz_params."""

    def test_nonexistent_file_raises_error(self):
        """Test that nonexistent file raises an error."""
        with pytest.raises(FileNotFoundError):
            iwfm_read_uz_params('/nonexistent/unsat.dat')
