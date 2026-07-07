# test_get_change_col.py
# Unit tests for the get_change_col function in the iwfm package
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

# Import directly from module since it may not be exported in __init__.py
from iwfm.get_change_col import get_change_col


class TestGetChangeColFunctionExists:
    """Test that the get_change_col function exists and is callable."""

    def test_get_change_col_exists(self):
        """Test that get_change_col function exists and is callable."""
        assert get_change_col is not None
        assert callable(get_change_col)


class TestGetChangeColBasicFunctionality:
    """Test basic functionality of get_change_col."""

    def test_find_year_in_first_position(self):
        """Test finding year in column 1 (first data column)."""
        # Row 0 is the header row with years
        # Column 0 typically contains zone IDs, columns 1+ contain years
        changes_table = [
            ['Zone', 2000, 2005, 2010, 2015],
            [1, 1.0, 1.1, 1.2, 1.3],
            [2, 1.0, 1.05, 1.1, 1.15],
        ]

        result = get_change_col(changes_table, 2000, 'test.csv')
        assert result == 1

    def test_find_year_in_middle_position(self):
        """Test finding year in a middle column."""
        changes_table = [
            ['Zone', 2000, 2005, 2010, 2015],
            [1, 1.0, 1.1, 1.2, 1.3],
            [2, 1.0, 1.05, 1.1, 1.15],
        ]

        result = get_change_col(changes_table, 2005, 'test.csv')
        assert result == 2

    def test_find_year_in_last_position(self):
        """Test finding year in the last column."""
        changes_table = [
            ['Zone', 2000, 2005, 2010, 2015],
            [1, 1.0, 1.1, 1.2, 1.3],
            [2, 1.0, 1.05, 1.1, 1.15],
        ]

        result = get_change_col(changes_table, 2015, 'test.csv')
        assert result == 4

    def test_find_year_with_string_input(self):
        """Test finding year when input is a string."""
        changes_table = [
            ['Zone', 2000, 2005, 2010],
            [1, 1.0, 1.1, 1.2],
        ]

        # Function converts in_year to int
        result = get_change_col(changes_table, '2005', 'test.csv')
        assert result == 2


class TestGetChangeColReturnType:
    """Test the return type of get_change_col."""

    def test_returns_integer(self):
        """Test that get_change_col returns an integer."""
        changes_table = [
            ['Zone', 2000, 2005, 2010],
            [1, 1.0, 1.1, 1.2],
        ]

        result = get_change_col(changes_table, 2005, 'test.csv')
        assert isinstance(result, int)

    def test_returns_correct_column_index(self):
        """Test that returned index is 1-based (skips zone column)."""
        changes_table = [
            ['Zone', 1990, 1995, 2000, 2005, 2010],
            [1, 0.9, 0.95, 1.0, 1.05, 1.1],
        ]

        # Column index should match position in list (0-indexed)
        assert get_change_col(changes_table, 1990, 'test.csv') == 1
        assert get_change_col(changes_table, 1995, 'test.csv') == 2
        assert get_change_col(changes_table, 2000, 'test.csv') == 3
        assert get_change_col(changes_table, 2005, 'test.csv') == 4
        assert get_change_col(changes_table, 2010, 'test.csv') == 5


class TestGetChangeColYearNotFound:
    """Test behavior when year is not found in table."""

    def test_year_not_in_table_exits(self):
        """Test that function calls sys.exit when year not found."""
        changes_table = [
            ['Zone', 2000, 2005, 2010],
            [1, 1.0, 1.1, 1.2],
        ]

        # Year 1999 is not in the table
        with pytest.raises(ValueError):
            get_change_col(changes_table, 1999, 'test.csv')

    def test_year_after_range_exits(self):
        """Test that function raises when year is after all years in table."""
        changes_table = [
            ['Zone', 2000, 2005, 2010],
            [1, 1.0, 1.1, 1.2],
        ]

        with pytest.raises(ValueError):
            get_change_col(changes_table, 2020, 'test.csv')

    def test_year_before_range_exits(self):
        """Test that function raises when year is before all years in table."""
        changes_table = [
            ['Zone', 2000, 2005, 2010],
            [1, 1.0, 1.1, 1.2],
        ]

        with pytest.raises(ValueError):
            get_change_col(changes_table, 1990, 'test.csv')


class TestGetChangeColTableFormats:
    """Test get_change_col with various table formats."""

    def test_single_year_column(self):
        """Test table with only one year column."""
        changes_table = [
            ['Zone', 2000],
            [1, 1.0],
            [2, 1.1],
        ]

        result = get_change_col(changes_table, 2000, 'test.csv')
        assert result == 1

    def test_many_year_columns(self):
        """Test table with many year columns."""
        years = list(range(1990, 2021))  # 1990 to 2020
        changes_table = [
            ['Zone'] + years,
            [1] + [1.0 + i*0.01 for i in range(len(years))],
        ]

        result = get_change_col(changes_table, 2000, 'test.csv')
        assert result == 11  # 2000 is at index 11 (years start at index 1)

    def test_single_row_table(self):
        """Test table with only header row."""
        changes_table = [
            ['Zone', 2000, 2005, 2010],
        ]

        result = get_change_col(changes_table, 2005, 'test.csv')
        assert result == 2

    def test_multiple_zone_rows(self):
        """Test table with multiple zone rows."""
        changes_table = [
            ['Zone', 2000, 2005, 2010],
            [1, 1.0, 1.1, 1.2],
            [2, 0.9, 1.0, 1.1],
            [3, 1.1, 1.2, 1.3],
            [4, 0.8, 0.9, 1.0],
            [5, 1.2, 1.3, 1.4],
        ]

        result = get_change_col(changes_table, 2010, 'test.csv')
        assert result == 3


