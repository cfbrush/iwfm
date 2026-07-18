# refined_lu_factors.py
# Calculate land use factors for refined model elements
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

def refined_lu_factors(orig_areas_file,refined_areas_file,elem2elem_file):
    '''Calculate land use factors for refined model elements.

    Parameters
    ----------
    orig_areas_file : str
        original model element areas file name

    refined_elems_file : str
        refined model element areas file name

    elem2elem_file : str
        element to element file name

    Returns
    -------
    lu_factors : list
        list of land use factors for refined model elements
    '''

    import csv
    import iwfm

    # -- read the original model element areas file
    iwfm.file_test(orig_areas_file)
    with open(orig_areas_file, 'r', encoding='utf-8') as file:
        orig_areas = list(csv.reader(file))[1:]
    for line in orig_areas:
        line[0], line[1] = int(line[0]), float(line[1])
    orig_areas_d = dict(orig_areas)

    # -- read the refined model element areas file
    iwfm.file_test(refined_areas_file)
    with open(refined_areas_file, 'r', encoding='utf-8') as file:
        refined_areas = list(csv.reader(file))[1:]
    for line in refined_areas:
        line[0], line[1] = int(line[0]), float(line[1])

    # -- read the element to element file
    iwfm.file_test(elem2elem_file)
    with open(elem2elem_file, 'r', encoding='utf-8') as file:
        elem2elem = list(csv.reader(file))[1:]
    for line in elem2elem:
        line[0], line[1] = int(line[0]), int(line[1])
    elem2elem_d = dict(elem2elem)

    # -- calculate the land use factors
    lu_factors = []
    for elem in refined_areas:
        refined_elem, refined_area = elem[0], elem[1]
        orig_elem = elem2elem_d[refined_elem]
        orig_area = orig_areas_d[orig_elem]
        lu_factors.append([refined_elem, orig_elem, refined_area / orig_area ]) 

    return lu_factors

