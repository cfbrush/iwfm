# mysql_insert_record.py
# Insert a new record to a mysql database
# Copyright (C) 2020-2021 University of California
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


'''Insert a new record to a mysql database.'''

def mysql_insert_record(cur, city, coord):
    '''Insert a record into a mysql database.

    ** Demo  **

    Parameters
    ----------
    cur : obj
        cursor (pointer to mysql record)

    city : str
        city name

    coord : str
        city coordinates

    Return
    ------
    nothing
    '''
    cur.execute(
        'INSERT INTO PLACES (name, location) VALUES ('
        + city
        + ', GeomFromText('
        + coord
        + '))'
    )
    return
