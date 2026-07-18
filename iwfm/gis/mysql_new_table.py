# mysql_new_table.py
# Add a new table to a mysql database
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


def mysql_new_table(cur, table_name):
    '''Add a new table to a mysql database.

    ** example/template for future use **

    Parameters
    ----------
    cur : database object
        mysql database object

    table_name : str
        name of table to add

    Returns
    -------
    nothing    

    '''
    # Add name and location fields.
    # The location field is spatially enabled to hold GIS data
    cur.execute(
        'CREATE TABLE '
        + table_name
        + ' (id int NOT NULL AUTO_INCREMENT PRIMARY KEY, Name varchar(50) NOT NULL, locationGeometry NOT NULL)'
    )
