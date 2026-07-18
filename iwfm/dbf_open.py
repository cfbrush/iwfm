# dbf_open.py
# open a DBF file
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


class _DBFTable(list):
    '''s'''

    def __init__(self, records, fields):
        super().__init__(records)
        self.fields = fields
        self.records = records


def dbf_open(infile, load=False, verbose=False):
    '''Open a DBF file (read with PyShp).

    Parameters
    ----------
    infile : str
        Name of existing DBF file

    load : bool, default=False
        Retained for backward compatibility; records are always read
        into memory

    verbose : bool, default=False
        Turn command-line output on or off

    Returns
    -------
    db: _DBFTable
        list of records with .fields and .records attributes
    '''
    import shapefile  # PyShp

    with shapefile.Reader(dbf=infile) as r:
        db = _DBFTable(r.records(), r.fields)
    if verbose:
        print(f'   Opened file {infile}, contains {len(db):,} records')
    return db
