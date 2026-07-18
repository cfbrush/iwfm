# las2dem.py
# Converts a LIDAR LAS file to an ASCII DEM
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

'''Convert a LIDAR LAS file to an ASCII DEM.'''

import numpy as np


def las2dem(source, target, cell=1.0, NODATA=0):
    '''Convert a LIDAR LAS file to an ASCII DEM.

    Interpolation is used to account for data loss

    Parameters
    ----------
    source : str
        input LIDAR LAS file name

    target : str
        output ASCII DEM file name

    cell : float, default=1.0
        interpolation distance

    NODATA : int, default=0
        value to use for blank areas

    Return
    ------
    nothing
    '''
    import laspy

    if source[-4:] != '.las':
        source += '.las'
    if target[-4:] != '.asc':
        target += '.asc'
    las = laspy.read(source)  # Open LIDAR LAS file
    min_coords = las.header.mins  # xyz min and max
    max_coords = las.header.maxs

    xdist = max_coords[0] - min_coords[0]  # Get the x axis distance
    ydist = max_coords[1] - min_coords[1]  # Get the y axis distance
    cols = int(xdist) / cell  # Number of columns for our grid
    rows = int(ydist) / cell  # Number of rows for our grid
    cols = int(cols + 1)
    rows = int(rows + 1)

    # Track how many elevation values we aggregate
    count = np.zeros((rows, cols), dtype=float)

    zsum = np.zeros((rows, cols), dtype=float)  # Aggregate elevation values
    ycell = -1 * cell  # Y resolution is negative

    # Project x, y values to grid
    projx = (las.x - min_coords[0]) / cell
    projy = (las.y - min_coords[1]) / ycell
    # Cast to integers and clip for use as index
    ix = projx.astype(np.int32)
    iy = projy.astype(np.int32)

    # Loop through x, y, z arrays, add to grid shape, and aggregate values for averaging
    for x, y, z in np.nditer([ix, iy, las.z]):
        count[y, x] += 1
        zsum[y, x] += z

    # Change 0 values to 1 to avoid numpy warnings, and NaN values in array
    nonzero = np.where(count > 0, count, 1)

    zavg = zsum / nonzero  # Average our z values

    # Interpolate 0 values in array to avoid any holes in the grid
    mean = np.ones((rows, cols)) * np.mean(zavg)
    left = np.roll(zavg, -1, 1)
    lavg = np.where(left > 0, left, mean)
    right = np.roll(zavg, 1, 1)
    ravg = np.where(right > 0, right, mean)
    interpolate = (lavg + ravg) / 2
    fill = np.where(zavg > 0, zavg, interpolate)

    # Create our ASCII DEM header
    header =  f'ncols        {fill.shape[1]}\n'
    header += f'nrows        {fill.shape[0]}\n'
    header += f'xllcorner    {min_coords[0]}\n'
    header += f'yllcorner    {min_coords[1]}\n'
    header += f'cellsize     {cell}\n'
    header += f'NODATA_value      {NODATA}\n'

    # Open the output file, add the header, save the array
    with open(target, 'wb') as f:
        f.write(bytes(header, 'UTF-8'))
        # The fmt string ensures we output floats that have at least one number but only
        # two decimal places
        np.savetxt(f, fill, fmt='%1.2f')
    return
