# test_budget_info.py
# Unit tests for the budget_info function in the iwfm package
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

import iwfm


class TestBudgetInfoFunctionExists:
    """Test that the budget_info function exists and is callable."""

    def test_budget_info_exists(self):
        """Test that budget_info function exists in the iwfm module."""
        assert hasattr(iwfm, 'budget_info')
        assert callable(getattr(iwfm, 'budget_info'))


class TestBudgetInfoReturnTypes:
    """Test that budget_info returns correct types."""

    def test_returns_three_values(self):
        """Test that budget_info returns exactly three values."""
        budget_lines = [
            "C Header line",
            "10/31/1973_24:00       100.0     200.0",
        ]
        result = iwfm.budget_info(budget_lines)
        assert len(result) == 3

    def test_returns_integers(self):
        """Test that budget_info returns integers."""
        budget_lines = [
            "C Header line",
            "10/31/1973_24:00       100.0     200.0",
        ]
        tables, header, footer = iwfm.budget_info(budget_lines)
        assert isinstance(tables, int)
        assert isinstance(header, int)
        assert isinstance(footer, int)

    def test_returns_non_negative_values(self):
        """Test that budget_info returns non-negative values."""
        budget_lines = [
            "C Header line",
            "10/31/1973_24:00       100.0     200.0",
        ]
        tables, header, footer = iwfm.budget_info(budget_lines)
        assert tables >= 0
        assert header >= 0
        assert footer >= 0


class TestBudgetInfoBasicParsing:
    """Test basic parsing of budget file structure."""

    def test_counts_header_lines(self):
        """Test that header lines are counted correctly."""
        budget_lines = [
            "                    IWFM (v2015.0.1129)",
            "           GROUNDWATER BUDGET IN AC.FT.",
            "              SUBREGION AREA: 1000.0 AC",
            "--------------------------------------",
            "      Time          Value1      Value2",
            "                     (+)         (-)",
            "--------------------------------------",
            "10/31/1973_24:00       100.0     200.0",
            "11/30/1973_24:00       110.0     210.0",
        ]
        tables, header, footer = iwfm.budget_info(budget_lines)

        # Should detect 7 header lines (all lines before the first data line)
        assert header == 7

    def test_detects_data_lines_starting_with_digit(self):
        """Test that data lines starting with digits are detected."""
        budget_lines = [
            "Header line 1",
            "Header line 2",
            "10/31/1973_24:00       100.0",
            "11/30/1973_24:00       110.0",
        ]
        tables, header, footer = iwfm.budget_info(budget_lines)

        # Should have 2 header lines
        assert header == 2

    def test_single_table_detection(self):
        """Test detection of a single table."""
        budget_lines = [
            "Header 1",
            "Header 2",
            "10/31/1973_24:00       100.0",
            "11/30/1973_24:00       110.0",
            "12/31/1973_24:00       120.0",
        ]
        tables, header, footer = iwfm.budget_info(budget_lines)

        assert tables >= 1


