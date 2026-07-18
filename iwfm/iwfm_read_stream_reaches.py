# iwfm_read_stream_reaches.py
# read IWFM stream reach file
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


'''Read IWFM stream reach file.'''

def iwfm_read_stream_reaches(reach_file):
    '''Read group definitions of stream reaches.

    Thin wrapper around :func:`iwfm.calib.divshort2obs.read_reaches`,
    which is the canonical parser for the stream-groundwater group file
    format (e.g. ``stgwgroups.in``).

    Parameters
    ----------
    reach_file: str
        Path to the reach groups file.

    Returns
    -------
    reaches: list
        One entry per group, ``[name, [reach_num, ...]]``.
    '''
    from iwfm.calib.divshort2obs import read_reaches
    return read_reaches(reach_file)


