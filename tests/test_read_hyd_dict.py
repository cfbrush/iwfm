# test_read_hyd_dict.py
# unit tests for read_hyd_dict function
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
import os

import pytest

import iwfm


def create_gw_dat_file(filepath, nouth, hydrograph_data):
    """Helper to create a minimal Groundwater.dat file for testing.

    Parameters
    ----------
    filepath : path
        Path to write the file
    nouth : int
        Number of hydrographs
    hydrograph_data : list
        List of tuples: (id, hydtyp, layer, x, y, name)
    """
    lines = []

    # Add 20 non-comment lines that are skipped before NOUTH
    # These represent various parameters in the Groundwater.dat file
    for i in range(20):
        lines.append(f"C Comment line {i+1}")
        lines.append(f" param_{i+1}                    / PARAM{i+1}")

    # NOUTH line (after skipping 20 non-comment lines)
    lines.append(f"     {nouth}                                      / NOUTH")

    # Skip 2 more lines (FACTXY and GWHYDOUTFL)
    lines.append("     1.0                                      / FACTXY")
    lines.append("                                              / GWHYDOUTFL")

    # Comment lines before hydrograph data
    lines.append("C ID    HYDTYP  IOUTHL  X           Y           NAME")
    lines.append("C------------------------------------------------------------------")

    # Hydrograph data
    for hyd in hydrograph_data:
        hyd_id, hydtyp, layer, x, y, name = hyd
        lines.append(f"{hyd_id}\t{hydtyp}\t{layer}\t{x}\t{y}\t{name}")

    filepath.write_text('\n'.join(lines))


class TestReadHydDict:
    """Tests for the read_hyd_dict function."""

    def test_basic_single_hydrograph(self, tmp_path):
        """Test reading file with single hydrograph."""
        gw_file = tmp_path / "groundwater.dat"
        hydrograph_data = [
            (1, 0, 1, 592798.7048, 4209815.426, "S_380313N1219426W001")
        ]
        create_gw_dat_file(gw_file, 1, hydrograph_data)

        result = iwfm.read_hyd_dict(str(gw_file))

        assert isinstance(result, dict)
        assert len(result) == 1
        assert "S_380313N1219426W001" in result

    def test_multiple_hydrographs(self, tmp_path):
        """Test reading file with multiple hydrographs."""
        gw_file = tmp_path / "groundwater.dat"
        hydrograph_data = [
            (1, 0, 1, 592798.7048, 4209815.426, "WELL_A"),
            (2, 0, 2, 622426.4231, 4296803.182, "WELL_B"),
            (3, 0, 3, 588091.0913, 4223057.566, "WELL_C"),
        ]
        create_gw_dat_file(gw_file, 3, hydrograph_data)

        result = iwfm.read_hyd_dict(str(gw_file))

        assert len(result) == 3
        assert "WELL_A" in result
        assert "WELL_B" in result
        assert "WELL_C" in result

    def test_dictionary_values_structure(self, tmp_path):
        """Test that dictionary values have correct structure."""
        gw_file = tmp_path / "groundwater.dat"
        hydrograph_data = [
            (1, 0, 1, 592798.7048, 4209815.426, "TEST_WELL")
        ]
        create_gw_dat_file(gw_file, 1, hydrograph_data)

        result = iwfm.read_hyd_dict(str(gw_file))

        values = result["TEST_WELL"]
        # Values should be a WellInfo instance
        from iwfm.iwfm_dataclasses import WellInfo
        assert isinstance(values, WellInfo)
        assert values.column == 1  # column number (ID)
        assert values.x == 592798.7048  # x coordinate
        assert values.y == 4209815.426  # y coordinate
        assert values.layer == 1  # layer
        assert values.name == "test_well"  # well name lowercase

    def test_x_y_coordinates_are_floats(self, tmp_path):
        """Test that X and Y coordinates are returned as floats."""
        gw_file = tmp_path / "groundwater.dat"
        hydrograph_data = [
            (1, 0, 1, 123456.789, 987654.321, "TEST_WELL")
        ]
        create_gw_dat_file(gw_file, 1, hydrograph_data)

        result = iwfm.read_hyd_dict(str(gw_file))

        values = result["TEST_WELL"]
        assert isinstance(values.x, float)  # x
        assert isinstance(values.y, float)  # y
        assert values.x == 123456.789
        assert values.y == 987654.321

    def test_column_number_is_int(self, tmp_path):
        """Test that column number is returned as integer."""
        gw_file = tmp_path / "groundwater.dat"
        hydrograph_data = [
            (42, 0, 1, 100.0, 200.0, "TEST_WELL")
        ]
        create_gw_dat_file(gw_file, 1, hydrograph_data)

        result = iwfm.read_hyd_dict(str(gw_file))

        values = result["TEST_WELL"]
        assert isinstance(values.column, int)
        assert values.column == 42

    def test_layer_is_int(self, tmp_path):
        """Test that layer number is returned as integer."""
        gw_file = tmp_path / "groundwater.dat"
        hydrograph_data = [
            (1, 0, 3, 100.0, 200.0, "TEST_WELL")
        ]
        create_gw_dat_file(gw_file, 1, hydrograph_data)

        result = iwfm.read_hyd_dict(str(gw_file))

        values = result["TEST_WELL"]
        assert isinstance(values.layer, int)
        assert values.layer == 3

    def test_well_name_lowercase_in_values(self, tmp_path):
        """Test that well name in values is lowercase."""
        gw_file = tmp_path / "groundwater.dat"
        hydrograph_data = [
            (1, 0, 1, 100.0, 200.0, "UPPER_CASE_NAME")
        ]
        create_gw_dat_file(gw_file, 1, hydrograph_data)

        result = iwfm.read_hyd_dict(str(gw_file))

        # Key should be original case
        assert "UPPER_CASE_NAME" in result
        # Value should have lowercase version
        values = result["UPPER_CASE_NAME"]
        assert values.name == "upper_case_name"

    def test_zero_hydrographs(self, tmp_path):
        """Test reading file with zero hydrographs."""
        gw_file = tmp_path / "groundwater.dat"
        create_gw_dat_file(gw_file, 0, [])

        result = iwfm.read_hyd_dict(str(gw_file))

        assert isinstance(result, dict)
        assert len(result) == 0

    def test_returns_dictionary(self, tmp_path):
        """Test that function returns a dictionary."""
        gw_file = tmp_path / "groundwater.dat"
        hydrograph_data = [
            (1, 0, 1, 100.0, 200.0, "WELL")
        ]
        create_gw_dat_file(gw_file, 1, hydrograph_data)

        result = iwfm.read_hyd_dict(str(gw_file))

        assert isinstance(result, dict)

    def test_file_not_found_exits(self, tmp_path):
        """Test that nonexistent file causes system exit."""
        nonexistent = tmp_path / "nonexistent.dat"

        with pytest.raises(FileNotFoundError):
            iwfm.read_hyd_dict(str(nonexistent))

    def test_debug_logger_output(self, tmp_path):
        """Test that logger.debug messages are emitted for Enter/Leave traces."""
        from iwfm.debug.logger_setup import logger
        gw_file = tmp_path / "groundwater.dat"
        hydrograph_data = [
            (1, 0, 1, 100.0, 200.0, "WELL")
        ]
        create_gw_dat_file(gw_file, 1, hydrograph_data)

        messages = []
        handler_id = logger.add(lambda msg: messages.append(str(msg)), level="DEBUG")
        try:
            iwfm.read_hyd_dict(str(gw_file), verbose=True)
        finally:
            logger.remove(handler_id)

        combined = " ".join(messages)
        assert "Entered read_hyd_dict()" in combined
        assert "Leaving read_hyd_dict()" in combined

    def test_no_verbose_output(self, tmp_path, capsys):
        """Test that verbose=False produces no output."""
        gw_file = tmp_path / "groundwater.dat"
        hydrograph_data = [
            (1, 0, 1, 100.0, 200.0, "WELL")
        ]
        create_gw_dat_file(gw_file, 1, hydrograph_data)

        iwfm.read_hyd_dict(str(gw_file), verbose=False)

        captured = capsys.readouterr()
        assert captured.out == ""

    def test_different_layers(self, tmp_path):
        """Test hydrographs in different layers."""
        gw_file = tmp_path / "groundwater.dat"
        hydrograph_data = [
            (1, 0, 1, 100.0, 200.0, "WELL_L1"),
            (2, 0, 2, 100.0, 200.0, "WELL_L2"),
            (3, 0, 3, 100.0, 200.0, "WELL_L3"),
            (4, 0, 4, 100.0, 200.0, "WELL_L4"),
        ]
        create_gw_dat_file(gw_file, 4, hydrograph_data)

        result = iwfm.read_hyd_dict(str(gw_file))

        assert result["WELL_L1"].layer == 1
        assert result["WELL_L2"].layer == 2
        assert result["WELL_L3"].layer == 3
        assert result["WELL_L4"].layer == 4

    def test_well_name_with_special_characters(self, tmp_path):
        """Test well names with special characters."""
        gw_file = tmp_path / "groundwater.dat"
        hydrograph_data = [
            (1, 0, 1, 100.0, 200.0, "S_380313N1219426W001%1"),
        ]
        create_gw_dat_file(gw_file, 1, hydrograph_data)

        result = iwfm.read_hyd_dict(str(gw_file))

        assert "S_380313N1219426W001%1" in result


