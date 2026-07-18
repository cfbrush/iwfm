# cropbud2csv.py
# Read crop-based information from IWFM Land and Water Use and Root Zone Budget 
# HDF files and write to a CSV file in a format amenable to database input
# Copyright (C) 2020-2023 University of California
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

'''Read crop-based information from IWFM Land and Water Use and Root Zone Budget.

HDF files and write to a CSV file in a format amenable to database input.
'''

def adjust_headers(headers):
    '''Replace each column header string with a truncated code for use as a database field name.

    Parameters
    ----------
    headers : list of strings
        Column headers from HDF file

    Returns
    -------
    headers: list of strings
        Modified column headers
    '''

    headers = [w.replace('Time', 'Timestep') for w in headers]
    headers = [w.replace('Area (SQ FT)', 'Area_ac') for w in headers]
    headers = [w.replace('Area (Ac)', 'Area_ac') for w in headers]
    # land and water use budget
    headers = [w.replace('Potential CUAW', 'Pot_CUAW') for w in headers]
    headers = [w.replace('Supply Requirement', 'Ag_Supp_Req') for w in headers]
    headers = [w.replace('Pumping', 'Pumping') for w in headers]
    headers = [w.replace('Deliveries', 'Deliveries') for w in headers]
    headers = [w.replace('Inflow as Surface Runoff', 'Inflow_SRO') for w in headers]
    headers = [w.replace('Shortage', 'Shortage') for w in headers]
    headers = [w.replace('ETAW', 'ETaw') for w in headers]
    headers = [w.replace('Effective Precipitation', 'ETpr') for w in headers]
    headers = [w.replace('ET from Groundwater', 'ETgr') for w in headers]
    headers = [w.replace('ET from Other Sources', 'EToth') for w in headers]
    # root zone budget
    headers = [w.replace('Potential ET', 'ETpot') for w in headers]
    headers = [w.replace('Precipitation', 'Precip') for w in headers]
    headers = [w.replace('Prime Applied Water', 'PrimeAW') for w in headers]
    headers = [w.replace('Reused Water', 'Reused') for w in headers]
    headers = [w.replace('Net Return Flow', 'NetRW') for w in headers]
    headers = [w.replace('Beginning Storage (+)', 'BegStor') for w in headers]
    headers = [w.replace('Net Gain from Land Expansion (+)', 'NetGainLandExp') for w in headers]
    headers = [w.replace('Infiltration (+)', 'Infiltration') for w in headers]
    headers = [w.replace('Groundwater Inflow (+)', 'GroundwaterIn') for w in headers]
    headers = [w.replace('Other Inflow (+)', 'OtherIn') for w in headers]
    headers = [w.replace('Pond Drain (-)', 'PondDrain') for w in headers]
    headers = [w.replace('Actual ET (-)', 'ETa') for w in headers]
    headers = [w.replace('Percolation (-)', 'Percolation') for w in headers]
    headers = [w.replace('Ending Storage (-)', 'EndStor') for w in headers]
    headers = [w.replace('Discrepancy (=)', 'Discrepancy') for w in headers]

    return headers


def process_budget_data(f, loc_names, column_headers, loc_values, write_header=False, verbose=False):
    '''Open an IWFM Budget HDF file and retreive all of the data.

    Parameters
    ----------
    outfile : File object
        Output file open for writing

    loc_names : list of strings
        Location names (subregion, stream reach, stream node, small watershed etc)

    column_headers : list of lists of strings
        Column headers for each location

    loc_values : list of dataframes
        Each dataframe contains values for one location

    print_header : bool, default=False
        If True then print header at top of file

    verbose : bool, default=False
        Turn command-line output on or off

    Returns
    -------
    nothing
    '''

    if write_header:
        # format nice headers for printout
        header = 'Subregion,Crop,'+','.join([h for h in adjust_headers(column_headers[0])])
        f.write(f'{header}\n')

    for loc in range(len(loc_names)):

        # subregion and crop
        name = loc_names[loc]

        # use last '_' to separate crop code from subregion/land use category name
        i = len(name) - name.rfind('_')
        sr, crop = str(name[:-i]), name[-(i-1):]

        values = loc_values[loc]
        vals = values.to_numpy()    # as numpy arrray, easier to convert time to string

        for row in range(vals.shape[0]):
            pv_row = []
            pv_row.append(vals[row][0].strftime('%m/%d/%Y'))    # time to string
            for i in range(1,vals.shape[1]):
                pv_row.append(str(vals[row][i]))                # values to strings
            f.write(f'{sr},{crop},{",".join([i for i in pv_row])}\n')

    return


def cropbud2csv(bud_file_ag, bud_file_pond, outfile, write_header=True, verbose=False):
    '''Read crop-based information from IWFM Land and Water Use and Root Zone Budget HDF files and write to a CSV file in a format amenable to database input.

    Parameters
    ----------
    bud_file_ag : string
        Name of IWFM Budget output HDF-formatted file for agricultural water use

    bud_file_pond : string
        Name of IWFM Budget output HDF-formatted file for ponded crop water use

    outfile : string
        Name of output CSV file

    write_header : bool, default=True
        If True then print header at top of file

    verbose : bool, default=False
        Turn command-line output on or off

    Returns
    -------
    nothing
    '''
    # Import directly from module files to avoid circular dependency
    # (iwfm.hdf5.__init__.py imports from this file)
    try:
        from iwfm.hdf5.get_budget_data_h5 import get_budget_data
    except ImportError:
        from iwfm.hdf5.get_budget_data_pywfm import get_budget_data

    # get data from budget files
    ag_budget_data = get_budget_data(bud_file_ag, verbose=verbose)      # (loc_names, column_headers, loc_values)
    pond_budget_data = get_budget_data(bud_file_pond, verbose=verbose)  # (loc_names, column_headers, loc_values)
    
    # write data to CSV file
    with open(outfile, 'w', encoding='utf-8') as f:
        process_budget_data(f, ag_budget_data[0], ag_budget_data[1], ag_budget_data[2],
                        write_header=write_header, verbose=verbose)
        process_budget_data(f, pond_budget_data[0], pond_budget_data[1], pond_budget_data[2],
                        verbose=verbose)


if __name__ == '__main__':
    ' Run from command line '
    import sys
    import iwfm.debug as idb
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()
 
    if len(sys.argv) > 1:  # arguments are listed on the command line
        bud_file_ag   = sys.argv[1]
        bud_file_pond = sys.argv[2]
        outfile       = sys.argv[3]

    else:  # ask for file names from terminal
        bud_file_ag    = input('IWFM Ag Budget HDF file name: ')
        bud_file_pond  = input('IWFM Ponded Crop Budget HDF file name: ')
        outfile        = input('Output file name: ')
        print('')

    idb.exe_time()  # initialize timer

    cropbud2csv(bud_file_ag, bud_file_pond, outfile)

    idb.exe_time()  # print elapsed time


