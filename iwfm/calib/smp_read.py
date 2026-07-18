# smp_read.py
# Read a PEST .smp file with observed values
# Copyright (C) 2020-202s University of California
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


'''Read a PEST .smp file with observed values.'''

def smp_read(smp_file_name):
    '''Read observed values smp file into list of lists obs.

    Parameters
    ----------
    smp_file_name : str
        name of smp file to read

    Returns
    -------
    obs : list
        list of lists of observed values
    '''
    import iwfm

    with open(smp_file_name, encoding='utf-8') as f:
        file_lines = f.read().splitlines()       # open and read input file

    # convert smp formatted observations to list of lists
    obs = []
    for i, line in enumerate(file_lines):
        list = line.split()
        date_str = list[1]
        try:
            date_dt = iwfm.safe_parse_date(date_str, f'{smp_file_name} line {i+1}')
        except ValueError as e:
            raise ValueError(f"Error reading {smp_file_name} line {i+1}: {str(e)}") from e
        list[1] = date_dt
        obs.append([list[0],list[1],list[2],float(list[3])])
    return obs

