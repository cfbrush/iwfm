# get_change_col.py
# When changing IWFM land use for a scenario, determine which column of the
# change factors table corresponds to a specific year
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


def get_change_col(changes_table, in_year, in_chg_file):
    '''When changing IWFM land use for a scenario, determine which column of the change factors table corresponds to a specific year.

    Parameters
    ----------
    changes_table : list
        table of change factors, col = years, row = zone

    in_year : int or str
        year

    in_chg_file : str
        change table file name, for error output if necessary

    Returns
    -------
    chg_col : int
        number of column corresponding to in_year
    '''
    year = int(in_year)
    chg_col = 0
    for i in range(1, len(changes_table[0])):
        if changes_table[0][i] == year:
            chg_col = i
    if chg_col == 0:  # change year not in change file
        raise ValueError(f'{in_year} not in {in_chg_file}')
    return chg_col