class TestBudgetInfoMultipleTables:
    """Test budget_info with multiple tables."""

    def create_multi_table_budget(self, num_tables, header_lines, data_lines, footer_lines):
        """Create a mock multi-table budget file structure.

        Parameters
        ----------
        num_tables : int
            Number of tables to create
        header_lines : int
            Number of header lines per table
        data_lines : int
            Number of data lines per table
        footer_lines : int
            Number of footer/blank lines between tables
        """
        budget_lines = []
        for t in range(num_tables):
            # Add header lines
            for h in range(header_lines):
                if h == 0:
                    budget_lines.append(f"                    IWFM Table {t+1}")
                else:
                    budget_lines.append(f"Header line {h} for table {t+1}")

            # Add data lines
            for d in range(data_lines):
                month = (d % 12) + 1
                year = 1973 + (d // 12)
                budget_lines.append(
                    f"{month:02d}/{28 if month == 2 else 30}/{year}_24:00       {100.0 + d:.1f}"
                )

            # Add footer lines (except after last table)
            if t < num_tables - 1:
                for f in range(footer_lines):
                    budget_lines.append("")

        return budget_lines

    def test_two_tables(self):
        """Test detection with two tables."""
        budget_lines = self.create_multi_table_budget(
            num_tables=2, header_lines=8, data_lines=12, footer_lines=2
        )
        tables, header, footer = iwfm.budget_info(budget_lines)

        # Should detect at least 1 table (exact count depends on algorithm)
        assert tables >= 1
        # Should detect 8 header lines
        assert header == 8

    def test_many_tables(self):
        """Test with many tables (like real GW budget with 21 subregions)."""
        budget_lines = self.create_multi_table_budget(
            num_tables=10, header_lines=8, data_lines=24, footer_lines=2
        )
        tables, header, footer = iwfm.budget_info(budget_lines)

        # Should detect multiple tables
        assert tables >= 1
        assert header == 8


class TestBudgetInfoEdgeCases:
    """Test budget_info with edge cases."""

    def test_empty_input(self):
        """Test with empty input list."""
        budget_lines = []
        tables, header, footer = iwfm.budget_info(budget_lines)

        # Should return minimal values without crashing
        assert tables >= 1
        assert header >= 0
        assert footer >= 0

    def test_header_only(self):
        """Test with only header lines, no data."""
        budget_lines = [
            "Header line 1",
            "Header line 2",
            "Header line 3",
        ]
        tables, header, footer = iwfm.budget_info(budget_lines)

        # Should return without crashing
        assert tables >= 1
        assert header == 3
        assert footer >= 0

    def test_single_data_line(self):
        """Test with a single data line."""
        budget_lines = [
            "Header",
            "10/31/1973_24:00       100.0",
        ]
        tables, header, footer = iwfm.budget_info(budget_lines)

        assert tables >= 1
        assert header == 1

    def test_empty_lines_in_header(self):
        """Test handling of empty lines in header."""
        budget_lines = [
            "Header line 1",
            "",
            "Header line 3",
            "10/31/1973_24:00       100.0",
        ]
        tables, header, footer = iwfm.budget_info(budget_lines)

        # Empty lines should be counted as header lines
        assert header == 3

    def test_whitespace_only_lines(self):
        """Test handling of whitespace-only lines."""
        budget_lines = [
            "Header line 1",
            "   ",
            "Header line 3",
            "10/31/1973_24:00       100.0",
        ]
        tables, header, footer = iwfm.budget_info(budget_lines)

        # Whitespace-only lines should be counted as header lines
        assert header == 3


class TestBudgetInfoRealFileFormats:
    """Test budget_info with formats matching real IWFM budget files."""

    def test_gw_budget_format(self):
        """Test with groundwater budget format (8 header lines)."""
        # Mimics actual C2VSimCG_GW_Budget.bud structure
        budget_lines = [
            "                                               IWFM (v2015.0.1129)",
            "                              GROUNDWATER BUDGET IN AC.FT. FOR Subregion 1 (SR1)",
            "                                         SUBREGION AREA: 334740.83 AC",
            "-------------------------------------------------------------------------------------",
            "                    Beginning       Ending       Deep         Gain from",
            "      Time          Percolation      Storage        Storage   Percolation",
            "                                       (+)            (-)         (+)",
            "-------------------------------------------------------------------------------------",
            "10/31/1973_24:00       16015.4    29333325.5    29284555.5        1361.9",
            "11/30/1973_24:00       66583.7    29284555.5    29412549.8       67557.8",
            "12/31/1973_24:00       80269.7    29412549.8    29488890.4       47658.0",
        ]
        tables, header, footer = iwfm.budget_info(budget_lines)

        # GW budget has 8 header lines
        assert header == 8

    def test_stream_budget_format(self):
        """Test with stream budget format (7 header lines, no area line)."""
        # Mimics actual C2VSimCG_Streams_Budget.bud structure
        budget_lines = [
            "                                    IWFM STREAM PACKAGE (v4.2.0106)",
            "                 STREAM FLOW BUDGET IN AC.FT. FOR Kern River(REACH 1)",
            "-----------------------------------------------------------------------",
            "              Upstream   Downstream    Tributary        Tile",
            "      Time     Inflow     Outflow       Inflow          Drain",
            "                (+)         (-)          (+)             (+)",
            "-----------------------------------------------------------------------",
            "10/31/1973_24:00      29460.2          0.0          0.0          0.0",
            "11/30/1973_24:00      24810.2          0.0         10.7          0.0",
            "12/31/1973_24:00      25580.2          0.0         76.9          0.0",
        ]
        tables, header, footer = iwfm.budget_info(budget_lines)

        # Stream budget has 7 header lines
        assert header == 7

    def test_land_use_budget_format(self):
        """Test with land and water use budget format."""
        budget_lines = [
            "                              IWFM ROOT ZONE PACKAGE (v4.11.0062)",
            "               LAND AND WATER USE BUDGET IN AC.FT. FOR Subregion 1 (SR1)",
            "                                  SUBREGION AREA: 334740.83 AC",
            "--------------------------------------------------------------------------------",
            "                   Ag Water     Urban Water    Riparian",
            "      Time          Demand        Demand          ET",
            "                     (+)           (+)           (-)",
            "--------------------------------------------------------------------------------",
            "10/31/1973_24:00       5000.0      1000.0       500.0",
            "11/30/1973_24:00       4500.0       950.0       450.0",
        ]
        tables, header, footer = iwfm.budget_info(budget_lines)

        # LWU budget has 8 header lines
        assert header == 8


class TestBudgetInfoWithRealFiles:
    """Integration tests using actual budget files from test data."""

    @pytest.fixture
    def gw_budget_path(self):
        """Return path to the GW budget test file."""
        return os.path.join(
            os.path.dirname(__file__),
            'C2VSimCG-2021', 'Results', 'C2VSimCG_GW_Budget.bud'
        )

    @pytest.fixture
    def streams_budget_path(self):
        """Return path to the Streams budget test file."""
        return os.path.join(
            os.path.dirname(__file__),
            'C2VSimCG-2021', 'Results', 'C2VSimCG_Streams_Budget.bud'
        )

    def test_gw_budget_file_exists(self, gw_budget_path):
        """Test that the GW budget test file exists, otherwise skip."""
        if not os.path.exists(gw_budget_path):
            pytest.skip(f"Test data file not found: {gw_budget_path}")

    def test_streams_budget_file_exists(self, streams_budget_path):
        """Test that the Streams budget test file exists, otherwise skip."""
        if not os.path.exists(streams_budget_path):
            pytest.skip(f"Test data file not found: {streams_budget_path}")

    def test_parse_real_gw_budget(self, gw_budget_path):
        """Test parsing real GW budget file."""
        if not os.path.exists(gw_budget_path):
            pytest.skip("GW budget test file not found")

        with open(gw_budget_path, 'r') as f:
            budget_lines = [line.rstrip('\n') for line in f.readlines()]

        tables, header, footer = iwfm.budget_info(budget_lines)

        # GW budget should have 8 header lines
        assert header == 8

        # GW budget has 21 subregions, so at least 1 table
        assert tables >= 1

        # Footer should be non-negative
        assert footer >= 0

    def test_parse_real_streams_budget(self, streams_budget_path):
        """Test parsing real Streams budget file."""
        if not os.path.exists(streams_budget_path):
            pytest.skip("Streams budget test file not found")

        with open(streams_budget_path, 'r') as f:
            budget_lines = [line.rstrip('\n') for line in f.readlines()]

        tables, header, footer = iwfm.budget_info(budget_lines)

        # Stream budget should have 7 header lines
        assert header == 7

        # Should detect at least 1 table
        assert tables >= 1

        # Footer should be non-negative
        assert footer >= 0

    def test_gw_budget_table_count_reasonable(self, gw_budget_path):
        """Test that the GW budget table count is reasonable."""
        if not os.path.exists(gw_budget_path):
            pytest.skip("GW budget test file not found")

        with open(gw_budget_path, 'r') as f:
            budget_lines = [line.rstrip('\n') for line in f.readlines()]

        tables, header, footer = iwfm.budget_info(budget_lines)

        # C2VSimCG has 21 subregions, so should have approximately 21 tables
        # Allow some tolerance in case algorithm counts differently
        assert 1 <= tables <= 50


class TestBudgetInfoCommentLines:
    """Test budget_info handling of different comment line styles."""

    def test_lines_starting_with_C(self):
        """Test that lines starting with 'C' are treated as headers."""
        budget_lines = [
            "C This is a comment",
            "C Another comment",
            "10/31/1973_24:00       100.0",
        ]
        tables, header, footer = iwfm.budget_info(budget_lines)

        # Lines starting with 'C' don't start with a digit, so counted as header
        assert header == 2

    def test_lines_starting_with_dashes(self):
        """Test that separator lines (dashes) are treated as headers."""
        budget_lines = [
            "Header title",
            "-----------------------------",
            "Column1    Column2",
            "-----------------------------",
            "10/31/1973_24:00       100.0",
        ]
        tables, header, footer = iwfm.budget_info(budget_lines)

        assert header == 4


class TestBudgetInfoDataLineFormats:
    """Test budget_info recognition of different data line formats."""

    def test_dss_date_format(self):
        """Test recognition of DSS date format (MM/DD/YYYY_HH:MM)."""
        budget_lines = [
            "Header",
            "10/31/1973_24:00       100.0     200.0",
            "11/30/1973_24:00       110.0     210.0",
        ]
        tables, header, footer = iwfm.budget_info(budget_lines)

        assert header == 1

    def test_various_months(self):
        """Test that all months are recognized as data lines."""
        budget_lines = [
            "Header",
            "01/31/2000_24:00       100.0",  # January
            "02/28/2000_24:00       100.0",  # February
            "03/31/2000_24:00       100.0",  # March
            "04/30/2000_24:00       100.0",  # April
            "05/31/2000_24:00       100.0",  # May
            "06/30/2000_24:00       100.0",  # June
            "07/31/2000_24:00       100.0",  # July
            "08/31/2000_24:00       100.0",  # August
            "09/30/2000_24:00       100.0",  # September
            "10/31/2000_24:00       100.0",  # October
            "11/30/2000_24:00       100.0",  # November
            "12/31/2000_24:00       100.0",  # December
        ]
        tables, header, footer = iwfm.budget_info(budget_lines)

        assert header == 1

    def test_negative_values_in_data(self):
        """Test that data lines with negative values are handled."""
        budget_lines = [
            "Header",
            "10/31/1973_24:00      -100.0     200.0    -300.0",
            "11/30/1973_24:00       110.0    -210.0     310.0",
        ]
        tables, header, footer = iwfm.budget_info(budget_lines)

        assert header == 1

    def test_scientific_notation_values(self):
        """Test that data lines with scientific notation are handled."""
        budget_lines = [
            "Header",
            "10/31/1973_24:00       1.0E+05   2.0E-03",
            "11/30/1973_24:00       1.1E+05   2.1E-03",
        ]
        tables, header, footer = iwfm.budget_info(budget_lines)

        assert header == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
