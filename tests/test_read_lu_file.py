# test_read_lu_file.py
# unit tests for read_lu_file function
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


def create_lu_file(filepath, dates, elements_data, skip=4):
    """Helper to create a minimal IWFM land use file for testing.

    Parameters
    ----------
    filepath : path
        Path to write the file
    dates : list
        List of DSS dates (e.g., ['09/30/1974_24:00', '10/31/1974_24:00'])
    elements_data : list
        List of time step data, where each time step is a list of
        (elem_id, values...) tuples
    skip : int
        Number of header rows to create
    """
    lines = []

    # Add comment header
    lines.append("C This is a test land use file")
    lines.append("C Created for testing read_lu_file")

    # Add header/spec lines (these are the 'skip' lines)
    for i in range(skip):
        lines.append(f" {i+1}.0                    / PARAM{i+1}")

    # Add comment before data
    lines.append("C Data section follows")

    # Add data for each time step
    for t, date in enumerate(dates):
        elem_data = elements_data[t]
        for i, elem_row in enumerate(elem_data):
            elem_id = elem_row[0]
            values = elem_row[1:]
            values_str = '\t'.join(str(v) for v in values)
            if i == 0:
                # First element includes the date
                lines.append(f"{date}\t{elem_id}\t{values_str}")
            else:
                # Subsequent elements have tabs before the element ID
                lines.append(f"\t\t\t{elem_id}\t{values_str}")

    filepath.write_text('\n'.join(lines))


