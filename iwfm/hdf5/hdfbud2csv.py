# hdfbud2csv.py
# Read information from an IWFM Budget HDF file and write to a CSV file in a 
# format amenable to database input
# Currently processes any budget file, but only modifies headers to field names
# for Lane and Water Use and Root Zone budget files
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

    # NOTE: Some items are repeated here because they occur in multiple budgets
    #       This will reduce issues if the budget types are separated in the future

    # small watersheds
    headers = [w.replace('Precipitation', 'Precip') for w in headers]
    headers = [w.replace('Runoff', 'Runoff') for w in headers]
    headers = [w.replace('Root Zone Beginning Storage (+)', 'BegStorRZ') for w in headers]
    headers = [w.replace('Infiltration', 'Infiltration') for w in headers]
    headers = [w.replace('Actual ET (-)', 'ETa') for w in headers]
    headers = [w.replace('Percolation', 'Percolation') for w in headers]
    headers = [w.replace('Deep Percolation', 'DeepPerc') for w in headers]
    headers = [w.replace('Root Zone Ending Storage (-)', 'EndStorRZ') for w in headers]
    headers = [w.replace('Root Zone Discrepancy (=)', 'DiscrepancyRZ') for w in headers]
    headers = [w.replace('GW Beginning Storage (+)', 'BegStorGW') for w in headers]
    headers = [w.replace('Recharge (+)', 'Recharge') for w in headers]
    headers = [w.replace('Base Flow (-)', 'BaseFlow') for w in headers]
    headers = [w.replace('GW Return Flow (-)', 'ReturnFlowGW') for w in headers]
    headers = [w.replace('GW Enging Storage (-)', 'EndStorGW') for w in headers]
    headers = [w.replace('GW Discrepancy (=)', 'DiscrepancyGW') for w in headers]
    headers = [w.replace('Total Surface Flow (+)', 'SurfFlowTot') for w in headers]
    headers = [w.replace('Percolation to GW (-)', 'PercolationGW') for w in headers]
    headers = [w.replace('Net Stream Inflow (=)', 'StreamInNet') for w in headers]
    headers = [w.replace('Total GW Inflow', 'InflowGWTot') for w in headers]

    # land and water use budget
    headers = [w.replace('Ag. Area (SQ FT)', 'Ag_Area_ac') for w in headers]
    headers = [w.replace('Ag. Area (acres)', 'Ag_Area_ac') for w in headers]
    headers = [w.replace('Potential CUAW', 'Pot_CUAW') for w in headers]
    headers = [w.replace('Ag. Supply Requirement', 'Ag_Supp_Req') for w in headers]
    headers = [w.replace('Ag. Pumping', 'Ag_Pumping') for w in headers]
    headers = [w.replace('Ag. Deliveries', 'Ag_Deliveries') for w in headers]
    headers = [w.replace('Ag. Inflow as Surface Runoff', 'Ag_Inflow_SRO') for w in headers]
    headers = [w.replace('Ag. Shortage', 'Ag_Shortage') for w in headers]
    headers = [w.replace('Ag. ETAW', 'Ag_ETaw') for w in headers]
    headers = [w.replace('Ag. Effective Precipitation', 'Ag_ETpr') for w in headers]
    headers = [w.replace('Ag. ET from Groundwater', 'Ag_ETgr') for w in headers]
    headers = [w.replace('Ag. ET from Other Sources', 'Ag_EToth') for w in headers]
    headers = [w.replace('Ag. Effective Precip', 'Ag_ETpr') for w in headers]

    headers = [w.replace('Urban Area (SQ FT)', 'Ur_Area_ac') for w in headers]
    headers = [w.replace('Urban Area (acres)', 'Ur_Area_ac') for w in headers]
    headers = [w.replace('Urban Supply Requirement', 'Ur_Supp_Req') for w in headers]
    headers = [w.replace('Urban Pumping', 'Ur_Pumping') for w in headers]
    headers = [w.replace('Urban Deliveries', 'Ur_Deliveries') for w in headers]
    headers = [w.replace('Urban Inflow as Surface Runoff', 'Ur_Inflow_SRO') for w in headers]
    headers = [w.replace('Urban Shortage', 'Ur_Shortage') for w in headers]

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
    headers = [w.replace('Ag. Potential ET', 'Ag_ETpot') for w in headers]
    headers = [w.replace('Ag. Precipitation', 'Ag_Precip') for w in headers]
    headers = [w.replace('Ag. Runoff', 'Ag_Runoff') for w in headers]
    headers = [w.replace('Ag. Prime Applied Water', 'Ag_PrimeAW') for w in headers]
    headers = [w.replace('Ag. Inflow as Surface Runoff', 'Ag_Inflow_SRO') for w in headers]
    headers = [w.replace('Ag. Reused Water', 'Ag_Reused') for w in headers]
    headers = [w.replace('Ag. Net Return Flow', 'Ag_NetRW') for w in headers]
    headers = [w.replace('Ag. Beginning Storage (+)', 'Ag_BegStor') for w in headers]
    headers = [w.replace('Ag. Net Gain from Land Expansion (+)', 'Ag_NetGainLandExp') for w in headers]
    headers = [w.replace('Ag. Infiltration (+)', 'Ag_Infiltration') for w in headers]
    headers = [w.replace('Ag. Groundwater Inflow (+)', 'Ag_GroundwaterIn') for w in headers]
    headers = [w.replace('Ag. Other Inflow (+)', 'Ag_OtherIn') for w in headers]
    headers = [w.replace('Ag. Pond Drain (-)', 'Ag_PondDrain') for w in headers]
    headers = [w.replace('Ag. Actual ET (-)', 'Ag_ETa') for w in headers]
    headers = [w.replace('Ag. Percolation (-)', 'Ag_Percolation') for w in headers]
    headers = [w.replace('Ag. Ending Storage (-)', 'Ag_EndStor') for w in headers]
    headers = [w.replace('Ag. Discrepancy (=)', 'Ag_Discrepancy') for w in headers]
    headers = [w.replace('Ag. Precip', 'Ag_Precip') for w in headers]
    headers = [w.replace('Ag. ETa', 'Ag_ETa') for w in headers]

    headers = [w.replace('Urban Potential ET', 'Ur_ETpot') for w in headers]
    headers = [w.replace('Urban Precipitation', 'Ur_Precip') for w in headers]
    headers = [w.replace('Urban Runoff', 'Ur_Runoff') for w in headers]
    headers = [w.replace('Urban Prime Applied Water', 'Ur_PrimeAW') for w in headers]
    headers = [w.replace('Urban Inflow as Surface Runoff', 'Ur_Inflow_SRO') for w in headers]
    headers = [w.replace('Urban Reused Water', 'Ur_Reused') for w in headers]
    headers = [w.replace('Urban Net Return Flow', 'Ur_NetRW') for w in headers]
    headers = [w.replace('Urban Beginning Storage (+)', 'Ur_BegStor') for w in headers]
    headers = [w.replace('Urban Net Gain from Land Expansion (+)', 'Ur_NetGainLandExp') for w in headers]
    headers = [w.replace('Urban Infiltration (+)', 'Ur_Infiltration') for w in headers]
    headers = [w.replace('Urban Groundwater Inflow (+)', 'Ur_GroundwaterIn') for w in headers]
    headers = [w.replace('Urban Other Inflow (+)', 'Ur_OtherIn') for w in headers]
    headers = [w.replace('Urban Actual ET (-)', 'Ur_ETa') for w in headers]
    headers = [w.replace('Urban Percolation (-)', 'Ur_Percolation') for w in headers]
    headers = [w.replace('Urban Ending Storage (-)', 'Ur_EndStor') for w in headers]
    headers = [w.replace('Urban Discrepancy (=)', 'Ur_Discrepancy') for w in headers]
    headers = [w.replace('Urban Precip', 'Ur_Precip') for w in headers]
    headers = [w.replace('Urban ETa', 'Ur_ETa') for w in headers]

    headers = [w.replace('Native&Riparian Veg. Area (SQ FT)', 'NR_Area_ac') for w in headers]
    headers = [w.replace('Native&Riparian Veg. Area (acres)', 'NR_Area_ac') for w in headers]
    headers = [w.replace('Native&Riparian Veg. Potential ET', 'NR_ETpot') for w in headers]
    headers = [w.replace('Native&Riparian Veg. Precipitation', 'NR_Precip') for w in headers]
    headers = [w.replace('Native&Riparian Veg. Inflow as Surface Runoff', 'NR_Inflow_SRO') for w in headers]
    headers = [w.replace('Native&Riparian Veg. Runoff', 'NR_Runoff') for w in headers]
    headers = [w.replace('Native&Riparian Veg. Beginning Storage (+)', 'NR_BegStor') for w in headers]
    headers = [w.replace('Native&Riparian Veg. Net Gain from Land Expansion (+)', 'NR_NetGainLandExp') for w in headers]
    headers = [w.replace('Native&Riparian Veg. Infiltration (+)', 'NR_Infiltration') for w in headers]
    headers = [w.replace('Native&Riparian Veg. Groundwater Inflow (+)', 'NR_GroundwaterIn') for w in headers]
    headers = [w.replace('Native&Riparian Veg. Other Inflow (+)', 'NR_OtherIn') for w in headers]
    headers = [w.replace('Native&Riparian Veg. Stream Inflow for ET (+)', 'NR_StreamIn') for w in headers]
    headers = [w.replace('Native&Riparian Veg. Actual ET (-)', 'NR_ETa') for w in headers]
    headers = [w.replace('Native&Riparian Veg. Percolation (-)', 'NR_Percolation') for w in headers]
    headers = [w.replace('Native&Riparian Veg. Ending Storage (-)', 'NR_EndStor') for w in headers]
    headers = [w.replace('Native&Riparian Veg. Discrepancy (=)', 'NR_Discrepancy') for w in headers]
    headers = [w.replace('Native&Riparian Veg. Inflow_SRO', 'NR_Inflow_SRO') for w in headers]
    headers = [w.replace('Native&Riparian Veg. Precip', 'NR_Precip') for w in headers]
    headers = [w.replace('Native&Riparian Veg. ETa', 'NR_ETa') for w in headers]


    # groundwater
    headers = [w.replace('Beginning Storage (+)', 'BegStor') for w in headers]
    headers = [w.replace('Deep Percolation (+)', 'DeepPerc') for w in headers]
    headers = [w.replace('Gain from Stream (+)', 'StreamGain') for w in headers]
    headers = [w.replace('Recharge (+)', 'Recharge') for w in headers]
    headers = [w.replace('Gain from Lake (+)', 'LakeGain') for w in headers]
    headers = [w.replace('Boundary Inflow (+)', 'BoundaryIn') for w in headers]
    headers = [w.replace('Subsidence (+)', 'Subsidence') for w in headers]
    headers = [w.replace('Subsurface Irrigation (+)', 'SubIrr') for w in headers]
    headers = [w.replace('Tile Drain Outflow (-)', 'DrainOut') for w in headers]
    headers = [w.replace('Pumping (-)', 'Pumping') for w in headers]
    headers = [w.replace('Outflow to Root Zone (-)', 'ToRZ') for w in headers]
    headers = [w.replace('Net Subsurface Inflow (+)', 'NetSubsIn') for w in headers]
    headers = [w.replace('Ending Storage (-)', 'EndStor') for w in headers]
    headers = [w.replace('Discrepancy (=)', 'Discrepancy') for w in headers]
    headers = [w.replace('Cumulative Subsidence', 'CumSubsidence') for w in headers]

    # streams
    headers = [w.replace('Upstream Inflow (+)', 'UpstreamIn') for w in headers]
    headers = [w.replace('Downstream Outflow (-)', 'DownstreamOut') for w in headers]
    headers = [w.replace('Tributary Inflow (+)', 'TribIn') for w in headers]
    headers = [w.replace('Tile Drain (+)', 'TileDrIn') for w in headers]
    headers = [w.replace('Runoff (+)', 'Runoff') for w in headers]
    headers = [w.replace('Return Flow (+)', 'ReturnFlow') for w in headers]
    headers = [w.replace('Pond Drain (+)', 'PondDrain') for w in headers]
    headers = [w.replace('Gain from GW_Inside Model (+)', 'GWGainIn') for w in headers]
    headers = [w.replace('Gain from GW_Outside Model (+)', 'GWGainOut') for w in headers]
    headers = [w.replace('Gain from Lake (+)', 'LakeGain') for w in headers]
    headers = [w.replace('Riparian ET (-)', 'ETriparian') for w in headers]
    headers = [w.replace('Surface Evaporation (-)', 'EvapSurf') for w in headers]
    headers = [w.replace('Diversion (-)', 'Diversion') for w in headers]
    headers = [w.replace('By-pass Flow (-)', 'BypassFlow') for w in headers]
    headers = [w.replace('Discrepancy', 'Discrepancy') for w in headers]
    headers = [w.replace('Diversion Shortage', 'DivShortage') for w in headers]

    # unsaturated zone
    headers = [w.replace('Discrepancy (=)', 'Discrepancy') for w in headers]
    headers = [w.replace('Ending Storage (-)', 'EndStor') for w in headers]
    headers = [w.replace('Percolation', 'Percolation') for w in headers]
    headers = [w.replace('Deep Percolation', 'DeepPerc') for w in headers]
    headers = [w.replace('Discrepancy', 'Discrepancy') for w in headers]

    # universal
    headers = [w.replace('Time', 'Timestep') for w in headers]
    headers = [w.replace('Area (SQ FT)', 'Area_ac') for w in headers]
    headers = [w.replace('Area (Ac)', 'Area_ac') for w in headers]
    headers = [w.replace('Area (acres)', 'Area_ac') for w in headers]
    headers = [w.replace('Other Inflow (+)', 'OtherIn') for w in headers]
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
    headers = [w.replace('Percolation (+)', 'Percolation') for w in headers]
    headers = [w.replace('Deep Percolation (-)', 'DeepPerc') for w in headers]
    headers = [w.replace('Ending Storage (-)', 'EndStor') for w in headers]
    headers = [w.replace('Discrepancy (=)', 'Discrepancy') for w in headers]
    headers = [w.replace('DeepPerc (+)', 'DeepPerc') for w in headers]
    headers = [w.replace('DeepPerc (-)', 'DeepPerc') for w in headers]


    return headers

