#!/usr/bin/env python
# generate_datetime_objects.py
# Generate datetime objects for Excel
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

from datetime import datetime, timedelta


def generate_datetime_objects(start_date, n_steps, delta_t, time_unit):
    '''Generate datetime objects for Excel.

    Parameters
    ----------
    start_date : str
        Starting date string
    n_steps : int
        Number of time steps
    delta_t : float
        Time step size
    time_unit : str
        Time unit (e.g., '1MON', '1DAY')

    Returns
    -------
    list : List of datetime objects
    '''
    import iwfm
    
    dates = []
    dt = iwfm.parse_iwfm_date(start_date)

    if dt is None:
        # Fallback: just use strings
        return [f"Step {i+1}" for i in range(n_steps)]

    # Determine time increment
    if '1MON' in time_unit or 'MON' in time_unit:
        # Monthly time steps
        for i in range(n_steps):
            # Add months
            month = dt.month + i
            year = dt.year
            while month > 12:
                month -= 12
                year += 1

            # Get last day of month
            if month == 12:
                next_month = datetime(year + 1, 1, 1)
            else:
                next_month = datetime(year, month + 1, 1)

            last_day = next_month - timedelta(days=1)
            dates.append(last_day)
    else:
        # Daily or other time steps
        days_per_step = int(delta_t * 30)  # Approximate
        for i in range(n_steps):
            current_dt = dt + timedelta(days=i*days_per_step)
            dates.append(current_dt)

    return dates

