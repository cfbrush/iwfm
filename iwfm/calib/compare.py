# compare.py
# Take two lists, return list2 items 'in_both' and 'missing' from list1
# Copyright (C) 2020-2023 University of California
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


'''Return two lists.'''

def compare(list1,list2):
    '''Return two lists.

    missing has list1 items not in list2, in_both has list1 items in list2

    Parameters
    ----------
    list1 : list of str
        observation site names

    list2 : list of str
        observation site names

    Returns
    -------
    missing : list of str
        observation site names in list2 that are not in list1

    in_both : list of str
        observation site names in both list1 and list2
    '''

    missing, in_both  = [], []
    for item in list1:
        if item not in list2:
            missing.append(item)
        else:
            in_both.append(item)
    return missing, in_both
