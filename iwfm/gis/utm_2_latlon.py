# utm_2_latlon.py
# Reproject from UTM to geographic coordinates
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


def utm_2_latlon(easting, northing, zone, band='U'):
    ''' utm_2_latlon() - Reproject from UTM to geographic coordinates

    Parameters
    ----------
    easting : float
        Easting (X) value
    
    notthing : float
        Northing (Y) value
    
    zone : int
        UTM zone
    
    band : str, default='U'
        MGRS latitude band letter; bands N-X are the northern
        hemisphere, C-M the southern

    Returns
    -------
    (lat, lon) : tuple of float
        Latitude and Longitude

    '''
    from pyproj import Transformer

    epsg = (32600 if band.upper() >= 'N' else 32700) + int(zone)
    lon, lat = Transformer.from_crs(epsg, 4326, always_xy=True).transform(easting, northing)
    return (lat, lon)
