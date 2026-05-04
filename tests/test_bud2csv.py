# test_bud2csv.py
# Unit tests for the bud2csv function in the iwfm package
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
import tempfile
import os
import io
from datetime import datetime

import pandas as pd

import iwfm


class TestBud2CsvFunctionExists:
    """Test that the bud2csv function exists and is callable."""

    def test_bud2csv_exists(self):
        """Test that bud2csv function exists in the iwfm module."""
        assert hasattr(iwfm, 'bud2csv')
        assert callable(getattr(iwfm, 'bud2csv'))


class TestBud2CsvGroundwaterBudget:
    """Test bud2csv with groundwater budget data."""

    def create_mock_gw_budget_data(self):
        """Create mock groundwater budget data for testing."""
        # Location names (subregions)
        loc_names = ['SR1', 'SR2', 'SR3']

        # Column headers matching a typical GW budget
        column_headers = [[
            'Time', 'Percolation', 'Beginning Storage', 'Ending Storage',
            'Deep Percolation', 'Gain from Stream', 'Recharge',
            'Gain from Lake', 'Boundary Inflow', 'Subsidence',
            'Tile Drain Outflow', 'Pumping', 'Outflow to Root Zone',
            'Net Subsurface Inflow', 'Discrepancy', 'Cumulative Subsidence'
        ]]

        # Create mock dataframes with budget values
        dates = [
            datetime(1973, 10, 31),
            datetime(1973, 11, 30),
            datetime(1973, 12, 31),
        ]

        loc_values = []
        for i, loc in enumerate(loc_names):
            data = {
                'Time': dates,
                'Percolation': [16015.4 + i*100, 66583.7 + i*100, 80269.7 + i*100],
                'Beginning Storage': [29333325.5, 29284555.5, 29412549.8],
                'Ending Storage': [29284555.5, 29412549.8, 29488890.4],
                'Deep Percolation': [1361.9, 67557.8, 47658.0],
                'Gain from Stream': [-76422.1, 52752.3, 24133.2],
                'Recharge': [36.5, 13.1, 13.6],
                'Gain from Lake': [0.0, 0.0, 0.0],
                'Boundary Inflow': [3291.7, 4300.8, 4102.4],
                'Subsidence': [25675.6, 5063.5, 2324.2],
                'Tile Drain Outflow': [0.0, 0.0, 0.0],
                'Pumping': [920.1, 583.2, 437.7],
                'Outflow to Root Zone': [0.0, 0.0, 0.0],
                'Net Subsurface Inflow': [-1793.5, -1110.1, -1452.9],
                'Discrepancy': [-0.0, -0.0, -0.0],
                'Cumulative Subsidence': [25675.6, 30739.0, 33063.2],
            }
            df = pd.DataFrame(data)
            loc_values.append(df)

        # Budget info tuple - format: [(index, 'BUDGET_TYPE description')]
        budget_info = [(0, 'GROUNDWATER BUDGET IN AC.FT. FOR Subregion 1 (SR1)')]

        return loc_names, column_headers, loc_values, budget_info

    def test_bud2csv_groundwater_no_header(self):
        """Test bud2csv writes groundwater budget data without header."""
        loc_names, column_headers, loc_values, budget_info = self.create_mock_gw_budget_data()

        # Write to a StringIO buffer
        output = io.StringIO()

        iwfm.bud2csv(output, loc_names, column_headers, loc_values,
                     budget_info, print_header=False)

        # Get the output and check it
        csv_content = output.getvalue()
        lines = csv_content.strip().split('\n')

        # Should have 9 lines (3 locations x 3 dates)
        assert len(lines) == 9

        # Check first line format (SR1, date, values...)
        first_line = lines[0]
        parts = first_line.split(',')
        assert parts[0] == 'SR1'
        assert parts[1] == '10/31/1973'  # Date format

        # Verify numeric values are present
        assert len(parts) > 2

    def test_bud2csv_groundwater_with_header(self):
        """Test bud2csv writes groundwater budget data with header."""
        loc_names, column_headers, loc_values, budget_info = self.create_mock_gw_budget_data()

        output = io.StringIO()

        iwfm.bud2csv(output, loc_names, column_headers, loc_values,
                     budget_info, print_header=True)

        csv_content = output.getvalue()
        lines = csv_content.strip().split('\n')

        # Should have 10 lines (1 header + 9 data)
        assert len(lines) == 10

        # Check header line starts with location type
        header_line = lines[0]
        assert header_line.startswith('Subregion,')

        # Header should contain column names
        assert 'Time' in header_line
        assert 'Percolation' in header_line

    def test_bud2csv_groundwater_data_values(self):
        """Test that bud2csv writes correct numeric values."""
        loc_names, column_headers, loc_values, budget_info = self.create_mock_gw_budget_data()

        output = io.StringIO()

        iwfm.bud2csv(output, loc_names, column_headers, loc_values,
                     budget_info, print_header=False)

        csv_content = output.getvalue()
        lines = csv_content.strip().split('\n')

        # Parse first line and verify values
        first_line = lines[0]
        parts = first_line.split(',')

        # Third value should be percolation (16015.4 for SR1)
        percolation = float(parts[2])
        assert abs(percolation - 16015.4) < 0.1


