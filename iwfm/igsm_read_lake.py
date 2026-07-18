# igsm_read_lake.py
# Read an IGSM pre-processor lakes file
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


def igsm_read_lake(lake_file):
    '''Read an IGSM Lake file and return (a) a list of elements and (b) a list of properties for each lake.

    Parameters
    ----------
    lake_file : str
        name of IGSM lake file

    Returns
    -------
    lake_elems : list
        all lake elements

    lakes : list
        [lake_id, max_elev, next, nelem] for each lake
    '''
    import iwfm
    from iwfm.file_utils import read_next_line_value

    iwfm.file_test(lake_file)
    with open(lake_file, encoding='utf-8') as f:
        lake_lines = f.read().splitlines()  # open and read input file

    # skip comments and read number of lakes
    nlakes_str, lake_index = read_next_line_value(lake_lines, -1, column=0)
    nlakes = int(nlakes_str)

    # skip comments to first lake data line
    _, lake_index = read_next_line_value(lake_lines, lake_index, column=0)

    lakes = []
    lake_elems = []
    current_line = lake_index  # track current line being read

    for i in range(nlakes):
        l = lake_lines[current_line].split()  # read lake header line
        lake_id = int(l.pop(0))
        max_elev = float(l.pop(0))
        next = int(l.pop(0))
        nelem = int(l.pop(0))
        lakes.append([lake_id, max_elev, next, nelem])

        # Read elements for this lake
        for j in range(nelem):
            e = []
            e.append(lake_id)  # lake number
            e.append(int(l.pop(0)))  # element number
            e.append(float(l.pop(0)))  # area
            lake_elems.append(e)

            # Move to next line (either next element or next lake header)
            current_line += 1
            if current_line < len(lake_lines):
                l = lake_lines[current_line].split()

    return lake_elems, lakes
