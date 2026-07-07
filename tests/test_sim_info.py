# test_sim_info.py
# unit tests for sim_info function
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


def create_sim_file(filepath, start_date, time_step, end_date, restart=0):
    """Helper to create a minimal IWFM simulation main input file for testing.

    Parameters
    ----------
    filepath : path
        Path to write the file
    start_date : str
        Simulation start date in DSS format (MM/DD/YYYY_HH:MM)
    time_step : str
        Time step (e.g., '1MON', '1DAY', '1HOUR')
    end_date : str
        Simulation end date in DSS format
    restart : int
        Restart option (0 or 1)
    """
    lines = []

    # Add comment header
    lines.append("C This is a test simulation file")
    lines.append("C Created for testing sim_info")

    # Add 14 non-comment lines (file names and parameters)
    # Lines 1-14 represent various input file specifications
    for i in range(14):
        lines.append(f" file_{i+1}.dat                    / {i+1}: INPUT FILE {i+1}")

    # Add comment before simulation dates
    lines.append("C Simulation Period Section")

    # Start date (BDT) - line after 14 non-comment lines
    lines.append(f"      {start_date}          / BDT")

    # RESTART option
    lines.append(f"      {restart}                         / RESTART")

    # Comment before time step
    lines.append("C Time step and end date")

    # Time step (UNITT)
    lines.append(f"        {time_step}                    / UNITT")

    # End date (EDT)
    lines.append(f"        {end_date}        / EDT")

    filepath.write_text('\n'.join(lines))


class TestSimInfo:
    """Tests for the sim_info function."""

    def test_basic_simulation_dates(self, tmp_path):
        """Test reading basic simulation dates."""
        sim_file = tmp_path / "simulation.in"
        create_sim_file(
            sim_file,
            start_date="09/30/1973_24:00",
            time_step="1MON",
            end_date="09/30/1974_24:00"
        )

        start, end, step = iwfm.sim_info(str(sim_file))

        assert start == "09/30/1973_24:00"
        assert end == "09/30/1974_24:00"
        assert step == "1MON"

    def test_returns_three_values(self, tmp_path):
        """Test that function returns three values."""
        sim_file = tmp_path / "simulation.in"
        create_sim_file(
            sim_file,
            start_date="01/01/2000_24:00",
            time_step="1DAY",
            end_date="12/31/2000_24:00"
        )

        result = iwfm.sim_info(str(sim_file))

        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_returns_strings(self, tmp_path):
        """Test that all returned values are strings."""
        sim_file = tmp_path / "simulation.in"
        create_sim_file(
            sim_file,
            start_date="01/01/2000_24:00",
            time_step="1MON",
            end_date="12/31/2000_24:00"
        )

        start, end, step = iwfm.sim_info(str(sim_file))

        assert isinstance(start, str)
        assert isinstance(end, str)
        assert isinstance(step, str)

    def test_daily_time_step(self, tmp_path):
        """Test with daily time step."""
        sim_file = tmp_path / "simulation.in"
        create_sim_file(
            sim_file,
            start_date="01/01/2000_24:00",
            time_step="1DAY",
            end_date="01/31/2000_24:00"
        )

        start, end, step = iwfm.sim_info(str(sim_file))

        assert step == "1DAY"

    def test_hourly_time_step(self, tmp_path):
        """Test with hourly time step."""
        sim_file = tmp_path / "simulation.in"
        create_sim_file(
            sim_file,
            start_date="01/01/2000_24:00",
            time_step="1HOUR",
            end_date="01/02/2000_24:00"
        )

        start, end, step = iwfm.sim_info(str(sim_file))

        assert step == "1HOUR"

    def test_weekly_time_step(self, tmp_path):
        """Test with weekly time step."""
        sim_file = tmp_path / "simulation.in"
        create_sim_file(
            sim_file,
            start_date="01/01/2000_24:00",
            time_step="1WEEK",
            end_date="02/01/2000_24:00"
        )

        start, end, step = iwfm.sim_info(str(sim_file))

        assert step == "1WEEK"

    def test_yearly_time_step(self, tmp_path):
        """Test with yearly time step."""
        sim_file = tmp_path / "simulation.in"
        create_sim_file(
            sim_file,
            start_date="01/01/2000_24:00",
            time_step="1YEAR",
            end_date="01/01/2010_24:00"
        )

        start, end, step = iwfm.sim_info(str(sim_file))

        assert step == "1YEAR"

    def test_minute_time_steps(self, tmp_path):
        """Test with various minute time steps."""
        for mins in ["1MIN", "5MIN", "15MIN", "30MIN"]:
            sim_file = tmp_path / f"simulation_{mins}.in"
            create_sim_file(
                sim_file,
                start_date="01/01/2000_24:00",
                time_step=mins,
                end_date="01/01/2000_24:00"
            )

            _, _, step = iwfm.sim_info(str(sim_file))

            assert step == mins

    def test_multi_hour_time_steps(self, tmp_path):
        """Test with multi-hour time steps."""
        for hours in ["2HOUR", "6HOUR", "12HOUR"]:
            sim_file = tmp_path / f"simulation_{hours}.in"
            create_sim_file(
                sim_file,
                start_date="01/01/2000_24:00",
                time_step=hours,
                end_date="01/02/2000_24:00"
            )

            _, _, step = iwfm.sim_info(str(sim_file))

            assert step == hours

    def test_different_date_formats(self, tmp_path):
        """Test with different valid date formats."""
        sim_file = tmp_path / "simulation.in"
        create_sim_file(
            sim_file,
            start_date="12/31/1999_24:00",
            time_step="1MON",
            end_date="01/31/2000_24:00"
        )

        start, end, step = iwfm.sim_info(str(sim_file))

        assert start == "12/31/1999_24:00"
        assert end == "01/31/2000_24:00"

    def test_leap_year_dates(self, tmp_path):
        """Test with leap year dates."""
        sim_file = tmp_path / "simulation.in"
        create_sim_file(
            sim_file,
            start_date="02/28/2000_24:00",
            time_step="1DAY",
            end_date="02/29/2000_24:00"
        )

        start, end, step = iwfm.sim_info(str(sim_file))

        assert start == "02/28/2000_24:00"
        assert end == "02/29/2000_24:00"

    def test_long_simulation_period(self, tmp_path):
        """Test with long simulation period."""
        sim_file = tmp_path / "simulation.in"
        create_sim_file(
            sim_file,
            start_date="01/01/1950_24:00",
            time_step="1MON",
            end_date="12/31/2020_24:00"
        )

        start, end, step = iwfm.sim_info(str(sim_file))

        assert start == "01/01/1950_24:00"
        assert end == "12/31/2020_24:00"

    def test_file_not_found_exits(self, tmp_path):
        """Test that nonexistent file causes system exit."""
        nonexistent = tmp_path / "nonexistent.in"

        with pytest.raises(FileNotFoundError):
            iwfm.sim_info(str(nonexistent))

    def test_verbose_output(self, tmp_path, capsys):
        """Test verbose output shows messages."""
        sim_file = tmp_path / "simulation.in"
        create_sim_file(
            sim_file,
            start_date="09/30/1973_24:00",
            time_step="1MON",
            end_date="09/30/1974_24:00"
        )

        iwfm.sim_info(str(sim_file), verbose=True)

        captured = capsys.readouterr()
        assert "sim_info" in captured.out

    def test_no_verbose_output(self, tmp_path, capsys):
        """Test that verbose=False produces no output."""
        sim_file = tmp_path / "simulation.in"
        create_sim_file(
            sim_file,
            start_date="09/30/1973_24:00",
            time_step="1MON",
            end_date="09/30/1974_24:00"
        )

        iwfm.sim_info(str(sim_file), verbose=False)

        captured = capsys.readouterr()
        assert captured.out == ""

    def test_with_restart_option(self, tmp_path):
        """Test file with restart option enabled."""
        sim_file = tmp_path / "simulation.in"
        create_sim_file(
            sim_file,
            start_date="09/30/1973_24:00",
            time_step="1MON",
            end_date="09/30/1974_24:00",
            restart=1
        )

        start, end, step = iwfm.sim_info(str(sim_file))

        # Function should still work regardless of restart value
        assert start == "09/30/1973_24:00"
        assert end == "09/30/1974_24:00"