class TestReadLuFile:
    """Tests for the read_lu_file function."""

    def test_basic_single_timestep(self, tmp_path):
        """Test reading file with single time step."""
        lu_file = tmp_path / "landuse.dat"
        dates = ['09/30/1974_24:00']
        elements_data = [
            [(1, 100.0, 50.0), (2, 200.0, 75.0), (3, 150.0, 25.0)]
        ]
        create_lu_file(lu_file, dates, elements_data)

        table, result_dates, elems = iwfm.read_lu_file(str(lu_file))

        assert len(result_dates) == 1
        assert result_dates[0] == '09/30/1974_24:00'
        assert len(table) == 1
        assert len(table[0]) == 3  # 3 elements

    def test_multiple_timesteps(self, tmp_path):
        """Test reading file with multiple time steps."""
        lu_file = tmp_path / "landuse.dat"
        dates = ['09/30/1974_24:00', '10/31/1974_24:00', '11/30/1974_24:00']
        elements_data = [
            [(1, 100.0, 50.0), (2, 200.0, 75.0)],
            [(1, 110.0, 55.0), (2, 210.0, 80.0)],
            [(1, 120.0, 60.0), (2, 220.0, 85.0)],
        ]
        create_lu_file(lu_file, dates, elements_data)

        table, result_dates, elems = iwfm.read_lu_file(str(lu_file))

        assert len(result_dates) == 3
        assert len(table) == 3
        assert result_dates[0] == '09/30/1974_24:00'
        assert result_dates[1] == '10/31/1974_24:00'
        assert result_dates[2] == '11/30/1974_24:00'

    def test_returns_three_lists(self, tmp_path):
        """Test that function returns three lists."""
        lu_file = tmp_path / "landuse.dat"
        dates = ['09/30/1974_24:00']
        elements_data = [[(1, 100.0, 50.0)]]
        create_lu_file(lu_file, dates, elements_data)

        result = iwfm.read_lu_file(str(lu_file))

        assert isinstance(result, tuple)
        assert len(result) == 3
        table, dates_result, elems = result
        assert isinstance(table, list)
        assert isinstance(dates_result, list)
        assert isinstance(elems, list)

    def test_values_are_floats(self, tmp_path):
        """Test that land use values are returned as floats."""
        lu_file = tmp_path / "landuse.dat"
        dates = ['09/30/1974_24:00']
        elements_data = [[(1, 123.456, 78.901)]]
        create_lu_file(lu_file, dates, elements_data)

        table, _, _ = iwfm.read_lu_file(str(lu_file))

        values = table[0][0]
        for val in values:
            assert isinstance(val, float)

    def test_element_ids_are_integers(self, tmp_path):
        """Test that element IDs are returned as integers."""
        lu_file = tmp_path / "landuse.dat"
        dates = ['09/30/1974_24:00']
        elements_data = [[(42, 100.0, 50.0), (43, 200.0, 75.0)]]
        create_lu_file(lu_file, dates, elements_data)

        _, _, elems = iwfm.read_lu_file(str(lu_file))

        for elem_id in elems[0]:
            assert isinstance(elem_id, int)
        assert elems[0] == [42, 43]

    def test_table_structure(self, tmp_path):
        """Test table structure: [time_steps][elements][values]."""
        lu_file = tmp_path / "landuse.dat"
        dates = ['09/30/1974_24:00', '10/31/1974_24:00']
        elements_data = [
            [(1, 100.0, 50.0, 25.0), (2, 200.0, 75.0, 30.0)],
            [(1, 110.0, 55.0, 27.0), (2, 210.0, 80.0, 32.0)],
        ]
        create_lu_file(lu_file, dates, elements_data)

        table, _, _ = iwfm.read_lu_file(str(lu_file))

        # 2 time steps
        assert len(table) == 2
        # 2 elements per time step
        assert len(table[0]) == 2
        assert len(table[1]) == 2
        # 3 values per element
        assert len(table[0][0]) == 3
        assert len(table[1][1]) == 3

    def test_correct_values_extracted(self, tmp_path):
        """Test that correct values are extracted from file."""
        lu_file = tmp_path / "landuse.dat"
        dates = ['09/30/1974_24:00']
        elements_data = [
            [(1, 100.5, 50.25), (2, 200.75, 75.125)]
        ]
        create_lu_file(lu_file, dates, elements_data)

        table, _, elems = iwfm.read_lu_file(str(lu_file))

        # Check first element values
        assert table[0][0] == [100.5, 50.25]
        # Check second element values
        assert table[0][1] == [200.75, 75.125]
        # Check element IDs
        assert elems[0] == [1, 2]

    def test_custom_skip_parameter(self, tmp_path):
        """Test with custom skip parameter."""
        lu_file = tmp_path / "landuse.dat"
        dates = ['09/30/1974_24:00']
        elements_data = [[(1, 100.0, 50.0)]]
        # Create file with 6 header lines instead of default 4
        create_lu_file(lu_file, dates, elements_data, skip=6)

        table, result_dates, _ = iwfm.read_lu_file(str(lu_file), skip=6)

        assert len(result_dates) == 1
        assert result_dates[0] == '09/30/1974_24:00'

    def test_many_elements(self, tmp_path):
        """Test reading file with many elements."""
        lu_file = tmp_path / "landuse.dat"
        dates = ['09/30/1974_24:00']
        # Create 100 elements
        elements_data = [
            [(i, float(i*10), float(i*5)) for i in range(1, 101)]
        ]
        create_lu_file(lu_file, dates, elements_data)

        table, _, elems = iwfm.read_lu_file(str(lu_file))

        assert len(table[0]) == 100
        assert len(elems[0]) == 100
        assert elems[0][0] == 1
        assert elems[0][-1] == 100

    def test_many_land_use_types(self, tmp_path):
        """Test reading file with many land use types (columns)."""
        lu_file = tmp_path / "landuse.dat"
        dates = ['09/30/1974_24:00']
        # Create element with 10 land use type values
        elements_data = [
            [(1, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0)]
        ]
        create_lu_file(lu_file, dates, elements_data)

        table, _, _ = iwfm.read_lu_file(str(lu_file))

        assert len(table[0][0]) == 10
        assert table[0][0] == [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]

    def test_zero_values(self, tmp_path):
        """Test reading file with zero values."""
        lu_file = tmp_path / "landuse.dat"
        dates = ['09/30/1974_24:00']
        elements_data = [
            [(1, 0.0, 0.0), (2, 100.0, 0.0), (3, 0.0, 50.0)]
        ]
        create_lu_file(lu_file, dates, elements_data)

        table, _, _ = iwfm.read_lu_file(str(lu_file))

        assert table[0][0] == [0.0, 0.0]
        assert table[0][1] == [100.0, 0.0]
        assert table[0][2] == [0.0, 50.0]

    def test_large_values(self, tmp_path):
        """Test reading file with large values."""
        lu_file = tmp_path / "landuse.dat"
        dates = ['09/30/1974_24:00']
        elements_data = [
            [(1, 1234567.89, 9876543.21)]
        ]
        create_lu_file(lu_file, dates, elements_data)

        table, _, _ = iwfm.read_lu_file(str(lu_file))

        assert abs(table[0][0][0] - 1234567.89) < 0.01
        assert abs(table[0][0][1] - 9876543.21) < 0.01

    def test_small_decimal_values(self, tmp_path):
        """Test reading file with small decimal values."""
        lu_file = tmp_path / "landuse.dat"
        dates = ['09/30/1974_24:00']
        elements_data = [
            [(1, 0.00123, 0.00456)]
        ]
        create_lu_file(lu_file, dates, elements_data)

        table, _, _ = iwfm.read_lu_file(str(lu_file))

        assert abs(table[0][0][0] - 0.00123) < 0.00001
        assert abs(table[0][0][1] - 0.00456) < 0.00001

    def test_file_not_found_exits(self, tmp_path):
        """Test that nonexistent file causes system exit."""
        nonexistent = tmp_path / "nonexistent.dat"

        with pytest.raises(FileNotFoundError):
            iwfm.read_lu_file(str(nonexistent))

    def test_elems_list_per_timestep(self, tmp_path):
        """Test that elems list has entry for each time step."""
        lu_file = tmp_path / "landuse.dat"
        dates = ['09/30/1974_24:00', '10/31/1974_24:00']
        elements_data = [
            [(1, 100.0, 50.0), (2, 200.0, 75.0)],
            [(1, 110.0, 55.0), (2, 210.0, 80.0)],
        ]
        create_lu_file(lu_file, dates, elements_data)

        _, _, elems = iwfm.read_lu_file(str(lu_file))

        assert len(elems) == 2
        assert elems[0] == [1, 2]
        assert elems[1] == [1, 2]

    def test_different_date_formats(self, tmp_path):
        """Test reading files with different date formats."""
        lu_file = tmp_path / "landuse.dat"
        dates = ['01/31/2020_24:00', '12/31/2020_24:00']
        elements_data = [
            [(1, 100.0, 50.0)],
            [(1, 110.0, 55.0)],
        ]
        create_lu_file(lu_file, dates, elements_data)

        _, result_dates, _ = iwfm.read_lu_file(str(lu_file))

        assert result_dates[0] == '01/31/2020_24:00'
        assert result_dates[1] == '12/31/2020_24:00'

    def test_single_land_use_type(self, tmp_path):
        """Test reading file with single land use type (one column)."""
        lu_file = tmp_path / "landuse.dat"
        dates = ['09/30/1974_24:00']
        elements_data = [
            [(1, 100.0), (2, 200.0), (3, 300.0)]
        ]
        create_lu_file(lu_file, dates, elements_data)

        table, _, _ = iwfm.read_lu_file(str(lu_file))

        assert len(table[0][0]) == 1
        assert table[0][0] == [100.0]
        assert table[0][1] == [200.0]
        assert table[0][2] == [300.0]


