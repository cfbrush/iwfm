# map_param2shp_nodes.py
# Read a shapefile of IWFM model nodes and map an IWFM parameter to the nodes
# to 1 if served by the diversion else 0
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


def map_param2shp_nodes(param_type, param_vals, node_shp_name, out_shp_name='nodal_parameters', layers=0, verbose=False):
    '''Read a shapefile of IWFM model nodes and map an IWFM parameter to the nodes.

    Parameters
    ----------
    param_type : string
        name of parameter

    param_vals : list
        list of parameter values

    node_shp_name : shapefile name
        IWFM Nodes shapefile

    out_shp_name : shapefile name, default = 'nodal_parameters'
        IWFM output shapefile name

    layers : list, default = 0
        list of layer numbers

    verbose : bool, default = False
        Print status messages    

    Return
    ------
    nothing
    '''
    import geopandas as gpd
    import os

    gdf = gpd.read_file(node_shp_name)                                  # read nodes shapefile into geopandas dataframe

    gdf.columns = gdf.columns.str.lower()                               # convert column names to lower case

    node_ids = gdf['node_id'].tolist()                                  # copy geopandas dataframe field node_id to a list


    if layers > 0:                                                      # groundwater parameters
        count = 0
        for layer in range(layers):
            if param_type in ['Kh', 'Kv', 'Kq']:                        # plot Kh or Kv for layer 
                do_it = 1
            elif param_type == 'Sy' and layer == 0:                     # plot Sy for layer 1
                do_it = 1
            elif param_type == 'Ss' and layer >= 1:                     # plot Ss for layers > 0
                do_it = 1
            else:
                do_it = 0
    
            if do_it == 1:                                              # add a field for the parameter
                field_name = f'{param_type}_{layer+1}'                  # create the field name

                data = [param_vals[i][layer] for i in range(0, len(node_ids))] # compile data for the field

                gdf[field_name] = data                                  # add a field to the geopandas dataframe

                count += 1
                # to avoid fragmentation, make a deep copy every 50 fields
                if count >= 50:
                    gdf = gdf.copy()
                    count = 0

    else:                                                               # other parameters
            
        field_name = f'{param_type}'                                    # create the field name
    
        data = [param_vals[node-1][layer] for node in node_ids]         # compile data for the field

        gdf[field_name] = data                                          # add a field to the geopandas dataframe

    out_shp_base = os.path.basename(out_shp_name).split('.')[0]         # create a parameter shapefile name

    out_shp_name = out_shp_base+'_'+param_type+'.shp'

    gdf.to_file(out_shp_name)                                           # write the geopandas dataframe to a shapefile

    if verbose: print(f'  Created IWFM parameter shapefile {out_shp_name}')

    return 


if __name__ == "__main__":
    ''' Run map_param2shp_nodes() from command line using groundwater file'''
    import sys
    import iwfm.debug as idb
    import iwfm
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    args = sys.argv

    if len(args) > 1:  # arguments are listed on the command line
        gw_file_name       = args[1]                                    # groundwate.dat file
        node_shp_name      = args[2]
        out_shp_name       = args[3]
    else:  # ask for file names from terminal
        gw_file_name       = input('IWFM Groundwater file name: ')
        node_shp_name      = input('IWFM Nodal shapefile name: ')
        out_shp_name       = input('Output shapefile name: ')

    iwfm.file_test(gw_file_name)
    iwfm.file_test(node_shp_name)

    idb.exe_time()                                                      # initialize timer

    layers, Kh, Ss, Sy, Kq, Kv = iwfm.get_gw_params(gw_file_name)

    map_param2shp_nodes('Kh', Kh, node_shp_name, out_shp_name, layers, verbose=verbose)   

    map_param2shp_nodes('Kv', Kv, node_shp_name, out_shp_name, layers, verbose=verbose)   

    map_param2shp_nodes('Kq', Kq, node_shp_name, out_shp_name, layers, verbose=verbose)   

    map_param2shp_nodes('Sy', Sy, node_shp_name, out_shp_name, layers, verbose=verbose)   

    map_param2shp_nodes('Ss', Ss, node_shp_name, out_shp_name, layers, verbose=verbose)   

    # read another parameter from another file

    # map the parameter to a shapefile
    #map_param2shp_nodes('par_name', par_vals, node_shp_name, out_shp_name, verbose=verbose)   

    idb.exe_time()                                                  # print elapsed time