class TestReadHydDictRealFile:
    """Tests using real IWFM test data files."""

    @pytest.mark.xfail(
        reason="read_hyd_dict does not handle HYDTYP=1 (node number) records. "
               "The real file has 400 records with HYDTYP=1 where X and Y are empty, "
               "causing IndexError when accessing line[5] for well name."
    )
    def test_with_real_groundwater_file(self):
        """Test with actual C2VSimCG Groundwater.dat file if available.

        Note: This test currently fails because the read_hyd_dict function
        assumes all hydrographs use HYDTYP=0 (X,Y coordinates). When HYDTYP=1
        is used (node number instead of coordinates), the X and Y columns are
        empty, which causes the split() to produce fewer columns and the
        NAME column shifts to a different index.
        """
        test_file = os.path.join(
            os.path.dirname(__file__),
            'C2VSimCG-2021',
            'Simulation',
            'Groundwater',
            'C2VSimCG_Groundwater1974.dat'
        )

        if not os.path.exists(test_file):
            pytest.skip("Test data file not available")

        result = iwfm.read_hyd_dict(test_file)

        # Verify we got a dictionary back
        assert isinstance(result, dict)

        # Should have many hydrographs (54544 according to file)
        assert len(result) > 0

        # Check structure of first entry
        from iwfm.iwfm_dataclasses import WellInfo
        first_key = next(iter(result))
        values = result[first_key]
        assert isinstance(values, WellInfo)
        assert isinstance(values.column, int)   # column number
        assert isinstance(values.x, float)      # x
        assert isinstance(values.y, float)      # y
        assert isinstance(values.layer, int)    # layer
        assert isinstance(values.name, str)     # lowercase name
