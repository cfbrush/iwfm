# date_util.py
# Date validation utilities for IWFM package
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

from __future__ import annotations

from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    import datetime


def validate_date_format(date_str: str, param_name: str = 'date') -> Tuple[int, int, int]:
    """Validate that a date string is in MM/DD/YYYY format.

    Accepts dates with optional time component (e.g., '09/30/1973_24:00').
    The time component is stripped before validation.

    Parameters
    ----------
    date_str : str
        Date string to validate (may include optional time after underscore)
    param_name : str, default='date'
        Name of parameter for error messages

    Returns
    -------
    tuple
        (month, day, year) as integers

    Raises
    ------
    ValueError
        If date string is not in valid MM/DD/YYYY format
    """
    if not isinstance(date_str, str):
        raise ValueError(
            f"{param_name} must be a string, got {type(date_str).__name__}"
        )

    if not date_str or date_str.strip() == '':
        raise ValueError(
            f"{param_name} cannot be empty"
        )

    # Strip time component if present (e.g., '09/30/1973_24:00' -> '09/30/1973')
    date_only = date_str.strip().split('_')[0]

    parts = date_only.split('/')
    if len(parts) != 3:
        raise ValueError(
            f"{param_name} must be in MM/DD/YYYY format (e.g., '01/15/2020'), got '{date_str}'. "
            f"Expected 3 parts separated by '/', found {len(parts)}"
        )

    try:
        month, day, year = map(int, parts)
    except ValueError as e:
        raise ValueError(
            f"{param_name} contains non-numeric values in date part: '{date_only}' (from '{date_str}'). "
            f"All parts must be integers (MM/DD/YYYY)"
        ) from e

    # Validate ranges
    if not (1 <= month <= 12):
        raise ValueError(
            f"{param_name} has invalid month {month} in date '{date_only}' (from '{date_str}'), must be 1-12"
        )

    if not (1 <= day <= 31):
        raise ValueError(
            f"{param_name} has invalid day {day} in date '{date_only}' (from '{date_str}'), must be 1-31"
        )

    if year < 1800 or year > 5000:
        raise ValueError(
            f"{param_name} has invalid year {year} in date '{date_only}' (from '{date_str}'), must be 1800-2200"
        )

    return month, day, year


def safe_parse_date(date_str: str, param_name: str = 'date',
                    fmt: str = '%m/%d/%Y') -> 'datetime.datetime':
    """Safely parse a date string with validation.

    Parameters
    ----------
    date_str : str
        Date string to parse
    param_name : str, default='date'
        Name of parameter for error messages
    fmt : str, default='%m/%d/%Y'
        Expected date format

    Returns
    -------
    datetime
        Parsed datetime object

    Raises
    ------
    ValueError
        If date string cannot be parsed or is invalid
    """
    import datetime

    # First validate the format if it's MM/DD/YYYY
    if fmt == '%m/%d/%Y':
        try:
            month, day, year = validate_date_format(date_str, param_name)
        except ValueError:
            raise

    # Then parse with strptime, which will catch invalid dates like 02/30/2020
    try:
        dt = datetime.datetime.strptime(date_str.strip(), fmt)
        return dt
    except ValueError as e:
        raise ValueError(
            f"Invalid {param_name} '{date_str}': {str(e)}"
        ) from e


def validate_dss_date_format(date_str: str,
                             param_name: str = 'date') -> Tuple[int, int, int, int, int]:
    """Validate DSS date format (e.g., '10/31/1973_24:00').

    IWFM uses DSS format: MM/DD/YYYY_hh:mm where midnight is represented as 24:00.

    Parameters
    ----------
    date_str : str
        Date string in DSS format to validate (MM/DD/YYYY_hh:mm)
    param_name : str, default='date'
        Name of parameter for error messages

    Returns
    -------
    tuple
        (month, day, year, hour, minute) parsed components

    Raises
    ------
    ValueError
        If date string is not in valid DSS format
    """
    if not isinstance(date_str, str):
        raise ValueError(
            f"{param_name} must be a string, got {type(date_str).__name__}"
        )

    if not date_str or date_str.strip() == '':
        raise ValueError(f"{param_name} cannot be empty")

    date_str = date_str.strip()

    # DSS format: MM/DD/YYYY_hh:mm (e.g., '10/31/1973_24:00')
    # Expected length is 16 characters
    if len(date_str) != 16:
        raise ValueError(
            f"{param_name} must be in DSS format MM/DD/YYYY_hh:mm (e.g., '10/31/1973_24:00'), "
            f"expected 16 characters, got {len(date_str)} in '{date_str}'"
        )

    # Check for required separators
    if date_str[2] != '/' or date_str[5] != '/' or date_str[10] != '_' or date_str[13] != ':':
        raise ValueError(
            f"{param_name} must be in DSS format MM/DD/YYYY_hh:mm (e.g., '10/31/1973_24:00'), "
            f"got '{date_str}' with incorrect separators"
        )

    # Extract components
    try:
        month = int(date_str[0:2])
        day = int(date_str[3:5])
        year = int(date_str[6:10])
        hour = int(date_str[11:13])
        minute = int(date_str[14:16])
    except ValueError as e:
        raise ValueError(
            f"{param_name} contains invalid numeric values in '{date_str}': {str(e)}"
        ) from e

    # Validate ranges
    if not (1 <= month <= 12):
        raise ValueError(
            f"{param_name} has invalid month {month} in '{date_str}', must be 1-12"
        )

    if not (1 <= day <= 31):
        raise ValueError(
            f"{param_name} has invalid day {day} in '{date_str}', must be 1-31"
        )

    if year < 1800 or year > 5000:
        raise ValueError(
            f"{param_name} has invalid year {year} in '{date_str}', must be 1800-5000"
        )

    if not (0 <= hour <= 24):
        raise ValueError(
            f"{param_name} has invalid hour {hour} in '{date_str}', must be 0-24"
        )

    if not (0 <= minute <= 59):
        raise ValueError(
            f"{param_name} has invalid minute {minute} in '{date_str}', must be 0-59"
        )

    return month, day, year, hour, minute