class TestBud2CsvStreamBudget:
    """Test bud2csv with stream budget data."""

    def create_mock_stream_budget_data(self, budget_info_string):
        """Create mock stream budget data with specified budget_info string.

        Parameters
        ----------
        budget_info_string : str
            The budget info string that determines the budget type.
            Examples from actual IWFM files:
            - 'STREAM FLOW BUDGET IN AC.FT. FOR NODE 1' -> StreamNode
            - 'STREAM FLOW BUDGET IN AC.FT. FOR Kern River(REACH 1)' -> StreamReach
        """
        loc_names = ['Reach1', 'Reach2']

        column_headers = [[
            'Time', 'Upstream Inflow', 'Downstream Outflow',
            'Gain from GW', 'Return Flow', 'Diversion'
        ]]

        dates = [
            datetime(1973, 10, 31),
            datetime(1973, 11, 30),
        ]

        loc_values = []
        for i, loc in enumerate(loc_names):
            data = {
                'Time': dates,
                'Upstream Inflow': [1000.0 + i*100, 1200.0 + i*100],
                'Downstream Outflow': [900.0 + i*100, 1100.0 + i*100],
                'Gain from GW': [50.0, 60.0],
                'Return Flow': [10.0, 15.0],
                'Diversion': [160.0, 175.0],
            }
            df = pd.DataFrame(data)
            loc_values.append(df)

        budget_info = [(0, budget_info_string)]

        return loc_names, column_headers, loc_values, budget_info

    def test_bud2csv_stream_reach_budget(self):
        """Test bud2csv with stream reach budget.

        Uses actual format from C2VSimCG_Streams_Budget.bud:
        'STREAM FLOW BUDGET IN AC.FT. FOR Kern River(REACH 1)'
        """
        # Actual format from test data files
        budget_string = 'STREAM FLOW BUDGET IN AC.FT. FOR Kern River(REACH 1)'
        loc_names, column_headers, loc_values, budget_info = self.create_mock_stream_budget_data(
            budget_string
        )

        output = io.StringIO()

        iwfm.bud2csv(output, loc_names, column_headers, loc_values,
                     budget_info, print_header=True)

        csv_content = output.getvalue()
        lines = csv_content.strip().split('\n')

        # Header should use StreamReach as location type
        header_line = lines[0]
        assert header_line.startswith('StreamReach,')

    def test_bud2csv_stream_node_budget(self):
        """Test bud2csv with stream node budget.

        Uses actual format from C2VSimCG_Stream_Node_Budget.bud:
        'STREAM FLOW BUDGET IN AC.FT. FOR NODE 1'
        The function detects NODE at split()[-2] position.
        """
        # Actual format from test data files
        budget_string = 'STREAM FLOW BUDGET IN AC.FT. FOR NODE 1'
        loc_names, column_headers, loc_values, budget_info = self.create_mock_stream_budget_data(
            budget_string
        )

        output = io.StringIO()

        iwfm.bud2csv(output, loc_names, column_headers, loc_values,
                     budget_info, print_header=True)

        csv_content = output.getvalue()
        lines = csv_content.strip().split('\n')

        # Header should use StreamNode as location type
        header_line = lines[0]
        assert header_line.startswith('StreamNode,')


