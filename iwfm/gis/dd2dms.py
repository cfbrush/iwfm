# dd2dms.py
# Converts from decimal degrees to degree-minute-second
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


'''Convert from decimal degrees to degree-minute-second.'''

def dd2dms(lat, lon):
    '''Convert lat-lon point from decimal degrees to degree-minute-second.

    Parameters
    ----------
    lat : float
        latitude in decimal degreed

    lon : float
        longitude in decimal degrees

    Returns
    -------
    lat-lon : str
        latitude and longitude in degree-minute-second format
    '''
    import math

    latf, latn = math.modf(lat)
    lonf, lonn = math.modf(lon)
    latd = int(latn)
    latm = int(latf * 60)
    lats = (lat - latd - latm / 60) * 3600.00
    lond = int(lonn)
    lonm = int(lonf * 60)
    lons = (lon - lond - lonm / 60) * 3600.00

    compass = {'lat': ('N', 'S'), 'lon': ('E', 'W')}
    lat_compass = compass['lat'][0 if latd >= 0 else 1]
    lon_compass = compass['lon'][0 if lond >= 0 else 1]

    return f'{abs(latd)}º {abs(latm)}\' {abs(lats):.2f}\" {lat_compass}, {abs(lond)}º {abs(lonm)}\' {abs(lons):.2f}\" {lon_compass}'
