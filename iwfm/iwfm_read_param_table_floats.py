# iwfm_read_param_table_floats.py
# Read a table of integer parameters from a file and organize them into lists
# and return a numpy array of floats
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


def iwfm_read_param_table_floats(file_lines, line_index, lines):
    '''Read a table of integer parameters from a file and organize them into lists and return a numpy array of floats.

    Parameters
    ----------
    file_lines : list
        File contents as list of lines

    line_index : int
        The index of the line to start reading from.

    lines : int
        The number of lines to read.

    Returns
    -------

    params : list
        A list of parameters
    '''
    from iwfm.file_utils import read_param_table

    return read_param_table(file_lines, line_index, lines, cast=float)
