# zbudget2csv.py 
# Write IWFM ZBudget data for a set of Zones to a csv file
# For Groundwater ZBudgets, remove the inter-zone flows as these are different 
# for each zone.
# Copyright (C) 2018-2026 University of California
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


'''Write info from an IWFM ZBudget HDF file to an output file.'''

def zbudget2csv(outfile, zone_names, column_headers, zone_values, titles, zone_list, 
                         zone_extent_ids):
    '''Write info from an IWFM ZBudget HDF file to an output file.

    Parameters
    ----------
    outfile : Output file name template
        Output file name that will have zone number added to it

    zone_names : list of strings
        zone names

    column_headers : list of lists of strings
        Column headers for each zone

    zone_values : list of dataframes
        Each dataframe contains values for one zone

    titles : list
        Titles for each zone

    zone_list : string
        List of zone names

    zone_extent_ids : dictionary (retained for potential future use)
        {'horizontal': horizontal_extent_id, 'vertical': vertical_extent_id}
        horizontal_extent_id: int (0,1)
        vertical_extent_id: int (0,1)

    Returns
    -------
    nothing
    '''

    import numpy as np

    zbudget_type = titles[0][1].split()[0]    # get zbudget type from titles
    # 'GROUNDWATER', 'LAND', 'ROOT', or 'UNSATURATED''

    def first_interzone_col(names):
        # interzone flow columns are named for the neighboring zone
        # (e.g. 'Inflow from zone 2'); the column count varies by model
        for i, name in enumerate(names):
            if 'zone' in str(name).lower():
                return i
        return None

    header = column_headers[0][0]
    interzone_start = None
    if zbudget_type == 'GROUNDWATER':        # remove interzone columns, keep last 2
        interzone_start = first_interzone_col(header)
        if interzone_start is not None:
            for _ in range(interzone_start, len(header) - 2):
                header.pop(interzone_start)

    with open(outfile, 'w', encoding='utf-8') as f:
        f.write(f'ZoneNo,ZoneName,{",".join([i for i in header])}\n')   # write header to file

        for zone in range(len(zone_names)):
            vals = zone_values[zone].to_numpy()    # as numpy arrray, easier to convert time to string

            # only print some columns for GROUNDWATER
            if interzone_start is not None:        # remove interzone columns, keep last 2
                for i in range(interzone_start, vals.shape[1] - 2):
                    vals = np.delete(vals, [interzone_start], axis=1)

            for row in range(vals.shape[0]):
                pv_row = []
                pv_row.append(vals[row][0].strftime('%m/%d/%Y'))    # time to string
                for i in range(1,vals.shape[1]):
                    pv_row.append(str(vals[row][i]))                # values to strings
                f.write(f'{zone_list[zone]},{zone_names[zone]},{",".join([i for i in pv_row])}\n')

