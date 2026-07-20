# parse_iwfm_date.py
# DSS date to datetime object
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


'''Parse IWFM date string format (e.g., '10/31/1973_24:00').'''

def parse_iwfm_date(date_str):
    '''Parse IWFM date string format (e.g., '10/31/1973_24:00').

    Parameters
    ----------
    date_str : str
        IWFM format date string

    Returns
    -------
    datetime : datetime object
    '''
    from datetime import datetime, timedelta

    try:
        # Split date and time
        date_part, time_part = date_str.split('_')
        # Handle 24:00 as end of day
        if time_part == '24:00':
            dt = datetime.strptime(date_part, '%m/%d/%Y')
            dt = dt + timedelta(days=1)
        else:
            dt = datetime.strptime(f"{date_part} {time_part}", '%m/%d/%Y %H:%M')
        return dt
    except (ValueError, AttributeError):  # unparseable string or None input
        return None

