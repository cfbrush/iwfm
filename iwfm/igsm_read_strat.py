# igsm_read_strat.py
# Read an IGSM pre-processor stratigraphy file
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


def igsm_read_strat(strat_file, node_coords):
    '''Read an IGSM Stratigraphy file and return a list of stratigraphy for each node.

    Parameters
    ----------
    strat_file : str
        IGSM nodal stratigraphy file name

    node_coords: list
        nodes and coordinates

    Returns
    -------
    strat : list
        stratigraphy information

    nlayers : int
        number of aquifer layers
    '''
    import iwfm
    from iwfm.file_utils import read_next_line_value

    iwfm.file_test(strat_file)
    with open(strat_file, encoding='utf-8') as f:
        strat_lines = f.read().splitlines()

    # skip comments and read number of layers
    layers, strat_index = read_next_line_value(strat_lines, -1, column=0)

    strat = []
    # skip comments to first stratigraphy data line
    _, strat_index = read_next_line_value(strat_lines, strat_index, column=0)
    for i in range(0, len(node_coords)):
        s = []
        l = strat_lines[strat_index + i].split()
        s.append(int(l.pop(0)))
        for j in range(0, len(l)):
            s.append(float(l.pop(0)))
        strat.append(s)
    nlayers = int((len(strat[0]) - 1) / 2)
    return strat, nlayers