class TestReadLuFileComments:
    """Tests for handling of comment lines."""

    def test_multiple_comment_styles(self, tmp_path):
        """Test file with multiple comment styles (C, c, *, #)."""
        lu_file = tmp_path / "landuse.dat"
        content = """\
C Comment with capital C
c Comment with lowercase c
* Comment with asterisk
# Comment with hash
 1.0                    / PARAM1
 2.0                    / PARAM2
 3.0                    / PARAM3
 4.0                    / PARAM4
C Another comment before data
09/30/1974_24:00\t1\t100.0\t50.0
"""
        lu_file.write_text(content)

        table, dates, _ = iwfm.read_lu_file(str(lu_file))

        assert len(dates) == 1
        assert dates[0] == '09/30/1974_24:00'

    def test_header_without_interspersed_comments(self, tmp_path):
        """Test file with header lines followed by comments before data."""
        lu_file = tmp_path / "landuse.dat"
        # The function skips initial comments, then skips 'skip' number of
        # non-comment lines, then skips any comments before the data
        content = """\
C Header comment
 1.0                    / PARAM1
 2.0                    / PARAM2
 3.0                    / PARAM3
 4.0                    / PARAM4
C Data section comment
C Another comment
09/30/1974_24:00\t1\t100.0\t50.0
"""
        lu_file.write_text(content)

        table, dates, _ = iwfm.read_lu_file(str(lu_file))

        assert len(dates) == 1
        assert dates[0] == '09/30/1974_24:00'


