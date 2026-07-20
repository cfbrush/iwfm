# geopdf_create.py
# Create a geopdf canvas
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


'''Create a geopdf canvas that can be drawn on.'''

def geopdf_create(filename):
    '''Create a geopdf canvas that can be drawn on.

    Parameters
    ----------
    filename : str
        file name to import

    Returns
    -------
    canvas : geopdf object
        geopdf from file contents


    '''
    from geopdf import GeoCanvas

    return GeoCanvas(filename)
