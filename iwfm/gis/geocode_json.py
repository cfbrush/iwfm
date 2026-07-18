# geocode_json.py
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


'''Return the lat-lon of a street address.'''

def geocode_json(address, verbose=False):
    '''Return the lat-lon of a street address as a GeoJSON FeatureCollection.

    Parameters
    ----------
    address : str
        street and city address

    verbose : bool, default=False
        True = command line output on

    Returns
    -------
    geocode of address : GeoJSON FeatureCollection dict, or None if not found
    '''
    from geopy.geocoders import Nominatim

    location = Nominatim(user_agent='iwfm').geocode(address)
    if location is None:
        return None
    feature_collection = {
        'type': 'FeatureCollection',
        'features': [{
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [location.longitude, location.latitude],
            },
            'properties': {'address': location.address},
        }],
    }
    if verbose:
        print(f'  Geocode of {address} in geojson: {feature_collection}')
    return feature_collection
