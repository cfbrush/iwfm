# get_stream_list_41.py
# Reads part of the stream specification file for file type 4.1
# and returns stream reach and rating table info
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


def get_stream_list_41(stream_lines, line_index, nreach, nrate):
    '''Read part of the stream specification file for file type 4.1 and return stream reach and rating table info.

    Version 4.1 has the same section layout as 4.2; its rating tables
    carry an extra wetted-perimeter column (WPTB). Rating table rows are
    carried as verbatim text, so the extra column passes through the
    shared 4.2 parser unchanged.

    Parameters
    ----------
    stream_lines : list of strings
        contents of stream specification file

    line_index : int
        current item in stream_lines

    nreach : int
        number of stream reaches

    nrate : int
        number of points in each stream node rating table

    Returns
    -------
    same as :func:`iwfm.get_stream_list_42`
    '''
    from iwfm.get_stream_list_42 import get_stream_list_42

    return get_stream_list_42(stream_lines, line_index, nreach, nrate)
