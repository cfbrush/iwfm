# map_to_nodes.py
# Create a colored image map representing nodal values such as groundwater data.
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

'''Create a colored image map representing nodal values such as groundwater data.'''

def map_to_nodes(dataset, bounding_poly, image_name, cmap='rainbow', marker_size = 10, title="Parameter values", 
                label='Z values', units='', format='tiff', verbose=False):
    '''Create a colored image map representing nodal values such as groundwater data.

    NOTE: add title, legend, etc. to plot

    Parameters
    ----------
    dataset : list of lists [[x, y, value], [x, y, value], ...
        A list containing lists of three values (x, y, value), representing the x and y coordinates of each
        data point along with their corresponding values.

    bounding_poly : shapely Polygon
        Model boundary polygon

    image_name : str
        The desired name of the image file to be saved.

    cmap : str, default = 'rainbow'
        The colormap to be used for the scatter plot.  See https://matplotlib.org/stable/tutorials/colors/colormaps.html

    marker_size : int, default = 10
        Marker size for the scatter plot.

    title : str, default = "Parameter values"
        Title for the plot.

    label : str, default = 'Z values'
        Label for the colorbar.

    units : str, default = ''
        Units for the colorbar.

    format : str, default = 'tiff'
        output file format: eps, jpeg, jpg, pdf, pgf, png, ps, raw, rgba, svg, svgz, tif, tiff, webp

    verbose : bool, default = False
        If True, print status messages.  

    Returns
    -------
    nothing
    '''
    import matplotlib.pyplot as plt
    from matplotlib.path import Path
    from matplotlib.patches import PathPatch
    import iwfm.plot as iplot

    X, Y, values = iplot.get_XYvalues(dataset)  # list of lists to numpy arrays

    path = Path(bounding_poly)
    patch = PathPatch(path, facecolor='none')
    plt.gca().patch.set_color('1')

    fig, ax = plt.subplots(figsize=(10, 8))

    # Create a scatter plot with colors representing Z values
    sp = ax.scatter(X, Y, c=values, cmap=cmap, s=marker_size) 

    ax.add_patch(patch)
    ax.set_clip_path(patch)

    fig.set_clip_path(patch)

    fig.colorbar(sp, label=f'{label} {units}', shrink=.5, fraction=0.046, pad=0.04)       # Add colorbar to show the Z values

    ax.set_title(title)             # Add a title   

    ax.axis('off')                  # Hide X axis and Y axis labels

    plt.savefig(image_name,format=format)     # Save the plot 

    #plt.show()                     # Show the plot

    plt.close()

    if verbose: print(f"  Image saved to {image_name}")

