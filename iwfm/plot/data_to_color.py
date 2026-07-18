# data_to_color.py 
# Map a data value to a corresponding RGB color
# Copyright (C) 2023 University of California
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

def data_to_color(value, min_value, max_value, colormap='rainbow'):
    '''Map a data value to a corresponding RGB color.

    Parameters
    ----------
    value : float
        The data value to be mapped to a color.

    min_value : float
        The minimum value of the data range.

    max_value : float
        The maximum value of the data range.

    colormap : str
        The name of the colormap to use.  The default is 'rainbow'.

    Returns
    -------
    rgb_color : tuple
        A tuple containing three integers (R, G, B) representing the RGB color components of the mapped color.
        Each component ranges from 0 to 255.
    '''
    import matplotlib as plt

    # Define a colormap
    cmap = plt.colormaps[colormap]

    # Normalize the value to the range [0, 1] based on the min and max data values
    norm_value = (value - min_value) / (max_value - min_value)

    # Map the normalized value to an RGBA color
    rgba_color = cmap(norm_value)

    # Convert RGBA (Red, Green, Blue, Alpha) to RGB (Red, Green, Blue) for PIL
    rgb_color = tuple(int(255 * x) for x in rgba_color[:3])

    return rgb_color

