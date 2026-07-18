# mysql_conn.py
# Connect to a mysql database
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


'''Connect to a mysql database.'''

def mysql_conn(dbname, port=3306, host='localhost', user='root', passwd=''):
    '''Connect to a mysql database.

    Parameters
    ----------
    dbname : str
        database name

    port : int, default=3306
        post

    host : str, default='localhost'
        database host

    user : str, default='root'
        username

    passwd : str, default=''
        password

    Returns
    -------
    cur : database object
        pointer to current record

    conn : database object
        connection to open database
    '''
    import pymysql


    conn = pymysql.connect(
        host=host, port=port, user=user, passwd=passwd, db=dbname
    )
    cur = conn.cursor()
    return cur, conn
