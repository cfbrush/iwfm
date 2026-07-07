# test_hyd_diff.py
# Tests for hyd_diff function
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
Tests for iwfm.hyd_diff function.

The hyd_diff function subtracts values in one hydrograph file from another
and writes the result to an output file.

Example files used for testing:
- Hydrograph file 1: iwfm/tests/C2VSimCG-2021/Results/C2VSimCG_Hydrographs_GW.out
- Hydrograph file 2: iwfm/tests/C2VSimCG-2021/Results/C2VSimCG_Hydrographs_GW_mod.out

C2VSimCG hydrograph file characteristics (truncated test data):
- 22 total lines (file 1), 514 total lines (file 2)
- 9 header lines (lines 0-8)
- 13 data lines (lines 9-21) corresponding to timesteps in file 1
- Date format: MM/DD/YYYY_HH:MM
- Date range: 09/30/1973 to 09/30/1974

The function:
- Reads both hydrograph files
- Copies first 9 lines (header) from file 1
- Subtracts values: file_1[j] - file_2[j] for each data column
- Writes result to output file
"""

import pytest
import os
import sys
import inspect
import tempfile

# Add the iwfm directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from iwfm.hyd_diff import hyd_diff

# Path to example files
EXAMPLE_HYD_FILE_1 = os.path.join(
    os.path.dirname(__file__),
    'C2VSimCG-2021', 'Results', 'C2VSimCG_Hydrographs_GW.out'
)

EXAMPLE_HYD_FILE_2 = os.path.join(
    os.path.dirname(__file__),
    'C2VSimCG-2021', 'Results', 'C2VSimCG_Hydrographs_GW_mod.out'
)

# Check if example files exist
EXAMPLE_FILES_EXIST = (os.path.exists(EXAMPLE_HYD_FILE_1) and
                       os.path.exists(EXAMPLE_HYD_FILE_2))


class TestHydDiffFunctionExists:
    """Test that hyd_diff function exists and has correct signature."""

    def test_function_exists(self):
        """Test that hyd_diff function is importable."""
        assert hyd_diff is not None

    def test_function_is_callable(self):
        """Test that hyd_diff is callable."""
        assert callable(hyd_diff)

    def test_function_has_docstring(self):
        """Test that hyd_diff has a docstring."""
        assert hyd_diff.__doc__ is not None
        assert len(hyd_diff.__doc__) > 0

    def test_function_signature(self):
        """Test that hyd_diff has the expected parameters."""
        sig = inspect.signature(hyd_diff)
        params = list(sig.parameters.keys())

        assert 'gwhyd_file_1' in params
        assert 'gwhyd_file_2' in params
        assert 'outname' in params


@pytest.mark.skipif(not EXAMPLE_FILES_EXIST,
                    reason="Example hydrograph files not available")
class TestHydDiffOutputFile:
    """Test that hyd_diff creates output files."""

    def test_creates_output_file(self):
        """Test that hyd_diff creates an output file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            outname = os.path.join(temp_dir, 'diff_output.out')

            hyd_diff(EXAMPLE_HYD_FILE_1, EXAMPLE_HYD_FILE_2, outname)

            assert os.path.exists(outname)

    def test_output_file_not_empty(self):
        """Test that output file is not empty."""
        with tempfile.TemporaryDirectory() as temp_dir:
            outname = os.path.join(temp_dir, 'diff_output.out')

            hyd_diff(EXAMPLE_HYD_FILE_1, EXAMPLE_HYD_FILE_2, outname)

            assert os.path.getsize(outname) > 0


@pytest.mark.skipif(not EXAMPLE_FILES_EXIST,
                    reason="Example hydrograph files not available")
