# write_rmse_bias.py
# write RMSE and bias values to a text file
# Copyright (C) 2020-2026 University of California
# Based on a PEST utility written by John Doherty
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


'''Write the RMSE and Bias values plus well info (name,x,y,layer) for all observation wells to a text file.'''

def write_rmse_bias(output_filename, well_dict, well_names, rmse, bias, count):
    '''Write the RMSE and Bias values plus well info (name,x,y,layer) for all observation wells to a text file.

    Parameters
    ----------
    output_filemane : str
        Name of output data file

    well_dict : dictionary
        well data, key=well_name, values=[X,Y,Layer]

    well_names : list
        list of well_dict keys, for example state well names

    rmse : arr
        list or numpy array of rmse values for each well

    bias : arr
        list or numpy array of bias values for each well

    count : list
        number of observations for each well

    Returns
    -------
    nothing


    '''
    with open(output_filename, 'w', encoding='utf-8') as o:
        o.write('ID\tWell Name\tX\tY\tLayer\tRMSE\tBias\tCount\n')
        for i in range(0, len(well_names)):
            if well_dict.get(well_names[i]) is not None:
                info = well_dict.get(well_names[i])
                o.write(f'{i+1}\t{well_names[i]}\t{round(info.x, 2)}'+
                    f'\t{round(info.y, 2)}\t{info.layer}\t{round(rmse[i], 2)}'+
                    f'\t{round(bias[i], 2)}\t{count[i]}\n')
    return