class TestBud2CsvLandUseBudget:
    """Test bud2csv with land use and root zone budget data."""

    def create_mock_lu_budget_data(self, crop_budget=False):
        """Create mock land use budget data."""
        if crop_budget:
            # Crop budget - location names include crop identifier
            loc_names = ['1_Corn', '1_Wheat', '2_Corn', '2_Wheat']
        else:
            # Subregion budget
            loc_names = ['SR1 (Subregion 1)', 'SR2 (Subregion 2)']

        column_headers = [[
            'Time', 'Potential CU', 'Ag Supply', 'Pumping',
            'Deliveries', 'Inflow as SR', 'Reused Water'
        ]]

        dates = [
            datetime(1973, 10, 31),
            datetime(1973, 11, 30),
        ]

        loc_values = []
        for i, loc in enumerate(loc_names):
            data = {
                'Time': dates,
                'Potential CU': [500.0 + i*50, 600.0 + i*50],
                'Ag Supply': [450.0 + i*50, 550.0 + i*50],
                'Pumping': [100.0 + i*20, 120.0 + i*20],
                'Deliveries': [350.0 + i*30, 430.0 + i*30],
                'Inflow as SR': [10.0, 15.0],
                'Reused Water': [5.0, 8.0],
            }
            df = pd.DataFrame(data)
            loc_values.append(df)

        # Budget info for land use budget
        if crop_budget:
            budget_info = [(0, 'LAND AND WATER USE BUDGET IN AC.FT. Corn')]
        else:
            budget_info = [(0, 'LAND AND WATER USE BUDGET IN AC.FT. FOR Subregion 1 (SR1)')]

        return loc_names, column_headers, loc_values, budget_info

    def test_bud2csv_land_use_subregion(self):
        """Test bud2csv with land use budget for subregions."""
        loc_names, column_headers, loc_values, budget_info = self.create_mock_lu_budget_data(
            crop_budget=False
        )

        output = io.StringIO()

        iwfm.bud2csv(output, loc_names, column_headers, loc_values,
                     budget_info, print_header=True)

        csv_content = output.getvalue()
        lines = csv_content.strip().split('\n')

        # Header should use Subregion as location type
        header_line = lines[0]
        assert header_line.startswith('Subregion,')

    def test_bud2csv_land_use_crop_budget(self):
        """Test bud2csv with land use crop budget."""
        loc_names, column_headers, loc_values, budget_info = self.create_mock_lu_budget_data(
            crop_budget=True
        )

        output = io.StringIO()

        iwfm.bud2csv(output, loc_names, column_headers, loc_values,
                     budget_info, print_header=True)

        csv_content = output.getvalue()
        lines = csv_content.strip().split('\n')

        # Header should use Subregion,Crop as location type
        header_line = lines[0]
        assert header_line.startswith('Subregion,Crop,')

        # Data lines should have subregion ID and crop name separately
        data_line = lines[1]
        parts = data_line.split(',')
        # First part should be subregion ID (1)
        assert parts[0] == '1'
        # Second part should be crop name (Corn)
        assert parts[1] == 'Corn'


class TestBud2CsvRootZoneBudget:
    """Test bud2csv with root zone budget data."""

    def create_mock_rz_budget_data(self):
        """Create mock root zone budget data."""
        loc_names = ['SR1', 'SR2']

        column_headers = [[
            'Time', 'Precipitation', 'Irrigation', 'Actual ET',
            'Percolation', 'Root Zone Storage Change'
        ]]

        dates = [
            datetime(1973, 10, 31),
            datetime(1973, 11, 30),
        ]

        loc_values = []
        for i, loc in enumerate(loc_names):
            data = {
                'Time': dates,
                'Precipitation': [2.5 + i*0.5, 3.0 + i*0.5],
                'Irrigation': [10.0 + i*2, 12.0 + i*2],
                'Actual ET': [8.0 + i*1, 9.5 + i*1],
                'Percolation': [3.5 + i*0.5, 4.0 + i*0.5],
                'Root Zone Storage Change': [1.0, 1.5],
            }
            df = pd.DataFrame(data)
            loc_values.append(df)

        # Budget info for root zone budget - subregion
        budget_info = [(0, 'ROOT ZONE BUDGET IN AC.FT. FOR Subregion 1 (SR1)')]

        return loc_names, column_headers, loc_values, budget_info

    def test_bud2csv_root_zone_budget(self):
        """Test bud2csv with root zone budget."""
        loc_names, column_headers, loc_values, budget_info = self.create_mock_rz_budget_data()

        output = io.StringIO()

        iwfm.bud2csv(output, loc_names, column_headers, loc_values,
                     budget_info, print_header=True)

        csv_content = output.getvalue()
        lines = csv_content.strip().split('\n')

        # Should have data lines
        assert len(lines) > 0

        # Header should be present
        header_line = lines[0]
        assert 'Time' in header_line


