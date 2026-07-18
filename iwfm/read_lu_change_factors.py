# read_lu_change_factors.py
# When changing IWFM land use for a scenario, read the change factors
# for each change zone
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


def read_lu_change_factors(in_chg_file):
    '''Read the change factors for changing IWFM land use for a scenario.

    Parameters
    ----------
    in_chg_file : str
        change factors file name

    Returns
    -------
    change_table : list
        change factors
    '''
    import re
    import iwfm

    iwfm.file_test(in_chg_file)
    with open(in_chg_file, encoding='utf-8') as f:
        temp = f.read().splitlines()
    change_table = []
    for i in range(0, len(temp)):
        item = re.split(r';|,|\*|\n|\t', temp[i])
        if i == 0:
            for j in range(1, len(item)):
                item[j] = int(item[j])
        else:
            item[0] = int(item[0])
            for j in range(1, len(item)):
                item[j] = float(item[j])
        change_table.append(item)
    return change_table
