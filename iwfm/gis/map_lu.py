# map_lu.py
# Copy IWFM model elements shapefile, and create one shapefile of total area 
# for each year and element, and another shapefile with percent element area
# for each year and element
# Copyright (C) 2020-2026 University of California
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

import geopandas as gpd
import re
import sys
import iwfm.debug as idb
import iwfm 

def map_lu(land_use_file, elem_shp_name, out_shp_basename, verbose=False):
    '''map_lu() - Copy IWFM model elements shapefile, and create one shapefile of total area 
                    for each year and element, and another shapefile with percent element area
                    for each year and element

    Parameters
    ----------
    land_use_file : str
        name of existing model land use file

    elem_shp_name : str
        name of IWFM elements shapefile

    out_shp_basename : str
        basename of output shapefile

    verbose : bool, default=False
        turn command-line output on or off

    Returns
    -------
    nothing

    '''
    
    iwfm.file_test(elem_shp_name)
    gdf = gpd.read_file(elem_shp_name)                          # read elements shapefile into geopandas dataframe

    gdf.columns = gdf.columns.str.lower()                       # convert column names to lower case

    #elem_ids = gdf['elem_id'].tolist()                          # copy geopandas dataframe field ELEM_ID to a list - not used here
    
    #gdf['area'] = gdf['geometry'].area                          # calculate area of each element in shapefile - not used here

    iwfm.file_test(land_use_file)
    with open(land_use_file) as f:
        file_lines = f.read().splitlines()        # open input file

    # Read FACTLNP (area conversion factor) using utility function
    area_factor_str, line_index = iwfm.read_next_line_value(
        file_lines, -1, column=0, skip_lines=0
    )
    area_factor = float(area_factor_str)  # factor to convert area to square feet - not used here

    # Skip 4 lines (NSPLNP, NFQLNP, DSSFL, comments) to reach data section
    _, line_index = iwfm.read_next_line_value(file_lines, line_index - 1, skip_lines=4)

    lu_lines = 1                                                # how many lines per time-step? count lines to next date
    while file_lines[line_index + lu_lines].find('_24:00') == -1:
        lu_lines += 1

    data_lines = len(file_lines) - line_index                   # how many data lines per time step
    time_steps = int(data_lines/lu_lines)                       # how many time steps

    copy_count, fields_added = 0, 0                             # how many fields have been added to the shapefile
    for i in range(time_steps):
        is_first_line = 1                                       # flag for first line of time step, has date
        elem_areas = []
        for j in range(lu_lines):
            if is_first_line:                                   # process date into field name, remove and continue
                is_first_line = 0
                work_str = file_lines[line_index + i*lu_lines]
                work_str = re.sub("/", "-", work_str)
                work_str = re.sub("_24:00", "", work_str)
                work_str = re.sub("\t", " ", work_str)
                work_str = work_str.split()
                field_name = work_str.pop(0)                    # new field name for the shapefile's dbf
            else:
                work_str = file_lines[line_index + i*lu_lines + j].split()

            if len(work_str) > 2:
                area = 0
                for k in range(1, len(work_str) - 1):
                    area += float(work_str[k])
            else:
                area = float(work_str[1])
            elem_areas.append(float(f'{area:,.2f}'))

        if fields_added == 0:                                   # calculate maximum area for each element
            max_areas = elem_areas
        else:
            max_areas = [max(elem_areas[k], max_areas[k]) for k in range(len(elem_areas))]

        gdf[field_name] = elem_areas                            # add a field to the geopandas dataframe for the timestep

        copy_count += 1                                         # to avoid fragmentation, make a deep copy every 50 fields
        if copy_count >= 50:
            gdf = gdf.copy()
            copy_count = 0

    gdf['max_areas'] = max_areas                                # add a field to the geopandas dataframe for the maximum areas

    active = [1 if area > 0 else 0 for area in max_areas]    # create a list of 1's and 0's for the diversion area
    gdf['active'] = active                                   # add a field to the geopandas dataframe for the diversion area


    lu_areas_shp_name = out_shp_basename+'.shp'                 # create a shapefile name

    gdf.to_file(lu_areas_shp_name)                              # write the geopandas dataframe to a shapefile

    if verbose: print(f'  Created land use areas shapefile {lu_areas_shp_name}')

    return


if __name__ == '__main__':
    ''' Run map_lu() from command line 

    '''

    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()
    if len(sys.argv) > 1:  # arguments are listed on the command line
        land_use_file = sys.argv[1]
        elem_shp_name = sys.argv[2]
        if len(sys.argv) > 3:  # output file tupe listed on command line
            out_shp_name = sys.argv[3]
        else:
            out_shp_name = land_use_file[0 : land_use_file.find('.')]
    else:  # ask for file names from terminal
        land_use_file = input('IWFM Land use file name: ')
        elem_shp_name = input('IWFM Element shapefile: ')
        out_shp_name  = input('Output shapefile base name: ')

    iwfm.file_test(land_use_file)
    iwfm.file_test(elem_shp_name)

    idb.exe_time()  # initialize timer

    map_lu(land_use_file, elem_shp_name, out_shp_name, verbose=verbose)

    idb.exe_time()  # print elapsed time
