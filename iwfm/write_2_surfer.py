# write_2_surfer.py
# Write node (x,y) locations and nodal data to a surfer file
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

'''Write node (x,y) locations and nodal data to a surfer file.'''

def write_2_surfer(outfile_name, x_y_locs, data, date):
    '''Write node (x,y) locations and nodal data to a surfer file.

    Parameters
    ----------
    outfile_name : str
        Output file name

    x_y_locs : list
        List of (x,y) coordinates

    data : list
        Data to be written

    date : str
        Date of the data

    Returns
    -------
    nothing
    '''
    import numpy as np

    # transform data 
    data = np.asarray(data)
    data = np.transpose(data)

    # build header
    header = "'NodeID','X','Y'"
    for i in range(1, len(data[0]) + 1):
        header += f",'Layer {str(i)}'"

    # write the output file
    with open(outfile_name, 'w', encoding='utf-8') as f:
        f.write(f'{header}\n')                             # header

        for i in range(0, len(x_y_locs)):
            f.write(f'{x_y_locs[i][0]},{x_y_locs[i][1]},{x_y_locs[i][2]}')  # NodeID, X, Y
            for j in range(0,len(data[i])):
                f.write(f',{data[i][j]}')
            f.write('\n')

    return
