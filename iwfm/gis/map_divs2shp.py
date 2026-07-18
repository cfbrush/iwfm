# map_divs2shp.py
# Read a shapefile of IWFM model elements and an IWFM diversion specification
# make a deep copy of the elements files, and  add a field to the shapefile 
# for each delivery area, setting element value to 1 if in the delivery area else 0
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


def map_divs2shp(deliv_area_ids, deliv_areas, elem_shp_name, out_shp_name, verbose=False):
    '''Add diversion areas to shapefile of IWFM model elements.

    Parameters
    ----------
    deliv_area_ids : list
        IWFM delivery area numbers

    deliv_areas : list of lists
        List of elements in each IWFM delivery area

    elem_shp_name : shapefile name
        IWFM Elements shapefile

    out_shp_name : shapefile name
        IWFM diversion areas shapefile name

    verbose : bool, default = False
        Print status messages

    Return
    ------
    nothing
    '''
    import geopandas as gpd
    import os
    import warnings

    gdf = gpd.read_file(elem_shp_name)                                      # read elements shapefile into geopandas dataframe

    gdf.columns = gdf.columns.str.lower()                                   # convert column names to lower case

    elem_ids = gdf['elem_id'].tolist()                                      # copy geopandas dataframe field ELEM_ID to a list
    count = 0

    for deliv_id, div_area in zip(deliv_area_ids, deliv_areas):
        field_name = f'DelAr_{deliv_id}'                                    # add a field to the shapefile's dbf for the diversion area

        div_elems = [1 if elem in div_area else 0 for elem in elem_ids]     # create a list of 1's and 0's for the diversion area

        gdf[field_name] = div_elems                                         # add a field to the geopandas dataframe for the diversion area

        # to avoid fragmentation, make a deep copy every 50 fields
        count += 1
        if count >= 50:
            gdf = gdf.copy()
            count = 0

    # create a diversion specification shapefile name
    divareas_shp_base = os.path.basename(out_shp_name).split('.')[0]

    divareas_shp_name = divareas_shp_base+'.shp'

    # write the geopandas dataframe to a shapefile
    # suppress DBF field limit warning (255 vs 256 fields)
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', message='Creating a 256th field.*', category=RuntimeWarning)
        gdf.to_file(divareas_shp_name)

    if verbose: print(f'  Created diversion delivery areas shapefile {divareas_shp_name}')

    return 


if __name__ == "__main__":
    ''' Run map_divs2shp() from command line '''
    import sys
    import iwfm.debug as idb
    import iwfm
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    if len(sys.argv) > 1:  # arguments are listed on the command line
        divspec_file_name  = sys.argv[1]
        elem_shp_name      = sys.argv[2]
        out_shp_root       = sys.argv[3]
    else:  # ask for file names from terminal
        divspec_file_name  = input('IWFM Diversion Specification file name: ')
        elem_shp_name      = input('IWFM Elements shapefile name: ')
        out_shp_root       = input('Output shapefile root name: ')

    iwfm.file_test(divspec_file_name)
    iwfm.file_test(elem_shp_name)

    idb.exe_time()                                                                          # initialize timer

    deliv_area_ids, deliv_areas, rchg_area_ids, rchg_areas = iwfm.iwfm_read_div_areas(divspec_file_name)  # Read diversion specification file

    out_shp_name = out_shp_root + '_DelivArea'

    map_divs2shp(deliv_area_ids, deliv_areas, elem_shp_name, out_shp_name, verbose=verbose)    # Add diversion areas to shapefile of IWFM model elements

    idb.exe_time()                                          # print elapsed time
