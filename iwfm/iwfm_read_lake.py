# iwfm_read_lake.py
# read IWFM preprocessor lakes file
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


def iwfm_read_lake(lake_file):
    '''Read an IWFM Lake file and return (a) a list of elements and (b) a list of properties for each lake.

    Parameters
    ----------
    lake_file : str
        IWFM Preprocessor Lake file name

    Returns
    -------
    lake_elems : list
        element numbers for each lake

    lakes : list
        configuration info for each lake
          lake_id : int
              lake number
          max_elev : int
              column number in maximum elevation time series file
          dest : int
              destination stream node or lake id
          nelem : int
              number of elements in lake
    '''
    import iwfm
    from iwfm.file_utils import read_next_line_value

    iwfm.file_test(lake_file)
    with open(lake_file, encoding='utf-8') as f:
        lake_lines = f.read().splitlines()

    _, lake_index = read_next_line_value(lake_lines, -1, column=0)
    nlakes = int(lake_lines[lake_index].split()[0])

    lakes, lake_elems = [], []
    for i in range(0, nlakes):
        _, lake_index = read_next_line_value(lake_lines, lake_index, column=0)
        l = lake_lines[lake_index].split()
        lake_id = int(l.pop(0))
        max_elev = float(l.pop(0))
        dest = int(l.pop(0))
        nelem = int(l.pop(0))
        lakes.append([lake_id, max_elev, dest, nelem])
        for j in range(0, nelem):
            e = []
            if j > 0:
                _, lake_index = read_next_line_value(lake_lines, lake_index, column=0)
                l = lake_lines[lake_index].split()
            e.append(lake_id)
            e.append(int(l[0]))
            lake_elems.append(e)
    return lake_elems, lakes
