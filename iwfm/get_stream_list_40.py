# get_stream_list_40.py
# Reads part of the stream specification file for file type 4.0
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


'''Read part of the stream specification file for file type 4.0 and return stream reach and rating table info.'''

def get_stream_list_40(stream_lines, line_index, nreach, nrate):
    '''Read part of the stream specification file for file type 4.0 and return stream reach and rating table info.

    Version 4.0 has the same layout as 4.2: reach lines are
    ID NRD IDWN NAME, each stream node line pairs one stream node with one
    groundwater node, and each rating table row is BOTR/HRTB/QRTB. Rating
    table rows are carried as verbatim text, so the shared 4.2 parser
    handles this format directly.

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
