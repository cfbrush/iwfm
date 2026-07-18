# read_lu_change_zones.py
# When changing IWFM land use for a scenario, determine the model elements
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


def read_lu_change_zones(in_zone_file):
    '''When changing IWFM land use for a scenario, determine the model elements for each change zone.

    Parameters
    ----------
    in_zone_file : str
        file with change zones

    Returns
    -------
    zones : list
        1hange zones
    '''

    import re
    comments = 'Cc*#'
    with open(in_zone_file, encoding='utf-8') as f:
        temp = f.read().splitlines()
    zones = []
    for i in range(0, len(temp)):
        if temp[i][0] not in comments:  # not a comment line
            zones.append(re.split(r';|,|\*|\n|\t', temp[i]))
    for i in range(0, len(zones)):
        for j in range(0, len(zones[i])):
            zones[i][j] = int(zones[i][j])  # convert from string to int
    return zones
