# simhyds_file.py
# Class of methods for working with IWFM simulation hydrographs
# Copyright (C) 2020-2026 University of California
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

import bisect
import iwfm

class simhyds:

    def __init__(self, filename):
        self.sim_vals, self.sim_dates = [], []
        self.filename = filename
        with open(filename, 'r', encoding='utf-8') as inputfile:
            lines = inputfile.read().splitlines()
        lines = [word.replace('_24:00', ' ') for word in lines]

        for j in range(9, len(lines)):
            line = lines[j].split()
            date_str = line[0]
            try:
                line[0] = iwfm.safe_parse_date(date_str, f'{filename} line {j+1}')
            except ValueError as e:
                raise ValueError(f"Error reading {filename} line {j+1}: {str(e)}") from e
            self.sim_dates.append(line[0])
            for i in range(1, len(line)):
                line[i] = float(line[i])
            self.sim_vals.append(line)

    def sim_head(self, date, col):
        ''' sim_head() - Get interpolated head value at a specific date

        Parameters
        ----------
        date : str
            Date string to get head value for
        col : int
            Column index for the hydrograph

        Returns
        -------
        float
            Interpolated head value

        Raises
        ------
        ValueError
            If date is outside the simulation period or no data available
        '''
        if not self.sim_dates:
            raise ValueError("No simulation data available")

        try:
            dt = iwfm.safe_parse_date(date, 'date parameter')
        except ValueError as e:
            raise ValueError(f"Invalid date parameter in sim_head: {str(e)}") from e

        # Check if date is outside simulation period
        if dt < self.sim_dates[0]:
            raise ValueError(f"Date {date} is before simulation start date {self.sim_dates[0]}")
        if dt > self.sim_dates[-1]:
            raise ValueError(f"Date {date} is after simulation end date {self.sim_dates[-1]}")

        # Find position using binary search
        after = bisect.bisect_left(self.sim_dates, dt)

        # Handle exact match at end of list
        if after >= len(self.sim_dates):
            after = len(self.sim_dates) - 1

        # Determine before and after indices for interpolation
        if self.sim_dates[after] == dt:
            # Exact match - no interpolation needed
            return self.sim_vals[after][col]
        elif self.sim_dates[after] > dt:
            before = after - 1
        else:
            before, after = after, after + 1

        # numerator: days to observed value
        num = (dt - self.sim_dates[before]).days

        # denominator: days between simulated values
        den = (self.sim_dates[after] - self.sim_dates[before]).days

        if den == 0:
            return self.sim_vals[before][col]

        return self.sim_vals[before][col] + (
            self.sim_vals[after][col] - self.sim_vals[before][col]
        ) * (num / den)

    def get_head(self, row, col):
        return self.sim_vals[row][col]

    def date(self, row):
        return self.sim_vals[row][0]

    def start_date(self):
        if not self.sim_vals:
            return None
        return self.sim_vals[0][0]

    def end_date(self):
        if not self.sim_vals:
            return None
        return self.sim_vals[-1][0]

    def nlines(self):
        return len(self.sim_vals)

    def ncols(self):
        if not self.sim_vals:
            return 0
        return len(self.sim_vals[0])
