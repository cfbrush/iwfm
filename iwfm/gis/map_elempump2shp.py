# map_elempump2shp.py
# Read a shapefile of IWFM model elements and elemental pmping from a ZBudget file,
# make a deep copy of the elements files, and  add a field to the shapefile 
# for each type of pumping, then total pumping of each type for each element
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


'''Read a shapefile of IWFM model elements and elemental pmping from a ZBudget file, make a deep copy of the elements files, and add a field to the shapefile for each type of pumping, then total pumping of each type for each element.'''

def map_elempump2shp(zone_data, field_names, elem_shp_name, out_shp_name, verbose=False):
    '''Add diversion areas to shapefile of IWFM model elements.

    Parameters
    ----------
    zone_data : numpy array
        first column is zone id, the rest are column sums from col_ids columns

    field_names : list of str
        field names

    elem_shp_name : shapefile name
        IWFM Elements shapefile

    out_shp_name : shapefile name
        Output shapefile name

    verbose : bool, default = False
        Print status messages    

    Return
    ------
    nothing
    '''
    import geopandas as gpd
    import os

    gdf = gpd.read_file(elem_shp_name)                                      # read elements shapefile into geopandas dataframe

    gdf.columns = gdf.columns.str.lower()                                   # convert column names to lower case

    elem_ids = gdf['elem_id'].tolist()                                      # copy geopandas dataframe field ELEM_ID to a list
    count = 0

    for i in range(0,len(field_names)):
        field_name = field_names[i]   

        col_vals = [round(zone_data[elem-1][i+1],3) for elem in elem_ids]   # extract zone_data for field

        gdf[field_name] = col_vals                                          # add a field to the geopandas dataframe for the diversion area

        # to avoid fragmentation, make a deep copy every 50 fields
        count += 1
        if count >= 50:
            gdf = gdf.copy()
            count = 0

    shp_base = os.path.basename(out_shp_name).split('.')[0]                 # create a shapefile name

    shp_name = shp_base+'.shp'

    gdf.to_file(shp_name)                                                   # write the geopandas dataframe to a shapefile

    if verbose: print(f'  Created shapefile {shp_name}')

    return 


if __name__ == "__main__":
    ''' Run map_divs2shp() from command line '''
    import sys
    import pickle
    import iwfm.debug as idb
    import iwfm
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    # DEBUG

    if len(sys.argv) > 1:  # arguments are listed on the command line
        pkl_file       = sys.argv[1]
        elem_shp_name  = sys.argv[2]
        out_shp_root   = sys.argv[3]
    else:  # ask for file names from terminal
        pkl_file       = input('IWFM Z-Budget file name: ')
        elem_shp_name  = input('IWFM Elements shapefile name: ')
        out_shp_root   = input('Output shapefile root name: ')

    iwfm.file_test(pkl_file)
    iwfm.file_test(elem_shp_name)

    idb.exe_time()                                                          # initialize timer

    with open(pkl_file, 'rb') as f:                                         # retrieve pickled data
        zone_data = pickle.load(f)

#    col_names =['NP_Pump','RicePump','Ref_Pump','Urb_Pump']                # Land and Water Use ZBudget
    col_names =['ElemPump','WellPump']                                      # GW ZBudget

    out_shp_name = f'{out_shp_root}.shp'

    map_elempump2shp(zone_data, col_names, elem_shp_name, out_shp_name, verbose=verbose)

    idb.exe_time()                                                          # print elapsed time