class TestBud2CsvSmallWatershedBudget:
    """Test bud2csv with small watershed budget data."""

    def create_mock_sw_budget_data(self):
        """Create mock small watershed budget data."""
        loc_names = ['SW1', 'SW2']

        column_headers = [[
            'Time', 'Precipitation', 'Runoff', 'Baseflow', 'Total Flow'
        ]]

        dates = [
            datetime(1973, 10, 31),
            datetime(1973, 11, 30),
        ]

        loc_values = []
        for i, loc in enumerate(loc_names):
            data = {
                'Time': dates,
                'Precipitation': [5.0 + i*1, 6.0 + i*1],
                'Runoff': [2.0 + i*0.5, 2.5 + i*0.5],
                'Baseflow': [1.0 + i*0.2, 1.2 + i*0.2],
                'Total Flow': [3.0 + i*0.7, 3.7 + i*0.7],
            }
            df = pd.DataFrame(data)
            loc_values.append(df)

        # Budget info for small watershed budget
        budget_info = [(0, 'SMALL WATERSHED BUDGET IN AC.FT.')]

        return loc_names, column_headers, loc_values, budget_info

    def test_bud2csv_small_watershed_budget(self):
        """Test bud2csv with small watershed budget."""
        loc_names, column_headers, loc_values, budget_info = self.create_mock_sw_budget_data()

        output = io.StringIO()

        iwfm.bud2csv(output, loc_names, column_headers, loc_values,
                     budget_info, print_header=True)

        csv_content = output.getvalue()
        lines = csv_content.strip().split('\n')

        # Header should use SmallWatershed as location type
        header_line = lines[0]
        assert header_line.startswith('SmallWatershed,')


class TestBud2CsvUnsaturatedZoneBudget:
    """Test bud2csv with unsaturated zone budget data."""

    def create_mock_unsat_budget_data(self):
        """Create mock unsaturated zone budget data."""
        loc_names = ['SR1', 'SR2']

        column_headers = [[
            'Time', 'Percolation from RZ', 'Deep Percolation to GW',
            'Storage Change'
        ]]

        dates = [
            datetime(1973, 10, 31),
            datetime(1973, 11, 30),
        ]

        loc_values = []
        for i, loc in enumerate(loc_names):
            data = {
                'Time': dates,
                'Percolation from RZ': [100.0 + i*10, 120.0 + i*10],
                'Deep Percolation to GW': [80.0 + i*8, 95.0 + i*8],
                'Storage Change': [20.0 + i*2, 25.0 + i*2],
            }
            df = pd.DataFrame(data)
            loc_values.append(df)

        # Budget info - UNSAT type uses default Subregion location
        budget_info = [(0, 'UNSATURATED ZONE BUDGET IN AC.FT.')]

        return loc_names, column_headers, loc_values, budget_info

    def test_bud2csv_unsat_budget(self):
        """Test bud2csv with unsaturated zone budget."""
        loc_names, column_headers, loc_values, budget_info = self.create_mock_unsat_budget_data()

        output = io.StringIO()

        iwfm.bud2csv(output, loc_names, column_headers, loc_values,
                     budget_info, print_header=True)

        csv_content = output.getvalue()
        lines = csv_content.strip().split('\n')

        # Should have header + data lines
        assert len(lines) == 5  # 1 header + 4 data (2 locations x 2 dates)