class TestHydDiffOutputContent:
    """Test the content of hyd_diff output files."""

    def test_output_has_same_line_count(self):
        """Test that output file has same number of lines as input."""
        with tempfile.TemporaryDirectory() as temp_dir:
            outname = os.path.join(temp_dir, 'diff_output.out')

            hyd_diff(EXAMPLE_HYD_FILE_1, EXAMPLE_HYD_FILE_2, outname)

            # Count lines in input
            with open(EXAMPLE_HYD_FILE_1) as f:
                input_lines = len(f.readlines())

            # Count lines in output
            with open(outname) as f:
                output_lines = len(f.readlines())

            assert output_lines == input_lines

    def test_output_preserves_header(self):
        """Test that output file preserves header lines from input."""
        with tempfile.TemporaryDirectory() as temp_dir:
            outname = os.path.join(temp_dir, 'diff_output.out')

            hyd_diff(EXAMPLE_HYD_FILE_1, EXAMPLE_HYD_FILE_2, outname)

            # Read headers from input
            with open(EXAMPLE_HYD_FILE_1) as f:
                input_header = [f.readline() for _ in range(9)]

            # Read headers from output
            with open(outname) as f:
                output_header = [f.readline() for _ in range(9)]

            # Headers should match
            for i in range(9):
                assert input_header[i].strip() == output_header[i].strip()

    def test_output_has_date_column(self):
        """Test that output file has date column in data lines."""
        with tempfile.TemporaryDirectory() as temp_dir:
            outname = os.path.join(temp_dir, 'diff_output.out')

            hyd_diff(EXAMPLE_HYD_FILE_1, EXAMPLE_HYD_FILE_2, outname)

            with open(outname) as f:
                lines = f.readlines()

            # Check first data line (line 10, index 9)
            first_data_line = lines[9].split()
            # First field should be a date
            assert '/' in first_data_line[0]  # Date format MM/DD/YYYY

    def test_output_dates_preserved(self):
        """Test that dates in output match dates in input."""
        with tempfile.TemporaryDirectory() as temp_dir:
            outname = os.path.join(temp_dir, 'diff_output.out')

            hyd_diff(EXAMPLE_HYD_FILE_1, EXAMPLE_HYD_FILE_2, outname)

            with open(EXAMPLE_HYD_FILE_1) as f:
                input_lines = f.readlines()

            with open(outname) as f:
                output_lines = f.readlines()

            # Check that dates match for data lines
            for i in range(9, min(20, len(input_lines))):
                input_date = input_lines[i].split()[0]
                output_date = output_lines[i].split()[0]
                assert input_date == output_date


@pytest.mark.skipif(not EXAMPLE_FILES_EXIST,
                    reason="Example hydrograph files not available")
