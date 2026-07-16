# get_zbudget_data_pywfm.py
# open an IWFM ZBudget HDF file and Zones file and retreive all of the data
# using DWR's PyWFM package to interface wth the IWFM DLL
# DEPRECATED: Use get_zbudget_data_h5.py instead for cross-platform support
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

def get_zbudget_data(zbud_file, zone_file, area_units = 'ACRES', 
                    area_conversion_factor   = 0.0000229568411, volume_units = 'AC-FT', 
                    volume_conversion_factor = 0.0000229568411, 
                    logging=False, verbose=False):
    ''' get_zbudget_data() - open an IWFM Budget HDF file and retreive all of the data

    Parameters
    ----------
    zbud_file : string
        Name of IWFM ZBudget output HDF-formatted file

    zone_file : string
        Name of IWFM ZBudgetzone file

    area_conversion_factor : float, default = 0.0000229568411 Ac to ft^2
        Convert areas from model value to report calue
        Default: convert from square feet to acres

    volume_conversion_factor : float, default = 0.0000229568411 Ac to ft^2
        Convert volumes from model value to report calue
        Default: convert from cubic feet to acre-feet

    area_units : string, default = 'ACRES'
        Units for area values

    volume_units : string, default = 'AC-FT'
        Units for volume values

    logging : bool, default=False
        Turn zbudget logging on or off

    verbose : bool, default=False
        Turn command-line output on or off

    Returns
    -------
    nothing
    '''
    import warnings
    warnings.warn(
        "get_zbudget_data from get_zbudget_data_pywfm is deprecated. "
        "Use iwfm.hdf5.get_zbudget_data (h5py version) instead for cross-platform support.",
        DeprecationWarning,
        stacklevel=2
    )

    from pywfm import IWFMZBudget
    import iwfm

    iwfm.file_test(zbud_file)                          # test that input file exists
    iwfm.file_test(zone_file)                          # test that input file exists1

    zbud = IWFMZBudget(zbud_file)                      # open budget HDF file

    if logging:
        zbud.set_log_file([zone_file[:-4] + '.log'])   # set log file

    time_steps, interval = zbud.get_time_specs()       # get list of time steps and interval

    # open and read zbudget zone file
    zbud.generate_zone_list_from_file(zone_file)       # read zone file

    zone_names      = zbud.get_zone_names()            # get list of zone names
    zone_list       = zbud.get_zone_list()             # get list of zone IDs
    zone_extent_ids = zbud.get_zone_extent_ids()       # get zone extent IDs

    column_headers, zone_values, titles = [], [], []
    for zone in range(len(zone_names)):
        column_headers.append(zbud.get_column_headers_for_a_zone(zone+1,
                    area_unit=area_units,
                    volume_unit=volume_units,
                    ))
        zone_values.append(zbud.get_values_for_a_zone(zone+1,
                    area_conversion_factor=area_conversion_factor,
                    volume_conversion_factor=volume_conversion_factor,
                    area_unit=area_units,
                    volume_unit=volume_units,
                    ))
        titles.append(zbud.get_title_lines(zone+1,
                    area_conversion_factor=area_conversion_factor,
                    area_unit=area_units,
                    volume_unit=volume_units,
                    ))

    if logging:
        zbud.close_log_file()

    zbud.close_zbudget_file()
    return zone_names, column_headers, zone_values, titles, zone_list, zone_extent_ids

