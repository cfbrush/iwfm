# grid_shadedrelief.py
# Creates a shaded relief ASCII grid from an ASCII DEM.
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


def grid_shadedrelief(source,slopegrid,aspectgrid,shadegrid,
        az=315.0,alt=45.0,z=1.0,scale=1.0,NODATA=-9999):
    '''Create a shaded relief ASCII grid from an ASCII DEM.

    Also outputs intermediate grids for slope and aspect

    Parameters
    ----------
    source : str
        ASCII DEM file name

    slopegrid : str
        slope grid (steepness) file name

    aspectgrid : str
        aspect grid (direction faced between 0 and 360) file name

    shadegrid : str
        output file name

    az : float, default=315.0
        azimuth (sun direction) in degrees

    alt : float, default=45.0
        altitude (sun angle) in degrees

    z : float, default=1.0
        elevation exageration

    scale : float, default=1.0
        resolution

    NODATA : int, default=-9999
        value if no data

    Returns
    -------
    nothing
    '''

    import linecache
    import numpy as np

    skiprows = 6

    deg2rad = 3.141592653589793 / 180.0  # needed for numpy conversions
    rad2deg = 180.0 / 3.141592653589793
    # parse the header information from the ASCII Grid file
    hdr = [linecache.getline(source, i) for i in range(1, 7)]
    values = [float(h.split(' ')[-1].strip()) for h in hdr]
    cols, rows, lx, ly, cell, nd = values
    xres = cell
    yres = cell * -1
    arr = np.loadtxt(source, skiprows=skiprows)
    # set up 3x3 windows for smoothing, excluding 2 pixels around edges which are usually NODATA
    window = []
    for row in range(3):
        window.extend(
            arr[row : (row + arr.shape[0] - 2), col : (col + arr.shape[1] - 2)]
            for col in range(3)
        )
    # process each 3x3 window in both the x and y directions
    x = (z * (window[0] + 2 * window[3] + window[6] - window[2] - 2 * window[5] - window[8])) / (8.0 * xres * scale)
    y = (z * (window[6] + 2 * window[7] + window[8] - window[0] - 2 * window[1] - window[2])) / (8.0 * yres * scale)

    slope = 90.0 - np.arctan(np.sqrt(x * x + y * y)) * rad2deg  # calculate the slope
    aspect = np.arctan2(x, y)  # calculate the aspect

    # Calculate the shaded relief
    shaded = np.sin(alt * deg2rad) * np.sin(slope * deg2rad) + np.cos(alt * deg2rad) * np.cos(slope * deg2rad) * np.cos((az - 90.0) * deg2rad - aspect)
    shaded = shaded * 255

    # Rebuild the new header
    header =  f'ncols        {shaded.shape[1]}\n'
    header += f'nrows        {shaded.shape[0]}\n'
    header += f'xllcorner    {lx + (cell * (cols - shaded.shape[1]))}\n'
    header += f'yllcorner    {ly + (cell * (rows - shaded.shape[0]))}\n'
    header += f'cellsize     {cell}\n'
    header += f'NODATA_value {NODATA}\n'
    # Set no-data values
    for pane in window:
        slope[pane == nd] = NODATA
        aspect[pane == nd] = NODATA
        shaded[pane == nd] = NODATA

    # Open the output file, add the header, save the slope grid
    with open(slopegrid, 'wb') as f:
        f.write(bytes(header, 'UTF-8'))
        np.savetxt(f, slope, fmt='%4i')

    # Open the output file, add the header, save the aspect grid
    with open(aspectgrid, 'wb') as f:
        f.write(bytes(header, 'UTF-8'))
        np.savetxt(f, aspect, fmt='%4i')

    # Open the output file, add the header, save the shading grid
    with open(shadegrid, 'wb') as f:
        f.write(bytes(header, 'UTF-8'))
        np.savetxt(f, shaded, fmt='%4i')

    return
    