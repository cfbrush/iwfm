# geocode_ex.py
# Example - finds the lat-lon of a street address and then
#     reverses to use the lat-lon to get the address information
# Copyright (C) 2020-2025 University of California
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


def geocode_ex(address, verbose=False):
    ''' geocode_ex() - example: finds the lat-lon of a street address and then
        reverses to use the lat-lon to get the address information
    
    Parameters
    ----------
    address : str
        address
    
    verbose : bool, default=False
        True = command line update on

    Returns
    -------
    result : tuple
        A tuple containing the reversed address (str) and the geocode of the address (str)

    '''
    from geopy.geocoders import Nominatim

    g = Nominatim(user_agent="geoapiExercises")
    location = g.geocode(address)
    if location is None:
        raise ValueError(f"Address '{address}' could not be geocoded.")
    
    rev = g.reverse(f'{location.latitude},{location.longitude}')
    if rev is None:
        raise ValueError(f"Coordinates '{location.latitude},{location.longitude}' could not be reverse geocoded.")
    if verbose:
        print(f'    Reversed address:  {rev.address}')
        print(f'    Geocode: {location.raw}')
    return rev, location.raw
