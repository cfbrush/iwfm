# get_XYvalues.py
# Create X, Y, values vectors from a dataset
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

'''Create X, Y, values vectors from a dataset.'''

def save_plot(fig, filename):
    '''Create a colored image map representing groundwater data.

    Parameters
    ----------
    fig : matplotlib figure
        matplotlib figure to be saved

    filename : str
        name of file to be saved

    Returns
    -------
    nothing
    '''

    from PIL import Image
    from io import BytesIO


    # Save the image
    # (1) save the image in memory in PNG format
    png1 = BytesIO()
    fig.savefig(png1, format='png')

    # (2) load this image into PIL
    png2 = Image.open(png1)

    # (3) save as TIFF
    png2.save(filename)
    png2.close()
    png1.close()
    

