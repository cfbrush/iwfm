# write_2_csv.py
# Write a 3D array of crop areas to a series of 2D files for each crop
# Copyright (C) 2020-2024 University of California
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


def write_2_csv(file_base_name, data, crop_list, elem_list, no_time_steps, date_list):
    '''Write a 3D array as 2D tables (row=elements x col=time_steps) to (crops) # of comma-separated text files with filename extension 'csv'.

    Parameters
    ----------
    file_base_name : str
        Base name of output file

    data : list
        Data to be written

    crop_list : list
        List of crop codes or names

    elem_list : list
        Model element numbers

    no_time_steps : int
        Number of time steps

    date_list : list
        Dates corresponding to time steps

    Returns
    -------
    nothing
    '''
    # Create the output file names
    files = ['' for x in range(0, len(crop_list))]  # empty list

    for i in range(0, len(crop_list)):
        files[i] = ''.join([file_base_name, '_', str(i + 1), '.csv'])

    # write the arrays to the output files
    for i in range(0, len(crop_list)):
        with open(files[i], 'w', encoding='utf-8') as fp:
            fp.write('WYr')
            for j in range(no_time_steps):
                fp.write(f',{date_list[j].year}')
            fp.write('\n')
            for j in range(0, len(elem_list)):
                fp.write(f'{(elem_list[j])}')
                for k in range(no_time_steps):
                    fp.write(f',{float(data[i][j][k])}')
                fp.write('\n')
    return
