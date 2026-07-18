# shp_driver_type.py
# Return shapefile driver name
# Copyright (C) 2020-2024 University of California
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


def shp_driver_type(filename, verbose=False):
    '''Return the driver.

    Parameters
    ----------
    filename : str
        Input shapefile

    verbose : bool, default=False
        turn command-line output on or off

    Returns
    -------
    d : str
        Driver
    '''
    import shapefile

    try:
        sf = shapefile.Reader(filename)
        d = 'ESRI Shapefile'  # pyshp only handles ESRI Shapefiles
        sf.close()
    except shapefile.ShapefileException:
        d = None
        
    if verbose:
        print(f'  Driver for {filename}: {d}')
    return d
