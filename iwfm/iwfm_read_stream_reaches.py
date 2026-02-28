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


def iwfm_read_stream_reaches(reach_file):
    """ read_reaches() - Read list of reaches and stream nodes
        
        Parameters
        ----------        
        reach_file: str
            Name of reach list file

        Returns
        -------
        reaches: list
            Observation names and associates stream reach(es)
    """

    with open(reach_file) as f:
        reach_list = f.read().splitlines()

    reaches = []
    for line in reach_list[3:]: # skip header lines
        if len(line) > 2:
           temp = line.split()
           reaches.append([temp[0],[int(n) for n in temp[2].split(',')]])
    # return error when len(line) <= 2?
    return reaches


