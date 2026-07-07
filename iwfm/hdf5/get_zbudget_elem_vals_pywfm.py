# get_zbudget_elem_vals_pywfm.py
# open an IWFM ZBudget HDF file and retreive all of the data
# using DWR's PyWFM package to interface wth the IWFM DLL
# and create a dataframe with the sum of all of the values in each
# column for all elements
# DEPRECATED: Use get_zbudget_elem_vals_h5.py instead for cross-platform support
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

def get_zbudget_elem_vals(zbud, zones_file, col_ids, area_conversion_factor=0.0000229568411, area_units='ACRES', 
                        volume_conversion_factor=0.0000229568411, volume_units='ACRE-FEET', verbose=False):
    ''' get_zbudget_elem_vals() - open an IWFM ZBudget HDF file and retreive all of the data
             using DWR's PyWFM package to interface wth the IWFM DLL
             and create a dataframe with the sum of all of the values in each
             column for all elements

    Parameters
    ----------
    zbud : object
        IWFM ZBudget object (opened from HDF file)

    zones_file : str
        name of ZBudget zones file
        
    col_ids : list of ints
        Column numbers to retrieve
        
    area_conversion_factor : float, default = =0.0000229568411
        Area conversion factor

    area_units : str, default = 'ACRES'
        Area units

    volume_conversion_factor : float, default = =0.0000229568411
        Volume conversion factor

    volume_units : str, default = 'ACRE-FEET'
        Volume units

    verbose : bool, default=False
        Turn command-line output on or off

    Returns
    -------
    dates : dataframe 
        model time steps

    zone_data : numpy array
        first column is zone id, the rest are column sums from col_ids columns


    '''
    import warnings
    warnings.warn(
        "get_zbudget_elem_vals from get_zbudget_elem_vals_pywfm is deprecated. "
        "Use iwfm.hdf5.get_zbudget_elem_vals (h5py version) instead for cross-platform support.",
        DeprecationWarning,
        stacklevel=2
    )

    zbud.generate_zone_list_from_file(zone_definition_file=zones_file)

    zone_list = zbud.get_zone_list()

    zone_data, counter = [], 0
    for zone in range(0,len(zone_list)):
        zone_id = int(zone_list[zone])

        if verbose and counter >= 99:
            print(f' {zone_id:,}')
            counter = 0
        else:
            counter += 1

        zone_vals = zbud.get_values_for_a_zone(zone_id=zone_id, column_ids=col_ids, 
                        begin_date=None, end_date=None, output_interval=None, 
                        area_conversion_factor=area_conversion_factor, area_units=area_units, 
                        volume_conversion_factor=volume_conversion_factor, volume_units=volume_units)

        #retrieve col_names = ..?..

        # extract dates column to a list
        dates = zone_vals.iloc[:,0].tolist()
        zone_vals = zone_vals.drop('Time', axis=1)

        zone_sums = zone_vals.sum(axis='rows')

        this_zone_data = [zone+1]
        for col in range(0, len(col_ids)):
            this_zone_data.append(zone_sums.iloc[col])

        zone_data.append(this_zone_data)

    #zone_data = np.asarray(zone_data)

    return dates, zone_data


if __name__ == '__main__':
    ''' Run get_zbudget_elem_vals() from command line for IWFM Land and Water Use ZBudget file
        and elemental pumping'''
    import sys, os
    import pickle
    from pywfm import IWFMZBudget
    import iwfm
    import iwfm.debug as idb
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()


    if len(sys.argv) > 1:  # arguments are listed on the command line
        hdf_file   = sys.argv[1]
        zones_file = sys.argv[2]
        out_file  = sys.argv[3]
    else:  # ask for file names from terminal
        hdf_file       = input('IWFM Z-Budget file name: ')
        zones_file     = input('IWFM Z-Budget Zones file name: ')
        out_file       = input('Output file name: ')

    iwfm.file_test(hdf_file)
    iwfm.file_test(zones_file)

    idb.exe_time()  # initialize timer
    
    zbud = IWFMZBudget(hdf_file)    # open hdf file

#    col_ids = [5, 15, 25, 34]       # elemental pumping columns in IWFM Land and Water Use ZBudget HDF file
    col_ids = [9, 21]               # elemental pumping columns in IWFM Groundwater ZBudget HDF file

    dates, zone_data = get_zbudget_elem_vals(zbud, zones_file, col_ids, verbose=verbose)

    pickle_base = os.path.basename(out_file).split('.')[0]
    with open(pickle_base + '.pkl', 'wb') as f:
        pickle.dump(zone_data, f)

    with open( out_file, 'w', encoding='utf-8') as f:
#        f.write('ElemID\tNP Ag Pumping\tRice Pumping\tRefuge Pumping\tUrban Pumping\n')         # Land and Water Use
        f.write('ElemID\tElem Pumping\tWell Pumping\n')                                         # Groundwater

        for row in zone_data:
#            f.write(f'{row[0]}\t{row[1]:.2f}\t{row[2]:.2f}\t{row[3]:.2f}\t{row[4]:.2f}\n')      # Land and Water USe
            f.write(f'{row[0]}\t{row[1]:.2f}\t{row[2]:.2f}\n')                                  # Groundwater

    idb.exe_time()  # print elapsed time
