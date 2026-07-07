# test_vic_2_table.py
# unit tests for vic_2_table function
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

import iwfm


def create_vic_factors_file(filepath, vic_ids, dates, values_col2, values_col3=None):
    """Helper to create a VIC factors CSV file for testing.

    The VIC factors file format:
    - Line 0: Header
    - Subsequent lines: VIC_ID, Date, factor_col2, factor_col3, ...
    - Each VIC_ID has one row per date
    - VIC IDs are grouped (all dates for VIC_ID 1, then all dates for VIC_ID 2, etc.)

    Parameters
    ----------
    filepath : path
        Path to write the file
    vic_ids : list of int
        List of VIC grid IDs
    dates : list of str
        List of dates
    values_col2 : dict
        Dictionary mapping (vic_id, date_index) to value for column 2
    values_col3 : dict, optional
        Dictionary mapping (vic_id, date_index) to value for column 3
    """
    lines = ["VIC_ID,Date,Factor1,Factor2"]  # Header

    for vic_id in vic_ids:
        for i, date in enumerate(dates):
            val2 = values_col2.get((vic_id, i), 1.0)
            val3 = values_col3.get((vic_id, i), 1.0) if values_col3 else 1.0
            lines.append(f"{vic_id},{date} 0:00:00,{val2},{val3}")

    filepath.write_text('\n'.join(lines))


class TestVic2TableBasic:
    """Basic tests for vic_2_table function."""

    def test_creates_output_file(self, tmp_path):
        """Test that output file is created."""
        input_file = tmp_path / "factors.csv"
        output_file = tmp_path / "output.csv"

        # Create simple input with 2 VIC IDs and 3 dates
        vic_ids = [1, 2]
        dates = ["1/1/2000", "2/1/2000", "3/1/2000"]
        values = {(1, 0): 1.1, (1, 1): 1.2, (1, 2): 1.3,
                  (2, 0): 2.1, (2, 1): 2.2, (2, 2): 2.3}
        create_vic_factors_file(input_file, vic_ids, dates, values)

        iwfm.vic_2_table(str(input_file), str(output_file), col=2)

        assert output_file.exists()

    def test_returns_none(self, tmp_path):
        """Test that function returns None."""
        input_file = tmp_path / "factors.csv"
        output_file = tmp_path / "output.csv"

        vic_ids = [1, 2]
        dates = ["1/1/2000", "2/1/2000"]
        values = {(1, 0): 1.0, (1, 1): 1.0, (2, 0): 1.0, (2, 1): 1.0}
        create_vic_factors_file(input_file, vic_ids, dates, values)

        result = iwfm.vic_2_table(str(input_file), str(output_file), col=2)

        assert result is None

    def test_output_has_header(self, tmp_path):
        """Test that output file has header row."""
        input_file = tmp_path / "factors.csv"
        output_file = tmp_path / "output.csv"

        vic_ids = [1, 2]
        dates = ["1/1/2000", "2/1/2000"]
        values = {(1, 0): 1.0, (1, 1): 1.0, (2, 0): 1.0, (2, 1): 1.0}
        create_vic_factors_file(input_file, vic_ids, dates, values)

        iwfm.vic_2_table(str(input_file), str(output_file), col=2)

        with open(output_file) as f:
            lines = f.readlines()

        assert lines[0].startswith("Date")

    def test_output_has_correct_row_count(self, tmp_path):
        """Test that output has correct number of data rows."""
        input_file = tmp_path / "factors.csv"
        output_file = tmp_path / "output.csv"

        vic_ids = [1, 2]
        dates = ["1/1/2000", "2/1/2000", "3/1/2000"]
        values = {}
        for vid in vic_ids:
            for i in range(len(dates)):
                values[(vid, i)] = 1.0
        create_vic_factors_file(input_file, vic_ids, dates, values)

        iwfm.vic_2_table(str(input_file), str(output_file), col=2)

        with open(output_file) as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]

        # Should have 1 header + 3 data rows
        assert len(lines) == 4


class TestVic2TableColumns:
    """Tests for column extraction."""

    def test_extracts_column_2(self, tmp_path):
        """Test extracting column 2 values."""
        input_file = tmp_path / "factors.csv"
        output_file = tmp_path / "output.csv"

        vic_ids = [1, 2]
        dates = ["1/1/2000"]
        values_col2 = {(1, 0): 1.5, (2, 0): 2.5}
        values_col3 = {(1, 0): 9.9, (2, 0): 8.8}
        create_vic_factors_file(input_file, vic_ids, dates, values_col2, values_col3)

        iwfm.vic_2_table(str(input_file), str(output_file), col=2)

        with open(output_file) as f:
            lines = f.readlines()

        # Check that column 2 values appear in output
        data_line = lines[1]
        assert "1.5" in data_line

    def test_extracts_column_3(self, tmp_path):
        """Test extracting column 3 values."""
        input_file = tmp_path / "factors.csv"
        output_file = tmp_path / "output.csv"

        vic_ids = [1, 2]
        dates = ["1/1/2000"]
        values_col2 = {(1, 0): 1.5, (2, 0): 2.5}
        values_col3 = {(1, 0): 9.9, (2, 0): 8.8}
        create_vic_factors_file(input_file, vic_ids, dates, values_col2, values_col3)

        iwfm.vic_2_table(str(input_file), str(output_file), col=3)

        with open(output_file) as f:
            lines = f.readlines()

        # Check that column 3 values appear in output
        data_line = lines[1]
        assert "9.9" in data_line


