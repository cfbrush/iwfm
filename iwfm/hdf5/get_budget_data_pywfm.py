# get_budget_data_pywfm.py
# open an IWFM Budget HDF file and retreive all of the data
# using DWR's PyWFM package to interface wth the IWFM DLL
# DEPRECATED: Use get_budget_data_h5.py instead for cross-platform support
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

def get_budget_data(bud_file, 
                    area_conversion_factor = 0.0000229568411, 
                    volume_conversion_factor = 0.0000229568411, 
                    length_units="FEET",
                    area_units="ACRES",
                    volume_units="ACRE-FEET",
                    verbose=False,
                    ):
    '''Open an IWFM Budget HDF file and retreive all of the data.

    Parameters
    ----------
    bud_file : string
        Name of IWFM Budget output HDF-formatted file

    area_conversion_factor : float, default = 0.0000229568411
        Convert areas from model value to report calue
        Default: convert from square feet to acres

    volume_conversion_factor : float, default = 0.0000229568411
        Convert volumes from model value to report calue
        Default: convert from cubic feet to acre-feet

    verbose : bool, default=False
        Turn command-line output on or off

    Returns
    -------
    loc_names : list
        Location names

    column_headers : list
        Column headers for each location

    loc_values : list
        Values for each location

    titles : list
        Titles (3 items) for each location
    '''
    import warnings
    warnings.warn(
        "get_budget_data from get_budget_data_pywfm is deprecated. "
        "Use iwfm.hdf5.get_budget_data (h5py version) instead for cross-platform support.",
        DeprecationWarning,
        stacklevel=2
    )

    from pywfm import IWFMBudget
    import iwfm

    iwfm.file_test(bud_file)                        # test that input file exists
    bud = IWFMBudget(bud_file)                      # open budget HDF file
    
    # get some basic information about the file contents
    n_locs    = bud.get_n_locations()
    loc_names = bud.get_location_names()

    # retrieve everything at once
    n_data_columns, column_headers, loc_values = [], [], []
    for i in range(n_locs):
        n_data_columns.append(bud.get_n_columns(i+1))
        column_headers.append(bud.get_column_headers(i+1))
        loc_values.append(bud.get_values(i+1,
                area_conversion_factor=area_conversion_factor,
                volume_conversion_factor=volume_conversion_factor
                ))

    # get title lines for each location
    titles = []
    for loc in range(n_locs):
        titles.append(bud.get_title_lines(loc+1,
            area_conversion_factor=area_conversion_factor,
            length_units=length_units,
            area_units=area_units,
            volume_units=volume_units,
            ))

    bud.close_budget_file()

    return loc_names, column_headers, loc_values, titles