class TestHydDiffCalculation:
    """Test the difference calculation in hyd_diff."""

    def test_identical_files_produce_zeros(self):
        """Test that subtracting identical files produces zeros."""
        with tempfile.TemporaryDirectory() as temp_dir:
            outname = os.path.join(temp_dir, 'diff_output.out')

            # Subtract file from itself
            hyd_diff(EXAMPLE_HYD_FILE_1, EXAMPLE_HYD_FILE_1, outname)

            with open(outname) as f:
                lines = f.readlines()

            # Check first few data lines
            for i in range(9, min(15, len(lines))):
                values = lines[i].split()[1:]  # Skip date column
                for val in values[:10]:  # Check first 10 values
                    assert float(val) == 0.0

    def test_difference_calculated_correctly(self):
        """Test that difference is calculated correctly (file1 - file2)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            outname = os.path.join(temp_dir, 'diff_output.out')

            hyd_diff(EXAMPLE_HYD_FILE_1, EXAMPLE_HYD_FILE_2, outname)

            # Read values from all three files
            with open(EXAMPLE_HYD_FILE_1) as f:
                lines1 = f.readlines()
            with open(EXAMPLE_HYD_FILE_2) as f:
                lines2 = f.readlines()
            with open(outname) as f:
                lines_out = f.readlines()

            # Check a data line
            data_line = 10  # Index 10 (line 11)
            vals1 = [float(x) for x in lines1[data_line].split()[1:6]]
            vals2 = [float(x) for x in lines2[data_line].split()[1:6]]
            vals_out = [float(x) for x in lines_out[data_line].split()[1:6]]

            # Output should be vals1 - vals2
            for j in range(len(vals1)):
                expected = round(vals1[j] - vals2[j], 4)
                assert abs(vals_out[j] - expected) < 0.0001


@pytest.mark.skipif(not EXAMPLE_FILES_EXIST,
                    reason="Example hydrograph files not available")
class TestHydDiffReturnValue:
    """Test the return value of hyd_diff."""

    def test_returns_none(self):
        """Test that hyd_diff returns None."""
        with tempfile.TemporaryDirectory() as temp_dir:
            outname = os.path.join(temp_dir, 'diff_output.out')

            result = hyd_diff(EXAMPLE_HYD_FILE_1, EXAMPLE_HYD_FILE_2, outname)

            assert result is None


@pytest.mark.skipif(not EXAMPLE_FILES_EXIST,
                    reason="Example hydrograph files not available")
class TestHydDiffOutputPath:
    """Test output path handling."""

    def test_output_to_different_directory(self):
        """Test that output file is created in specified directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a subdirectory
            sub_dir = os.path.join(temp_dir, 'subdir')
            os.makedirs(sub_dir)
            outname = os.path.join(sub_dir, 'diff_output.out')

            hyd_diff(EXAMPLE_HYD_FILE_1, EXAMPLE_HYD_FILE_2, outname)

            assert os.path.exists(outname)

    def test_output_with_spaces_in_path(self):
        """Test output to path with spaces."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create directory with space
            sub_dir = os.path.join(temp_dir, 'sub dir')
            os.makedirs(sub_dir)
            outname = os.path.join(sub_dir, 'diff output.out')

            hyd_diff(EXAMPLE_HYD_FILE_1, EXAMPLE_HYD_FILE_2, outname)

            assert os.path.exists(outname)


class TestHydDiffErrorHandling:
    """Test error handling in hyd_diff."""

    def test_nonexistent_file1_raises_error(self):
        """Test that nonexistent file 1 raises an error."""
        with tempfile.TemporaryDirectory() as temp_dir:
            outname = os.path.join(temp_dir, 'diff_output.out')

            with pytest.raises(FileNotFoundError):
                hyd_diff('/nonexistent/file1.out', EXAMPLE_HYD_FILE_2 if EXAMPLE_FILES_EXIST else '/nonexistent/file2.out', outname)

    def test_nonexistent_file2_raises_error(self):
        """Test that nonexistent file 2 raises an error."""
        if not EXAMPLE_FILES_EXIST:
            pytest.skip("Example files not available")

        with tempfile.TemporaryDirectory() as temp_dir:
            outname = os.path.join(temp_dir, 'diff_output.out')

            with pytest.raises(FileNotFoundError):
                hyd_diff(EXAMPLE_HYD_FILE_1, '/nonexistent/file2.out', outname)


@pytest.mark.skipif(not EXAMPLE_FILES_EXIST,
                    reason="Example hydrograph files not available")
class TestHydDiffC2VSimCGSpecific:
    """Test C2VSimCG-specific expectations."""

    def test_c2vsimcg_line_count(self):
        """Test that C2VSimCG hydrograph file has 22 lines (truncated test data)."""
        with open(EXAMPLE_HYD_FILE_1) as f:
            lines = f.readlines()

        assert len(lines) == 22

    def test_c2vsimcg_data_line_count(self):
        """Test that C2VSimCG has 13 data lines (truncated test data)."""
        with open(EXAMPLE_HYD_FILE_1) as f:
            lines = f.readlines()

        # Data lines start at line 10 (index 9)
        data_lines = lines[9:]
        assert len(data_lines) == 13

    def test_c2vsimcg_output_has_13_timesteps(self):
        """Test that output has 13 data lines (truncated test data)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            outname = os.path.join(temp_dir, 'diff_output.out')

            hyd_diff(EXAMPLE_HYD_FILE_1, EXAMPLE_HYD_FILE_2, outname)

            with open(outname) as f:
                lines = f.readlines()

            data_lines = lines[9:]
            assert len(data_lines) == 13

    def test_c2vsimcg_date_range(self):
        """Test that C2VSimCG date range is correct in output (truncated test data)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            outname = os.path.join(temp_dir, 'diff_output.out')

            hyd_diff(EXAMPLE_HYD_FILE_1, EXAMPLE_HYD_FILE_2, outname)

            with open(outname) as f:
                lines = f.readlines()

            # First data line should start with 09/30/1973
            first_date = lines[9].split()[0]
            assert first_date.startswith('09/30/1973')

            # Last data line should start with 09/30/1974 (truncated test data)
            last_date = lines[-1].split()[0]
            assert last_date.startswith('09/30/1974')


@pytest.mark.skipif(not EXAMPLE_FILES_EXIST,
                    reason="Example hydrograph files not available")
class TestHydDiffWithSyntheticData:
    """Test hyd_diff with synthetic data files."""

    def test_simple_difference(self):
        """Test difference with simple synthetic data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create two simple hydrograph files
            file1 = os.path.join(temp_dir, 'hyd1.out')
            file2 = os.path.join(temp_dir, 'hyd2.out')
            outname = os.path.join(temp_dir, 'diff.out')

            # Create synthetic data with 9 header lines
            header_lines = [
                '* Header line 1',
                '* Header line 2',
                '* Header line 3',
                '* Header line 4',
                '* Header line 5',
                '* Header line 6',
                '* Header line 7',
                '* Header line 8',
                '*        TIME',
            ]

            # File 1: values 100.0, 200.0, 300.0
            with open(file1, 'w') as f:
                for line in header_lines:
                    f.write(line + '\n')
                f.write('01/01/2000           100.0           200.0           300.0\n')
                f.write('02/01/2000           110.0           210.0           310.0\n')

            # File 2: values 50.0, 100.0, 150.0
            with open(file2, 'w') as f:
                for line in header_lines:
                    f.write(line + '\n')
                f.write('01/01/2000            50.0           100.0           150.0\n')
                f.write('02/01/2000            55.0           105.0           155.0\n')

            hyd_diff(file1, file2, outname)

            with open(outname) as f:
                lines = f.readlines()

            # Check first data line: 100-50=50, 200-100=100, 300-150=150
            data1 = lines[9].split()
            assert data1[0] == '01/01/2000'
            assert float(data1[1]) == 50.0
            assert float(data1[2]) == 100.0
            assert float(data1[3]) == 150.0

            # Check second data line: 110-55=55, 210-105=105, 310-155=155
            data2 = lines[10].split()
            assert data2[0] == '02/01/2000'
            assert float(data2[1]) == 55.0
            assert float(data2[2]) == 105.0
            assert float(data2[3]) == 155.0

    def test_negative_difference(self):
        """Test that negative differences are handled correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file1 = os.path.join(temp_dir, 'hyd1.out')
            file2 = os.path.join(temp_dir, 'hyd2.out')
            outname = os.path.join(temp_dir, 'diff.out')

            header_lines = [
                '* Header line 1',
                '* Header line 2',
                '* Header line 3',
                '* Header line 4',
                '* Header line 5',
                '* Header line 6',
                '* Header line 7',
                '* Header line 8',
                '*        TIME',
            ]

            # File 1: smaller values
            with open(file1, 'w') as f:
                for line in header_lines:
                    f.write(line + '\n')
                f.write('01/01/2000            50.0           100.0           150.0\n')

            # File 2: larger values
            with open(file2, 'w') as f:
                for line in header_lines:
                    f.write(line + '\n')
                f.write('01/01/2000           100.0           200.0           300.0\n')

            hyd_diff(file1, file2, outname)

            with open(outname) as f:
                lines = f.readlines()

            # Should get negative values: 50-100=-50, 100-200=-100, 150-300=-150
            data = lines[9].split()
            assert float(data[1]) == -50.0
            assert float(data[2]) == -100.0
            assert float(data[3]) == -150.0

    def test_decimal_precision(self):
        """Test that decimal precision is maintained."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file1 = os.path.join(temp_dir, 'hyd1.out')
            file2 = os.path.join(temp_dir, 'hyd2.out')
            outname = os.path.join(temp_dir, 'diff.out')

            header_lines = [
                '* Header line 1',
                '* Header line 2',
                '* Header line 3',
                '* Header line 4',
                '* Header line 5',
                '* Header line 6',
                '* Header line 7',
                '* Header line 8',
                '*        TIME',
            ]

            # File 1: values with decimals
            with open(file1, 'w') as f:
                for line in header_lines:
                    f.write(line + '\n')
                f.write('01/01/2000           100.1234       200.5678\n')

            # File 2: values with decimals
            with open(file2, 'w') as f:
                for line in header_lines:
                    f.write(line + '\n')
                f.write('01/01/2000            50.0001       100.0002\n')

            hyd_diff(file1, file2, outname)

            with open(outname) as f:
                lines = f.readlines()

            # Check that result has expected precision (rounded to 4 decimals)
            data = lines[9].split()
            assert abs(float(data[1]) - 50.1233) < 0.0001
            assert abs(float(data[2]) - 100.5676) < 0.0001
