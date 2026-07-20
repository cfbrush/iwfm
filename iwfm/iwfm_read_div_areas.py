# iwfm_read_div_areas.py
# Read diversion areas from an IWFM Diversion Specification File
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


'''Read diversion areas from IWFM divirsion specification file.'''

def iwfm_read_div_areas(divspec_file_name):
    '''Read diversion areas from IWFM divirsion specification file.

    Parameters
    ----------
    divspec_file_name : str
        IWFM Diversion Specification file name

    Return
    ------
    div_ids : list
        IWFM diversion numbers

    div_areas : list of lists
        List of elements in each IWFM diversion area

    rchg_area_ids : list
        IWFM recharge numbers

    rchg_areas : list of lists
        List of elements in each IWFM recharge area
    '''
    import iwfm
    from iwfm.file_utils import read_next_line_value

    # read diversion specification file
    iwfm.file_test(divspec_file_name)
    with open(divspec_file_name, 'r', encoding='utf-8') as f:
        div_file_lines = f.readlines()

    ndivs, line_index = read_next_line_value(div_file_lines, -1, column=0)
    ndivs = int(ndivs)

    # skip ndiv lines and comment lines to get to the first delivery area
    n_delivs, line_index = read_next_line_value(div_file_lines, line_index, column=0, skip_lines=ndivs)
    n_delivs = int(n_delivs)

    deliv_area_ids, deliv_areas = [], []
    # read the element groups for each delivery
    for i in range(n_delivs):
        # the first line of a group has 3 items: deliv_area_id, number of elements, and first element number
        _, line_index = read_next_line_value(div_file_lines, line_index, column=0)
        deliv_area_id = int(div_file_lines[line_index].split()[0])
        deliv_area_ids.append(deliv_area_id)
        n_elems = int(div_file_lines[line_index].split()[1])

        elems = []
        elems.append(int(div_file_lines[line_index].split()[2]))
        # read each element in the rest of the diversion area
        for j in range(n_elems-1):
            elem, line_index = read_next_line_value(div_file_lines, line_index, column=0)
            elem = int(elem)
            elems.append(elem)

        deliv_areas.append(elems)

    rchg_area_ids, rchg_areas = [], []
    # read the element groups for each diversion recharge area
    for i in range(ndivs):
        # the first line of a group has 4 items: diversion id, number of elements, element number and factor
        _, line_index = read_next_line_value(div_file_lines, line_index, column=0)
        rchg_id = int(div_file_lines[line_index].split()[0])
        rchg_area_ids.append(rchg_id)
        n_elems = int(div_file_lines[line_index].split()[1])
        elems = []
        elems.append(int(div_file_lines[line_index].split()[2]))
        # read each element in the rest of the diversion area
        for j in range(n_elems-1):
            elem, line_index = read_next_line_value(div_file_lines, line_index, column=0)
            elem = int(elem)
            elems.append(elem)

        rchg_areas.append(elems)

    return deliv_area_ids, deliv_areas, rchg_area_ids, rchg_areas