class TestBud2CsvEdgeCases:
    """Test bud2csv with edge cases and error conditions."""

    def test_bud2csv_empty_locations(self):
        """Test bud2csv with empty location list."""
        loc_names = []
        column_headers = [['Time', 'Value']]
        loc_values = []
        budget_info = [(0, 'GROUNDWATER BUDGET')]

        output = io.StringIO()

        # Should not raise an error
        iwfm.bud2csv(output, loc_names, column_headers, loc_values,
                     budget_info, print_header=True)

        csv_content = output.getvalue()
        lines = csv_content.strip().split('\n')

        # Should only have header line
        assert len(lines) == 1

    def test_bud2csv_single_date(self):
        """Test bud2csv with only one date."""
        loc_names = ['SR1']
        column_headers = [['Time', 'Value']]

        dates = [datetime(1973, 10, 31)]
        data = {'Time': dates, 'Value': [100.0]}
        loc_values = [pd.DataFrame(data)]

        budget_info = [(0, 'GROUNDWATER BUDGET')]

        output = io.StringIO()

        iwfm.bud2csv(output, loc_names, column_headers, loc_values,
                     budget_info, print_header=False)

        csv_content = output.getvalue()
        lines = csv_content.strip().split('\n')

        # Should have 1 data line
        assert len(lines) == 1

    def test_bud2csv_to_file(self):
        """Test bud2csv writing to an actual file."""
        loc_names = ['SR1', 'SR2']
        column_headers = [['Time', 'Percolation', 'Storage']]

        dates = [datetime(1973, 10, 31), datetime(1973, 11, 30)]

        loc_values = []
        for i in range(2):
            data = {
                'Time': dates,
                'Percolation': [100.0 + i*10, 120.0 + i*10],
                'Storage': [1000.0 + i*100, 1050.0 + i*100],
            }
            loc_values.append(pd.DataFrame(data))

        budget_info = [(0, 'GROUNDWATER BUDGET')]

        # Write to temp file
        fd, temp_file = tempfile.mkstemp(suffix='.csv', text=True)
        try:
            with os.fdopen(fd, 'w') as f:
                iwfm.bud2csv(f, loc_names, column_headers, loc_values,
                             budget_info, print_header=True)

            # Read back and verify
            with open(temp_file, 'r') as f:
                content = f.read()

            lines = content.strip().split('\n')
            assert len(lines) == 5  # 1 header + 4 data lines

            # Verify CSV can be parsed
            df = pd.read_csv(temp_file)
            assert len(df) == 4

        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_bud2csv_negative_values(self):
        """Test bud2csv handles negative values correctly."""
        loc_names = ['SR1']
        column_headers = [['Time', 'Gain', 'Loss']]

        dates = [datetime(1973, 10, 31)]
        data = {
            'Time': dates,
            'Gain': [100.5],
            'Loss': [-50.25],  # Negative value
        }
        loc_values = [pd.DataFrame(data)]

        budget_info = [(0, 'GROUNDWATER BUDGET')]

        output = io.StringIO()

        iwfm.bud2csv(output, loc_names, column_headers, loc_values,
                     budget_info, print_header=False)

        csv_content = output.getvalue()

        # Should contain the negative value
        assert '-50.25' in csv_content


class TestBud2CsvDateFormatting:
    """Test that bud2csv formats dates correctly."""

    def test_bud2csv_date_format(self):
        """Test that dates are formatted as MM/DD/YYYY."""
        loc_names = ['SR1']
        column_headers = [['Time', 'Value']]

        # Test various dates
        test_dates = [
            datetime(1973, 1, 5),    # Single digit month and day
            datetime(1973, 10, 31),  # Double digit month and day
            datetime(2000, 12, 25),  # Year 2000+
        ]

        data = {
            'Time': test_dates,
            'Value': [100.0, 200.0, 300.0],
        }
        loc_values = [pd.DataFrame(data)]

        budget_info = [(0, 'GROUNDWATER BUDGET')]

        output = io.StringIO()

        iwfm.bud2csv(output, loc_names, column_headers, loc_values,
                     budget_info, print_header=False)

        csv_content = output.getvalue()
        lines = csv_content.strip().split('\n')

        # Check date formats
        assert '01/05/1973' in lines[0]
        assert '10/31/1973' in lines[1]
        assert '12/25/2000' in lines[2]


class TestBud2CsvWithRealBudgetFile:
    """Integration tests using actual budget file from test data."""

    @pytest.fixture
    def budget_file_path(self):
        """Return path to the test budget file."""
        return os.path.join(
            os.path.dirname(__file__),
            'C2VSimCG-2021', 'Results', 'C2VSimCG_GW_Budget.bud'
        )

    def test_budget_file_exists(self, budget_file_path):
        """Test that the sample budget file exists, otherwise skip."""
        if not os.path.exists(budget_file_path):
            pytest.skip(f"Test data file not found: {budget_file_path}")

    def test_parse_real_budget_header(self, budget_file_path):
        """Test parsing header from real budget file."""
        if not os.path.exists(budget_file_path):
            pytest.skip("Test data file not found")

        with open(budget_file_path, 'r') as f:
            lines = f.readlines()

        # Should have content
        assert len(lines) > 0

        # Use budget_info to parse the file structure
        budget_lines = [line.rstrip('\n') for line in lines]
        tables, header, footer = iwfm.budget_info(budget_lines)

        # Verify reasonable values
        assert tables >= 1
        assert header >= 1  # Should have some header lines

    def test_parse_budget_file_structure(self, budget_file_path):
        """Test that we can parse the budget file structure."""
        if not os.path.exists(budget_file_path):
            pytest.skip("Test data file not found")

        with open(budget_file_path, 'r') as f:
            first_lines = [f.readline().rstrip() for _ in range(10)]

        # Check that file contains expected structure
        # First line should contain IWFM version
        assert 'IWFM' in first_lines[0]

        # Second line should contain budget type
        assert 'GROUNDWATER BUDGET' in first_lines[1]

        # Third line should contain area info
        assert 'SUBREGION AREA' in first_lines[2]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
