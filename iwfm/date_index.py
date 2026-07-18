# date_index.py
# Returns date inval dates from start_date
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


'''Return date inval dates from start_date.'''

def date_index(inval, start_date):
    '''Calculate a date inval months from start_date.

    Parameters
    ----------
    inval : int
        number of months from start_date

    start_date : str
        date in MM/DD/YYYY format

    Returns
    -------
    date_str : str
        date in MM/DD/YYYY format that is inval months after start_date

    Raises
    ------
    ValueError
        If date format is invalid or inval cannot be converted to integer
    TypeError
        If inval is not a valid numeric type
    '''

    # Validate start_date format
    if not isinstance(start_date, str):
        raise ValueError(
            f"start_date must be a string in MM/DD/YYYY format, "
            f"got {type(start_date).__name__}"
        )

    parts = start_date.split('/')
    if len(parts) != 3:
        raise ValueError(
            f"start_date must be in MM/DD/YYYY format, got '{start_date}'. "
            f"Expected 3 parts separated by '/', found {len(parts)}"
        )

    try:
        month_val, day_val, year_val = map(int, parts)
    except ValueError as e:
        raise ValueError(
            f"start_date contains non-numeric values: '{start_date}'. "
            f"All parts must be integers (MM/DD/YYYY)"
        ) from e

    # Validate month, day, year ranges
    if not (1 <= month_val <= 12):
        raise ValueError(
            f"Invalid month in start_date '{start_date}': {month_val}. "
            f"Month must be between 1 and 12"
        )
    if not (1 <= day_val <= 31):
        raise ValueError(
            f"Invalid day in start_date '{start_date}': {day_val}. "
            f"Day must be between 1 and 31"
        )
    if year_val < 1:
        raise ValueError(
            f"Invalid year in start_date '{start_date}': {year_val}. "
            f"Year must be positive"
        )

    # Validate inval
    try:
        months_to_add = int(inval)
    except (ValueError, TypeError) as e:
        raise ValueError(
            f"inval must be convertible to integer, got '{inval}' "
            f"of type {type(inval).__name__}"
        ) from e

    if months_to_add < 0:
        raise ValueError(
            f"inval must be non-negative, got {months_to_add}"
        )

    # Extract date components - use already-parsed date components
    y = year_val
    m = month_val
    d = day_val

    # Add months (inval is the number of months to add)
    for i in range(months_to_add):
        if m == 12:
            y += 1
            m = 1
        else:
            m += 1

    return f'{m:02d}/{d:02d}/{y}'  # format as MM/DD/YYYY


if __name__ == "__main__":
    " Run date_index() from command line "
    import sys
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    if len(sys.argv) > 1:  # arguments are listed on the command line
        inval = sys.argv[1]
        start_date = sys.argv[2]
    else:  # ask for file names from terminal
        start_date = input('Date (MM/DD/YYYY):')
        inval = input('Number of months: ')

    end_date = date_index(inval, start_date)

    print(f'  {end_date} is {inval} months after {start_date}.')