class TestVic2TableDates:
    """Tests for date handling."""

    def test_dates_in_output(self, tmp_path):
        """Test that dates appear in output rows."""
        input_file = tmp_path / "factors.csv"
        output_file = tmp_path / "output.csv"

        vic_ids = [1, 2]
        dates = ["1/1/2000", "2/1/2000", "3/1/2000"]
        values = {}
        for vid in vic_ids:
            for i in range(len(dates)):
                values[(vid, i)] = 1.0
        create_vic_factors_file(input_file, vic_ids, dates, values)

        iwfm.vic_2_table(str(input_file), str(output_file), col=2)

        with open(output_file) as f:
            content = f.read()

        # Check dates are in output (without the 0:00:00 part)
        assert "1/1/2000" in content
        assert "2/1/2000" in content
        assert "3/1/2000" in content

    def test_removes_time_component(self, tmp_path):
        """Test that 0:00:00 time component is removed from dates."""
        input_file = tmp_path / "factors.csv"
        output_file = tmp_path / "output.csv"

        vic_ids = [1, 2]
        dates = ["1/1/2000"]
        values = {(1, 0): 1.0, (2, 0): 1.0}
        create_vic_factors_file(input_file, vic_ids, dates, values)

        iwfm.vic_2_table(str(input_file), str(output_file), col=2)

        with open(output_file) as f:
            content = f.read()

        # Should not contain time component
        assert "0:00:00" not in content


class TestVic2TableVerbose:
    """Tests for verbose output."""

    def test_verbose_false_no_output(self, tmp_path, capsys):
        """Test that verbose=False produces no console output."""
        input_file = tmp_path / "factors.csv"
        output_file = tmp_path / "output.csv"

        vic_ids = [1, 2]
        dates = ["1/1/2000"]
        values = {(1, 0): 1.0, (2, 0): 1.0}
        create_vic_factors_file(input_file, vic_ids, dates, values)

        iwfm.vic_2_table(str(input_file), str(output_file), col=2, verbose=False)

        captured = capsys.readouterr()
        assert captured.out == ""

    def test_verbose_true_produces_output(self, tmp_path, capsys):
        """Test that verbose=True produces console output."""
        input_file = tmp_path / "factors.csv"
        output_file = tmp_path / "output.csv"

        vic_ids = [1, 2]
        dates = ["1/1/2000"]
        values = {(1, 0): 1.0, (2, 0): 1.0}
        create_vic_factors_file(input_file, vic_ids, dates, values)

        iwfm.vic_2_table(str(input_file), str(output_file), col=2, verbose=True)

        captured = capsys.readouterr()
        assert len(captured.out) > 0
        assert "Read" in captured.out


class TestVic2TableFileNotFound:
    """Tests for file not found handling."""

    def test_nonexistent_file_exits(self, tmp_path):
        """Test that nonexistent input file causes system exit."""
        nonexistent = tmp_path / "nonexistent.csv"
        output_file = tmp_path / "output.csv"

        with pytest.raises(FileNotFoundError):
            iwfm.vic_2_table(str(nonexistent), str(output_file), col=2)


class TestVic2TableMultipleVicIds:
    """Tests with multiple VIC grid IDs."""

    def test_three_vic_ids(self, tmp_path):
        """Test with three VIC grid IDs."""
        input_file = tmp_path / "factors.csv"
        output_file = tmp_path / "output.csv"

        vic_ids = [1, 2, 3]
        dates = ["1/1/2000", "2/1/2000"]
        values = {}
        for vid in vic_ids:
            for i in range(len(dates)):
                values[(vid, i)] = float(vid) + i * 0.1
        create_vic_factors_file(input_file, vic_ids, dates, values)

        iwfm.vic_2_table(str(input_file), str(output_file), col=2)

        assert output_file.exists()
        with open(output_file) as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]

        # Header + 2 data rows
        assert len(lines) == 3

    def test_output_csv_format(self, tmp_path):
        """Test that output is valid CSV format."""
        input_file = tmp_path / "factors.csv"
        output_file = tmp_path / "output.csv"

        vic_ids = [1, 2]
        dates = ["1/1/2000"]
        values = {(1, 0): 1.0, (2, 0): 2.0}
        create_vic_factors_file(input_file, vic_ids, dates, values)

        iwfm.vic_2_table(str(input_file), str(output_file), col=2)

        with open(output_file) as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]

        # Each line should be CSV (contain commas)
        for line in lines:
            assert "," in line


class TestVic2TableMultipleDates:
    """Tests with multiple dates/time steps."""

    def test_twelve_time_steps(self, tmp_path):
        """Test with 12 time steps (months)."""
        input_file = tmp_path / "factors.csv"
        output_file = tmp_path / "output.csv"

        vic_ids = [1, 2]
        dates = [f"{m}/1/2000" for m in range(1, 13)]
        values = {}
        for vid in vic_ids:
            for i in range(len(dates)):
                values[(vid, i)] = 1.0 + i * 0.01
        create_vic_factors_file(input_file, vic_ids, dates, values)

        iwfm.vic_2_table(str(input_file), str(output_file), col=2)

        with open(output_file) as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]

        # Header + 12 data rows
        assert len(lines) == 13