class TestGetChangeColEdgeCases:
    """Test edge cases for get_change_col."""

    def test_float_year_input(self):
        """Test with float year input (gets converted to int)."""
        changes_table = [
            ['Zone', 2000, 2005, 2010],
            [1, 1.0, 1.1, 1.2],
        ]

        # 2005.9 should be converted to 2005
        result = get_change_col(changes_table, 2005.9, 'test.csv')
        assert result == 2

    def test_negative_year(self):
        """Test with negative year (unlikely but valid)."""
        changes_table = [
            ['Zone', -100, 0, 100],
            [1, 1.0, 1.1, 1.2],
        ]

        result = get_change_col(changes_table, -100, 'test.csv')
        assert result == 1

    def test_year_zero(self):
        """Test with year zero."""
        changes_table = [
            ['Zone', -100, 0, 100],
            [1, 1.0, 1.1, 1.2],
        ]

        result = get_change_col(changes_table, 0, 'test.csv')
        assert result == 2

    def test_duplicate_years_returns_last(self):
        """Test table with duplicate years (returns last occurrence)."""
        changes_table = [
            ['Zone', 2000, 2000, 2005],  # 2000 appears twice
            [1, 1.0, 1.1, 1.2],
        ]

        # Function searches from left to right, overwrites, so returns last
        result = get_change_col(changes_table, 2000, 'test.csv')
        assert result == 2  # Last occurrence of 2000

    def test_numeric_string_in_table(self):
        """Test when table contains string years (comparison with int)."""
        # If table has string years, they won't match int comparison
        changes_table = [
            ['Zone', '2000', '2005', '2010'],  # String years
            [1, 1.0, 1.1, 1.2],
        ]

        # String '2000' != int 2000, so year not found
        with pytest.raises(ValueError):
            get_change_col(changes_table, 2000, 'test.csv')


class TestGetChangeColRealWorldScenarios:
    """Test get_change_col with realistic IWFM scenarios."""

    def test_water_year_scenario(self):
        """Test with typical water year range for California."""
        # Water years 1974-2015 (42 years like C2VSimCG)
        years = list(range(1974, 2016))
        changes_table = [
            ['Zone'] + years,
            [1] + [1.0] * len(years),
            [2] + [1.0] * len(years),
            [3] + [1.0] * len(years),
        ]

        # Find the first year
        result = get_change_col(changes_table, 1974, 'scenario_changes.csv')
        assert result == 1

        # Find a middle year
        result = get_change_col(changes_table, 2000, 'scenario_changes.csv')
        assert result == 27  # 2000 - 1974 + 1 = 27

        # Find the last year
        result = get_change_col(changes_table, 2015, 'scenario_changes.csv')
        assert result == 42

    def test_land_use_change_factors(self):
        """Test with realistic land use change factor table."""
        changes_table = [
            ['Zone', 2005, 2010, 2015, 2020],
            [1, 1.00, 1.05, 1.10, 1.15],   # Urban zone - increasing
            [2, 1.00, 0.98, 0.95, 0.90],   # Agricultural zone - decreasing
            [3, 1.00, 1.02, 1.05, 1.08],   # Native vegetation - slight increase
        ]

        result = get_change_col(changes_table, 2010, 'lu_changes.csv')
        assert result == 2

    def test_decadal_projections(self):
        """Test with decadal projection years."""
        changes_table = [
            ['Zone', 2020, 2030, 2040, 2050, 2060, 2070],
            [1, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0],
        ]

        result = get_change_col(changes_table, 2050, 'projections.csv')
        assert result == 4

    def test_historical_simulation_period(self):
        """Test with historical simulation period."""
        # Monthly simulation from 1973 to 2015
        # But change table might only have annual or decadal values
        changes_table = [
            ['Zone', 1975, 1980, 1985, 1990, 1995, 2000, 2005, 2010, 2015],
            [1, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        ]

        result = get_change_col(changes_table, 1995, 'historical_changes.csv')
        assert result == 5


class TestGetChangeColFilenameParameter:
    """Test that filename parameter is used for error messages."""

    def test_filename_in_error_output(self, capsys):
        """Test that filename appears in error output when year not found."""
        changes_table = [
            ['Zone', 2000, 2005, 2010],
            [1, 1.0, 1.1, 1.2],
        ]

        filename = 'my_custom_changes.csv'

        with pytest.raises(ValueError) as exc_info:
            get_change_col(changes_table, 1999, filename)

        assert filename in str(exc_info.value)
        assert '1999' in str(exc_info.value)


class TestGetChangeColConsecutiveYears:
    """Test get_change_col with consecutive year searches."""

    def test_consecutive_year_lookups(self):
        """Test looking up consecutive years."""
        changes_table = [
            ['Zone', 2000, 2001, 2002, 2003, 2004],
            [1, 1.0, 1.01, 1.02, 1.03, 1.04],
        ]

        for year in range(2000, 2005):
            result = get_change_col(changes_table, year, 'test.csv')
            assert result == year - 2000 + 1  # Column index


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