def process_budget_data(f, loc_names, column_headers, loc_values, titles, write_header=False, verbose=False):
    '''Open an IWFM Budget HDF file and retreive all of the data.

    Parameters
    ----------
    f : File object
        Output file open for writing

    loc_names : list of strings
        Location names (subregion, stream reach, stream node, small watershed etc)

    column_headers : list of lists of strings
        Column headers for each location

    loc_values : list of dataframes
        Each dataframe contains values for one location

    titles : list of tuples
        Each tuple contains the location type and the number of columns in the dataframe

    write_header : bool, default=False
        If True then print header at top of file

    verbose : bool, default=False
        Turn command-line output on or off

    Returns
    -------
    nothing
    '''
    loc_type = titles[0][1].split()[0]  # location type: 'GROUNDWATER', 'LAND' etc

    if write_header:        # format nice headers for printout
        header = 'Subregion,'+','.join([h for h in adjust_headers(column_headers[0])])
        f.write(f'{header}\n')

    for loc in range(len(loc_names)):

        # subregion and crop
        names = loc_names[loc].split()
        sr = " ".join(str(s) for s in names)
        if loc_type == 'STREAM':    sr = sr.replace('(',' (')
        values = loc_values[loc]
        vals = values.to_numpy()    # as numpy arrray, easier to convert time to string

        for row in range(vals.shape[0]):
            pv_row = []
            pv_row.append(vals[row][0].strftime('%m/%d/%Y'))    # time to string
            for i in range(1,vals.shape[1]):
                pv_row.append(str(vals[row][i]))                # values to strings
            f.write(f'{sr},{",".join([i for i in pv_row])}\n')

    return

def hdfbud2csv(bud_file, outfile, write_header=True, verbose=False):
    '''Read information from an IWFM Budget HDF file and write to a CSV file in a format amenable to database input.

    Parameters
    ----------
    bud_file : string
        Name of IWFM Budget output HDF-formatted file

    outfile : string
        Name of output CSV file

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

    budget_data = get_budget_data(bud_file, verbose=verbose)  # (loc_names, column_headers, loc_values)
    
    with open(outfile, 'w', encoding='utf-8') as f:
        process_budget_data(f, budget_data[0], budget_data[1], budget_data[2], budget_data[3],
                        write_header=write_header, verbose=verbose)


if __name__ == '__main__':
    ' Run from command line '
    import sys
    import iwfm.debug as idb
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()
 
    if len(sys.argv) > 1:  # arguments are listed on the command line
        bud_file = sys.argv[1]
        outfile  = sys.argv[2]

    else:  # ask for file names from terminal
        bud_file = input('IWFM Budget HDF file name: ')
        outfile  = input('Output file name: ')
        print('')

    idb.exe_time()  # initialize timer

    hdfbud2csv(bud_file, outfile)

    idb.exe_time()  # print elapsed time


