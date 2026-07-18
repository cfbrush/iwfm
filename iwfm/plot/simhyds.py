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

# ** Incomplete **
'''Class of methods for working with IWFM simulation hydrographs.'''

import bisect
import iwfm
from iwfm.debug.logger_setup import logger

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
        logger.debug(f'simhyds.sim_vals read {len(self.sim_vals)} hydrographs')
        logger.debug(f'each with {len(self.sim_vals[0])} data points')
        logger.debug(f'self.sim_dates[0:3]: {self.sim_dates[:3]}')

    def sim_head(self, date, col):
        try:
            dt = iwfm.safe_parse_date(date, 'date parameter')
        except ValueError as e:
            raise ValueError(f"Invalid date parameter in sim_head: {str(e)}") from e
        closest = min(self.sim_dates, key=lambda d: abs(d - dt))
        after  = bisect.bisect_left(self.sim_dates,dt)
        
        logger.debug(f'{date=}, {dt=}')
        logger.debug(f'{closest=}')
        logger.debug(f'self.sim_dates[after]: {self.sim_dates[after]}')

        if self.sim_dates[after] > dt:
            before = after - 1
        else: 
            before, after = after, after + 1

        # numerator: days to observed value
        num = (dt - self.sim_dates[before]).days

        # denominator: days between simulated values
        den = (self.sim_dates[after] - self.sim_dates[before]).days

        logger.debug(f'{num=}, {den=}')

        return self.sim_vals[before][col] + (
            self.sim_vals[after][col] - self.sim_vals[before][col]
        ) * (num / den)

    def get_head(self, row, col):
        return self.sim_vals[row][col]

    def date(self, row):
        return self.sim_vals[row][0]

    def start_date(self):
        return self.sim_vals[0][0]

    def end_date(self):
        return self.sim_vals[len(self.sim_vals) - 1][0]

    def nlines(self):
        return len(self.sim_vals)

    def ncols(self):
        return len(self.sim_vals[0])
