# dss_date.py
# Convert datetime object to DSS-format straing
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


'''Convert datetime object 'date' into a string in DSS format MM/DD/YYYY_HH:MM with HH in 24-hour format, midnight = 24:00.'''

def dss_date(date):
    '''Convert datetime object 'date' into a string in DSS format MM/DD/YYYY_HH:MM with HH in 24-hour format, midnight = 24:00.

    Parameters
    ----------
    date : datetime
        date as datetime object

    Returns
    -------
    date : str
        date as string in DSS format
    '''

    mo = str(date.month).rjust(2, '0')  # right-justify to 2 chars
    dy = str(date.day).rjust(2, '0')  # right-justify to 2 chars
    hour = date.hour
    if hour == 0:  # if midnight then put in DSS value
        hour = 24
    hr = str(hour).rjust(2, '0')  # right-justify to 2 chars
    mn = str(date.minute).rjust(2, '0')  # right-justify to 2 chars
    return f'{mo}/{dy}/{str(date.year)}_{hr}:{mn}'