class TestReadLuFileRealData:
    """Tests using real IWFM test data files."""

    def test_with_real_native_veg_file(self):
        """Test with actual C2VSimCG native vegetation file if available."""
        test_file = os.path.join(
            os.path.dirname(__file__),
            'C2VSimCG-2021',
            'Simulation',
            'RootZone',
            'C2VSimCG_NativeVeg_Area.dat'
        )

        if not os.path.exists(test_file):
            pytest.skip("Test data file not available")

        table, dates, elems = iwfm.read_lu_file(test_file)

        # Verify we got lists back
        assert isinstance(table, list)
        assert isinstance(dates, list)
        assert isinstance(elems, list)

        # Should have at least one time step
        assert len(dates) > 0
        assert len(table) > 0
        assert len(elems) > 0

        # Check structure of first time step
        assert len(table[0]) > 0
        assert len(elems[0]) > 0

        # Check that values are floats
        first_values = table[0][0]
        for val in first_values:
            assert isinstance(val, float)

        # Check that element IDs are integers
        for elem_id in elems[0]:
            assert isinstance(elem_id, int)

        # First element should be 1
        assert elems[0][0] == 1

        # Check first date format
        assert '24:00' in dates[0]

    def test_real_file_data_consistency(self):
        """Test that real file has consistent data across time steps."""
        test_file = os.path.join(
            os.path.dirname(__file__),
            'C2VSimCG-2021',
            'Simulation',
            'RootZone',
            'C2VSimCG_NativeVeg_Area.dat'
        )

        if not os.path.exists(test_file):
            pytest.skip("Test data file not available")

        table, dates, elems = iwfm.read_lu_file(test_file)

        # All time steps should have same number of elements
        num_elements = len(elems[0])
        for t, elem_list in enumerate(elems):
            assert len(elem_list) == num_elements, \
                f"Time step {t} has {len(elem_list)} elements, expected {num_elements}"

        # All elements should have same number of land use types
        num_lu_types = len(table[0][0])
        for t, timestep_data in enumerate(table):
            for e, elem_data in enumerate(timestep_data):
                assert len(elem_data) == num_lu_types, \
                    f"Time {t}, element {e} has {len(elem_data)} values, expected {num_lu_types}"

    def test_real_file_known_values(self):
        """Test known values from the real file."""
        test_file = os.path.join(
            os.path.dirname(__file__),
            'C2VSimCG-2021',
            'Simulation',
            'RootZone',
            'C2VSimCG_NativeVeg_Area.dat'
        )

        if not os.path.exists(test_file):
            pytest.skip("Test data file not available")

        table, dates, elems = iwfm.read_lu_file(test_file)

        # Check first date
        assert dates[0] == '09/30/1974_24:00'

        # Check first element ID
        assert elems[0][0] == 1

        # Check known values from first element (from file inspection)
        # Element 1: ALANDNV=450.185, ALANDRV=154.017
        assert abs(table[0][0][0] - 450.185) < 0.01
        assert abs(table[0][0][1] - 154.017) < 0.01

        # Check second element: ALANDNV=156.854, ALANDRV=91.323
        assert elems[0][1] == 2
        assert abs(table[0][1][0] - 156.854) < 0.01
        assert abs(table[0][1][1] - 91.323) < 0.01