class TestSimInfoComments:
    """Tests for handling of comment lines."""

    def test_multiple_comment_styles(self, tmp_path):
        """Test file with multiple comment styles."""
        sim_file = tmp_path / "simulation.in"
        lines = []

        # Multiple comment styles
        lines.append("C Comment with C")
        lines.append("c Comment with lowercase c")
        lines.append("* Comment with asterisk")
        lines.append("# Comment with hash")

        # 14 non-comment lines
        for i in range(14):
            lines.append(f" file_{i+1}.dat                    / {i+1}")

        # More comments before dates
        lines.append("C Start date section")

        # Dates and time step
        lines.append("      01/01/2000_24:00          / BDT")
        lines.append("      0                         / RESTART")
        lines.append("C Time step")
        lines.append("        1MON                    / UNITT")
        lines.append("        12/31/2000_24:00        / EDT")

        sim_file.write_text('\n'.join(lines))

        start, end, step = iwfm.sim_info(str(sim_file))

        assert start == "01/01/2000_24:00"
        assert end == "12/31/2000_24:00"
        assert step == "1MON"


class TestSimInfoRealFile:
    """Tests using real IWFM test data files."""

    def test_with_real_simulation_file(self):
        """Test with actual C2VSimCG simulation file if available."""
        test_file = os.path.join(
            os.path.dirname(__file__),
            'C2VSimCG-2021',
            'Simulation',
            'C2VSimCG.in'
        )

        if not os.path.exists(test_file):
            pytest.skip("Test data file not available")

        start, end, step = iwfm.sim_info(test_file)

        # Verify we got strings back
        assert isinstance(start, str)
        assert isinstance(end, str)
        assert isinstance(step, str)

        # Should have valid date format (contains _24:00 or similar)
        assert "_" in start or start.replace(".", "").isdigit()
        assert "_" in end or end.replace(".", "").isdigit()

    def test_real_file_known_values(self):
        """Test known values from the real file."""
        test_file = os.path.join(
            os.path.dirname(__file__),
            'C2VSimCG-2021',
            'Simulation',
            'C2VSimCG.in'
        )

        if not os.path.exists(test_file):
            pytest.skip("Test data file not available")

        start, end, step = iwfm.sim_info(test_file)

        # From file inspection:
        # BDT = 09/30/1973_24:00
        # UNITT = 1MON
        # EDT = 09/30/1974_24:00
        assert start == "09/30/1973_24:00"
        assert end == "09/30/1974_24:00"
        assert step == "1MON"

    def test_real_file_date_format(self):
        """Test that real file dates have expected format."""
        test_file = os.path.join(
            os.path.dirname(__file__),
            'C2VSimCG-2021',
            'Simulation',
            'C2VSimCG.in'
        )

        if not os.path.exists(test_file):
            pytest.skip("Test data file not available")

        start, end, step = iwfm.sim_info(test_file)

        # Check date format: MM/DD/YYYY_HH:MM
        assert "/" in start
        assert "_" in start
        assert ":" in start

        assert "/" in end
        assert "_" in end
        assert ":" in end
