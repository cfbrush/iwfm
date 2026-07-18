# geocode.py
# Return the lat-lon of a street address
# Copyright (C) 2020-2021 University of California
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


def geocode(address, verbose=True):
    '''Return the lat-lon of a street address.

    Parameters
    ----------
    address : str
        street address

    verbose : bool, sefault=True
        turn command-line output on or off




    '''
    from geopy.geocoders import Nominatim

    g = Nominatim()
    location = g.geocode(address)
    if verbose:
        print(f'  Geocoding: \'{address}\' to \'{location}\'')
    return location
