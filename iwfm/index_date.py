# index_date.py
# Returns no days between two dates
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


def index_date(in_date, start_date='10/01/1984'):
    '''Return the number of days from start_date to in_date.

    Parameters
    ----------
    in_date : str
        date after start_date in MM/DD/YYYY format

    start_date : str, default='10/01/1984'
        date to count from in MM/DD/YYYY format

    Returns
    -------
    days : int
        Number of days between two dates

    Raises
    ------
    ValueError
        If date format is invalid or dates cannot be parsed
    '''
    from datetime import datetime

    def validate_date_format(date_str, param_name):
        """Validate date string format and return parsed components."""
        if not isinstance(date_str, str):
            raise ValueError(
                f"{param_name} must be a string, got {type(date_str).__name__}"
            )

        parts = date_str.split('/')
        if len(parts) != 3:
            raise ValueError(
                f"{param_name} must be in MM/DD/YYYY format, got '{date_str}'. "
                f"Expected 3 parts separated by '/', found {len(parts)}"
            )

        try:
            month, day, year = map(int, parts)
        except ValueError as e:
            raise ValueError(
                f"{param_name} contains non-numeric values: '{date_str}'. "
                f"All parts must be integers (MM/DD/YYYY)"
            ) from e

        return month, day, year

    # Validate and parse start_date
    try:
        start_month, start_day, start_year = validate_date_format(start_date, 'start_date')
        start_dt = datetime(start_year, start_month, start_day)
    except ValueError as e:
        if 'start_date' in str(e):
            raise
        raise ValueError(
            f"Invalid start_date '{start_date}': {str(e)}"
        ) from e

    # Validate and parse in_date
    try:
        in_month, in_day, in_year = validate_date_format(in_date, 'in_date')
        in_dt = datetime(in_year, in_month, in_day)
    except ValueError as e:
        if 'in_date' in str(e):
            raise
        raise ValueError(
            f"Invalid in_date '{in_date}': {str(e)}"
        ) from e

    # Calculate difference in days
    diff = in_dt - start_dt
    return diff.days
