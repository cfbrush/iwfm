# is_northern.py
# Determines if given latitude is a northern for UTM
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


def is_northern(latitude):
    '''Determine if given latitude is a northern for UTM.

    Parameters
    ----------
    latitude : float
        latitude in decimal degrees

    Returns
    -------
    True = latitude is in northern hemisphere
    False = latitude is in southern hemisphere
    '''
    return latitude >= 0.0
