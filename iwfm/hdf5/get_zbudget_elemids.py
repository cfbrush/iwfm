# get_zbudget_elemids.py 
# open an IWFM ZBudget HDF file and retreive all of the data
# using DWR's PyWFM package to interface wth the IWFM DLL
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

'''Return the element IDs referenced in an IWFM Z-Budget zone definition file.'''

from iwfm.debug.logger_setup import logger


def get_zbudget_elemids(zbud, zones_file, area_conversion_factor=0.0000229568411, area_units='ACRES',
                        volume_conversion_factor=0.0000229568411, volume_units='ACRE-FEET', verbose=False):
    '''Return the element IDs referenced in an IWFM Z-Budget zone definition file.

    Parameters
    ----------
    zbud : object or None
        retained for backward compatibility; not used (element IDs come
        from the zone definition file)

    zones_file : str
        Name of IWFM Z-Budget Zones file

    area_conversion_factor : float, default = 0.0000229568411
        Area conversion factor (retained for backward compatibility)

    area_units : str, default = 'ACRES'
        Area units (retained for backward compatibility)

    volume_conversion_factor : float, default = 0.0000229568411
        Volume conversion factor (retained for backward compatibility)

    volume_units : str, default = 'ACRE-FEET'
        Volume units (retained for backward compatibility)

    verbose : bool, default=False
        Turn command-line output on or off

    Returns
    -------
    elemids : list
        sorted list of unique element IDs assigned to zones
    '''
    from iwfm.hdf5.hdf5_utils import read_zone_definition

    zextent, zone_info, element_zones = read_zone_definition(zones_file)

    if zextent == 1:
        elemids = sorted({int(e) for e in element_zones})
    else:
        elemids = sorted({int(e) for e, _layer in element_zones})

    logger.debug(f'{zones_file}: {len(zone_info)} zones, {len(elemids)} elements')
    if verbose:
        print(f'  {len(elemids)} elements in {len(zone_info)} zones from {zones_file}')

    return elemids

if __name__ == '__main__':
    ''' Run get_zbudget_elemids() from command line '''
    import sys
    import iwfm
    import iwfm.debug as idb
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    if len(sys.argv) > 1:  # arguments are listed on the command line
        zones_file = sys.argv[1]
    else:  # ask for file name from terminal
        zones_file = input('IWFM Z-Budget Zones file name: ')

    iwfm.file_test(zones_file)

    idb.exe_time()  # initialize timer

    elemids = get_zbudget_elemids(None, zones_file, verbose=True)

    print(f'  {len(elemids)} element IDs; first 10: {elemids[:10]}')

    idb.exe_time()  # print elapsed time
