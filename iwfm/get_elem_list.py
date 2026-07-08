# get_elem_list.py
# Reads the submodel elements and returns a dictionary of old to new elements
# and a dictionary of new to old elements
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


def get_elem_list(elem_pairs_file):
    ''' get_elem_list() - Reads the submodel elements and returns a dictionary
        of old to new elements and a dictionary of new to old elements

    Parameters
    ----------
    elem_pairs_file : str
        name of file listing elements of existing nmodel and submodel

    Returns
    -------
    elem_list : list
        list of existing model elements in submodel
    
    new_srs : list
        list of existing model subregions in submodel
    
    elem_dict : dictionary
        dictionary key = existing model element, value = submodel element
    
    rev_elem_dict : dictionary
        dictionary key = submodel element, value = existing model element

    '''
    import re

    with open(elem_pairs_file, encoding='utf-8') as f:
        elem_pairs = f.read().splitlines()  # open and read input file

    elem_list = []
    for line in elem_pairs:  # cycle through the lines
        # -- add try-except to gracefully fail with error statement if file is not tab-delimited --
        elem_list.append([int(x) for x in  re.split(r';|,|\*| |\t',line)])
    elem_dict = {row[0]: row[1:] for row in elem_list}  # dictionary old elem -> new elem

    # also create a reverse dictionary new elem -> old elem
    for i in range(0, len(elem_list)):  # switch the new and old elem nos
        elem_list[i][0], elem_list[i][1] = elem_list[i][1], elem_list[i][0]
    rev_elem_dict = {row[0]: row[1:] for row in elem_list}  # dictionary new elem -> old elem

    # make a list of the subregions in the submodel
    new_srs = []
    for i in range(0, len(elem_list)):
        if int(elem_list[i][2]) not in new_srs:
            new_srs.append(int(elem_list[i][2]))
    new_srs.sort()
    if new_srs[0] == 0:
        new_srs.pop(0)

    return elem_list, new_srs, elem_dict, rev_elem_dict
