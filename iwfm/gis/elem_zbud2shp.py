# elem_zbud2shp.py
# Read IWFM Elemental Z-Budget output file and place the sum of each column into
# a copy of the elemental hapefile
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


def elem_zbud2shp(budget_file, field_file, elem_shp_name, out_shp_name, verbose=False):
    '''Read IWFM Elemental Z-Budget output file and place the sum of each column into a copy of the elemental hapefile.

    Parameters
    ----------
    budget_file : str
        Name of IWFM Budget output file

    field_file : str
        Name of text file containing field names

    elem_shp_name : shapefile name
        IWFM Elements shapefile

    out_shp_name : shapefile name
        Output shapefile name

    verbose : bool, default = False
        Print status messages    

    Returns
    -------
    nothing
    '''
    from pathlib import Path
    import geopandas as gpd
    import numpy as np

    # -- read the Budget file into array file_lines
    with open(budget_file, encoding='utf-8') as f:
        file_lines = f.read().splitlines() 
    file_lines = [word.replace('_24:00', ' ') for word in file_lines]

    # -- Get the Budget file header and footer info
    header, footer, table, line = 0, 0, 1, 0
    while not file_lines[line][0].isdigit():  
        line += 1
        header += 1
    line += 1
    while  line < len(file_lines) and file_lines[line][0].isdigit():  
        line += 1
        table += 1
    line += 1

    if line + 5 < len(file_lines):  
        while (
            len(file_lines[line]) == 0 or not file_lines[line][0].isdigit()
        ):  
            line += 1
            footer += 1
    footer += 1
    footer -= header
    tables = round( len(file_lines) / (header + table + footer) )  
    if verbose:
        print(f'  Read {tables} tables from {budget_file}')

    # read the field names
    with open(field_file, encoding='utf-8') as f:
        field_lines = f.read().splitlines() 
    field_names = []
    for line in field_lines:
        field_names.append(line)

    # read the elements shapefile
    shapefile = gpd.read_file(elem_shp_name)                            # read elements shapefile into geopandas dataframe

    shapefile.columns = shapefile.columns.str.lower()                   # convert column names to lower case

    elem_ids = shapefile['elem_id'].tolist()                            # copy geopandas dataframe field ELEM_ID to a list
    

    # -- prepare the data for the shapefile
    # -- Step through the Budget file, one table at a time

    line = 0  
    budget_data = []
    for t in range(0, tables):  
        line += header  
        elem_data = []
        for _ in range(table):
            lines = file_lines[line].split()
            elem_data.append(lines[1:])       # skip the date - not using it
            line += 1
        line += footer  

        elem_data = np.asarray(elem_data).sum(axis=0).tolist()          # calculate sum of each column

        budget_data.append(elem_data)

    count = 0  # Initialize counter for deep copy management
    for col, field_name in enumerate(field_names):

        col_vals = [budget_data[col][elem] for elem in elem_ids]        # extract zone_data for field

        shapefile[field_name] = col_vals                                # add a field to the geopandas dataframe for the diversion area

        # to avoid fragmentation, make a deep copy every 50 fields
        count += 1
        if count >= 50:
            shapefile = shapefile.copy()
            count = 0

    shp_name = Path(out_shp_name).stem + '.shp'                          # create a shapefile name

    shapefile.to_file(shp_name)                                         # write the geopandas dataframe to a shapefile

    if verbose: print(f'  Created shapefile {shp_name}')

    return 
    


if __name__ == '__main__':
    ' Run elem_zbud2shp() from command line '
    import sys
    import iwfm.debug as idb
    import iwfm
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()


    if len(sys.argv) > 1:  # arguments are listed on the command line
        budget_file    = sys.argv[1]
        field_file     = sys.argv[2]
        elem_shp_name  = sys.argv[3]
        out_shp_root   = sys.argv[4]

    else:  # ask for file names from terminal
        budget_file    = input('IWFM Budget file name: ')
        field_file     = input('Tesxt file containing shapefile field names: ')
        elem_shp_name  = input('IWFM Elements shapefile name: ')
        out_shp_root   = input('Output shapefile root name: ')

    iwfm.file_test(budget_file)
    iwfm.file_test(field_file)
    iwfm.file_test(elem_shp_name)
    out_shp_name = f'{out_shp_root}.shp'

    idb.exe_time()  # initialize timer
    elem_zbud2shp(budget_file, field_file, elem_shp_name, out_shp_name, verbose=verbose)

    idb.exe_time()  # print elapsed time
