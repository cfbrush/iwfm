# mam_elempump.py
# Read a shapefile of IWFM model elements and an IWFM element pumping file.
# Make a deep copy of the elements shapefile, and add a field for Ag pumping 
# on/off, add a field for Urban pumping on/off, add a field for each model 
# layer for Ag pumping, and a field for each model layer for urban pumpimg. 
# Set initial values to zero. Set first two fields to 1 if any pumping else 0. 
# Set Ag and Urban layer columns to FRACSKL. Write the modified shapefile to 
# a new shapefile.
# Copyright (C) 2020-2025 University of California
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

import sys
import iwfm.debug as idb
import iwfm

def map_to_shp(param_table, header, gdf, out_shp_name, verbose=False):
    ''' map_to_shp() - Map a parameter table to a shapefile
    
    Parameters
    ----------
    param_table : pandas dataframe
        Parameter table to map to the shapefile

    gdf : geopandas dataframe
        Shapefile to map the parameter table to

    out_shp_name : shapefile name
        Output shapefile name

    verbose : bool, default = False
        Print status messages    

    Return
    ------
    nothing
    
    '''

    for col in range(0,len(param_table[0])):
        field_data = []
        field_name = header[col]
        for row in range(0,len(param_table)):
            field_data.append(param_table[row][col])
        gdf[field_name] = field_data

    # write the geopandas dataframe to a shapefile
    gdf.to_file(out_shp_name)

    if verbose: print(f'  Created element pumping shapefile {out_shp_name}')

    return
    


def map_elempump(elempump_file_name, elem_shp_name, out_shp_root, verbose=False):
    ''' mam_elempump() - Add diversion areas to shapefile of IWFM model elements
    
    Parameters
    ----------
    elempump_file_name : str
        IWFM Elemental Pumping file name
    
    elem_shp_name : shapefile name
        IWFM Element shapefile name

    out_shp_root : shapefile name root
        Output shapefile root name

    verbose : bool, default = False
        Print status messages    

    Return
    ------
    nothing
    
    '''
    import geopandas as gpd

    gdf = gpd.read_file(elem_shp_name)                                      # read elements shapefile into geopandas dataframe

    gdf.columns = gdf.columns.str.lower()                                   # convert column names to lower case

    elem_ids = gdf['elem_id'].tolist()                                      # copy geopandas dataframe field ELEM_ID to a list
    count = 0

    elempump_ag, elempump_ur, elempump_other, header = iwfm.iwfm_read_elempump(elempump_file_name, elem_ids, comment=1, verbose=False)  # Read element pumping file

    out_shp_name = out_shp_root + '_elempump_ag.shp'
    map_to_shp(elempump_ag, header, gdf.copy(), out_shp_name, verbose=False)
    if verbose: print(f'  Created elemental pumping shapefile {out_shp_name}')

    out_shp_name = out_shp_root + '_elempump_urban.shp'
    map_to_shp(elempump_ur, header, gdf.copy(), out_shp_name, verbose=False)
    if verbose: print(f'  Created elemental pumping shapefile {out_shp_name}')

    out_shp_name = out_shp_root + '_elempump_other.shp'
    map_to_shp(elempump_other, header, gdf.copy(), out_shp_name, verbose=False)
    if verbose: print(f'  Created elemental pumping shapefile {out_shp_name}')


if __name__ == "__main__":
    ''' Run mam_elempump() from command line '''

    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()
    if len(sys.argv) > 1:  # arguments are listed on the command line
        elempump_file_name = sys.argv[1]
        elem_shp_name      = sys.argv[2]
        out_shp_root       = sys.argv[3]
    else:  # ask for file names from terminal
        elempump_file_name = input('IWFM Element Pumping file name: ')
        elem_shp_name      = input('IWFM Elements shapefile name: ')
        out_shp_root       = input('Output shapefile root name: ')

    iwfm.file_test(elempump_file_name)
    iwfm.file_test(elem_shp_name)

    idb.exe_time()                                                                          # initialize timer

    out_shp_name = out_shp_root + '_ElemPump'

    map_elempump(elempump_file_name, elem_shp_name, out_shp_root, verbose=verbose)    # Add element pumping to shapefile of IWFM model elements

    idb.exe_time()                                          # print elapsed time
