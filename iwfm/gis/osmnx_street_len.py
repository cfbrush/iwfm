# osmnx_street_len.py
# Get average street length for a city
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


'''Use OSMNX to calculate average street length for a city.'''

def osmnx_street_len(city):
    '''Use OSMNX to calculate average street length for a city.

    Parameters
    ----------
    city : str
      City name

    Return
    ------
    float:  Average street length
    '''
    import osmnx

    stats = osmnx.basic_stats(city)
    return stats['street_length_avg']
