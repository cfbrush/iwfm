# headdiff_read.py
# Read file of paired locations for groundwater head differences
# Copyright (C) 2020-2023 University of California
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

'''Read file of paired locations for groundwater head differences.'''

def headdiff_read(headdiff_file):
    '''Read the file with paired locations for calculation of vertical head differences and the observation ID of the head difference.

    Parameters
    ----------
    headdiff_file : str
        name of text file containing paired well locations

    Returns
    -------
    hdiff_sites : list
        list of head difference sites

    hdiff_pairs : list
        list of head difference pairs

    hdiff_link : list
        list of head difference links



    '''
    with open(headdiff_file, encoding='utf-8') as f:
        hd_lines = f.read().splitlines()          # open and read input file
    hdiff_pairs, hdiff_sites, hdiff_link = [], [], []

    for line in hd_lines:
        if line[0] != '#':  # skip comments
            hdiff_pairs.append(line.split())

    for item in hdiff_pairs:
        hdiff_sites.append(item[0])
        hdiff_sites.append(item[1])
        #hdiff_link.append([item[2],item[0]])
        hdiff_link.append([item[1],item[0]])

    hdiff_sites.sort( key = lambda l: (l[0]))

    return hdiff_sites, hdiff_pairs, hdiff_link
