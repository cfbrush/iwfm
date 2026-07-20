# bud2csv.py
# Read information from an IWFM Budget HDF file and write to a CSV file
# Currently processes any budget file, but only modifies headers to field names
# for Land and Water Use and Root Zone budget files
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



'''Open an IWFM Budget HDF file and retreive all of the data.'''

def bud2csv(f, loc_names, column_headers, loc_values, budget_info, 
                        print_header=False):
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

    budget_info : string
        Type of budget, 'GROUNDWATER' == Groundwater, 'LAND' == Lane Use,
        'STREAM' == Stream or Stream Node, 'ROOT' == Root Zone,
        'SMALL' == Small Watershed, 'UNSAT' == Unsaturates Zone

    print_header : bool, default=False
        If True then print header at top of file

    Returns
    -------
    nothing
    '''


    # determine budget type and location type
    budget_type = budget_info[0][1].split()[0]
    loc_type    = 'Subregion'       # default location type

    # modify location type for stream reach vs stream node budget
    if budget_type == 'STREAM':        # Stream reach budget or stream node budget?
        test = budget_info[0][1].split()[-2]
        if test == 'NODE':
            budget_type, loc_type = 'STREAMNODE', 'StreamNode'
        else:
            budget_type, loc_type = 'STREAMREACH', 'StreamReach'
    # modify location type for LW and RZ budgets for subregion vs crop budgets
    elif budget_type == 'LAND' or budget_type == 'ROOT': 
        test = budget_info[0][1].split()[-1][-1]      # Subregion budget or crop budget?
        if test != ')':                     # Crop budget
            loc_type  = 'Subregion,Crop'
    elif budget_type == 'SMALL':        # Small watershed budget
        loc_type = 'SmallWatershed'

    if print_header:
        # modify headers to database fields and write to file
        header = loc_type+','+','.join([h for h in column_headers[0]])
        f.write(f'{header}\n')

    for loc in range(len(loc_names)):

        # location and ID
        if loc_type == 'Subregion,Crop':
            x = loc_names[loc].find('_')
            loc_id, ID = str(loc_names[loc][:x]), str(loc_names[loc][x+1:])
        else:
            loc_id = loc_names[loc]

        values = loc_values[loc]
        vals = values.to_numpy()    # as numpy arrray, easier to convert time to string

        for row in range(vals.shape[0]):
            pv_row = []
            pv_row.append(vals[row][0].strftime('%m/%d/%Y'))    # time to string
            for i in range(1,vals.shape[1]):
                pv_row.append(str(vals[row][i]))                # values to strings
            if loc_type == 'Subregion,Crop':
                f.write(f'{loc_id},{ID},{",".join([i for i in pv_row])}\n')
            else:
                f.write(f'{loc_id},{",".join([i for i in pv_row])}\n')


