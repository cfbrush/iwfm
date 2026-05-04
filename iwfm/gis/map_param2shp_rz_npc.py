# map_param2shp_rz_npc.py
# Read a shapefile of IWFM model elements and map IWFM Non-Ponded Crop parameters to the elements
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


def map_param2shp_rz_npc(param_types, param_vals, crops, elem_shp_name, out_shp_name='elem_parameters', verbose=False):
    ''' map_param2shp_rz_npc() - Read a shapefile of IWFM model elements and map IWFM 
                    Non-Ponded Crop parameters to the elements
    
    Parameters
    ----------
    param_types : list
        names of parameters

    param_vals : list of lists
        lists of parameter values

    crops : list
        list of crop names

    elem_shp_name : shapefile name
        IWFM Elements shapefile name

    out_shp_name : shapefile name, default = 'elem_parameters'
        IWFM output shapefile name

    verbose : bool, default = False
        Print status messages    

    Return
    ------
    nothing
    
    '''
    import geopandas as gpd
    import os

    param_types = [t.lower() for t in param_types]                      # convert parameter names to lower case

    gdf = gpd.read_file(elem_shp_name)                                  # read elements shapefile into geopandas dataframe

    gdf.columns = gdf.columns.str.lower()                               # convert column names to lower case

    out_shp_base = os.path.basename(out_shp_name).split('.')[0]         # create a parameter shapefile name

    count = 0

    for j in range(len(param_types)):
        gdf_copy = gdf.copy()                                           # make a copy of the geopandas dataframe
        field_name = f'{param_types[j]}'                                # create the field name
    
        if param_vals[j].ndim > 1: 

            for i in range(param_vals[j].shape[1]):

                if param_vals[j].shape[1] == len(crops) + 1:            # initial condition has extra fiels
                    if i == 0:
                        f_name = f'{param_types[j]}_IC'
                    else:
                        f_name = field_name+'_'+crops[i-1]
                else:
                    f_name = field_name+'_'+crops[i]

                data = param_vals[j][:,i]

                gdf_copy[f_name] = data                                 # add a field to the geopandas dataframe

                count += 1
                # to avoid fragmentation, make a deep copy every 50 fields
                if count >= 50:
                    gdf_copy = gdf_copy.copy()
                    count = 0

            out_shp_name = out_shp_base+'_'+param_types[j]+'.shp'

            gdf_copy.to_file(out_shp_name)                              # write the geopandas dataframe to a shapefile

            if verbose: print(f'  Created IWFM parameter shapefile {out_shp_name}')

        else:
            from iwfm.debug.logger_setup import logger
            logger.info(f'Skipping parameter {param_types[j]}')


    return 


if __name__ == "__main__":
    ''' Run map_param2shp_rz_npc() from command line'''
    import sys
    import iwfm.debug as idb
    import iwfm
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    args = sys.argv

    if len(args) > 1:  # arguments are listed on the command line
        rz_file_name       = args[1]
        elem_shp_name      = args[2]
        out_shp_name       = args[3]
    else:  # ask for file names from terminal
        rz_file_name       = input('IWFM Root Zone Main file name: ')
        elem_shp_name      = input('IWFM Elements shapefile name: ')
        out_shp_name       = input('Output shapefile name: ')

    iwfm.file_test(rz_file_name)
    iwfm.file_test(elem_shp_name)

    idb.exe_time()                                                            # initialize timer

    param_types = ["cn", "et", "wsp", "ip", "ms", "ts", "rf", "ru", "ic"]

    crops, param_vals, files = iwfm.iwfm_read_rz_npc(rz_file_name)            # Read non-ponded rootzone parameters

    map_param2shp_rz_npc(param_types, param_vals, crops, elem_shp_name, out_shp_name=out_shp_name, verbose=verbose)

    idb.exe_time()                                                            # print elapsed time

