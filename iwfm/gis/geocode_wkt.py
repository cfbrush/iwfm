# geocode_wkt.py
# Return the lat-lon of a street address
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


'''Return the lat-lon of a street address in WKT format.'''

def geocode_wkt(address, verbose=False):
    '''Return the lat-lon of a street address in WKT format.

    Parameters
    ----------
    address : str
        street address

    verbose : bool, default=False
      Turn command-line output on or off

    Returns
    -------
    geocode of address as WKT point : str, or None if not found
    '''
    from geopy.geocoders import Nominatim

    location = Nominatim(user_agent='iwfm').geocode(address)
    if location is None:
        return None
    wkt = f'POINT ({location.longitude} {location.latitude})'
    if verbose:
        print(f'  Geocode of {address} in WKT: {wkt}')
    return wkt
