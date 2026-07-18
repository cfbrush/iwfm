# map_to_nodes_contour.py
# Create a contour map representing nodal values such as groundwater data.
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

'''Create a contour map representing nodal values such as groundwater data.'''

def map_to_nodes_contour(dataset, bounding_poly, image_name, cmap='rainbow', title="Parameter values", 
                 label='Z values', units='', no_levels=20, contour='line', format='tiff', verbose=False):
    '''Create a contour map representing nodal values such as groundwater data.

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

    title : str, default = "Parameter values"
        Title for the plot.

    label : str, default = 'Z values'
        Label for the colorbar.

    units : str, default = ''
        Units for the colorbar.

    no_levels : int, default = 20
        Number of contour levels.

    contour : str, default = 'line'
        Type of contour to be plotted.  Options are 'line' or 'filled'.

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
    from scipy.interpolate import griddata
    import numpy as np
    import iwfm.plot as iplot

    X, Y, Z = iplot.get_XYvalues(dataset)  # list of lists to numpy arrays

    # Define the contour levels
    levels = iplot.contour_levels(Z, no_levels=no_levels, verbose=verbose)

    # create a regular grid for interpolation
    ratio = (X.max() - X.min()) / (Y.max() - Y.min())
    # Use a fixed grid resolution instead of scaling by data length
    grid_res = 200  # number of points in each dimension
    xi = np.linspace(X.min(), X.max(), int(grid_res * ratio))
    yi = np.linspace(Y.min(), Y.max(), grid_res)
    Xi, Yi = np.meshgrid(xi, yi)

    # interpolate the irregular data onto the regular grid
    Zi = griddata((X, Y), Z, (Xi, Yi), method='linear')

    # Set figure size, width and height in inches
    fig, ax = plt.subplots(figsize=(10, 8))

    # create path from boundary polygon
    # Extract coordinates from shapely Polygon if needed
    if hasattr(bounding_poly, 'exterior'):
        # It's a shapely Polygon, extract coordinates
        boundary_coords = list(bounding_poly.exterior.coords)
        path = Path(boundary_coords)
    else:
        # It's already a list of coordinates
        path = Path(bounding_poly)

    # create a mask from the path
    # Ensure we're working with the correct shape from Zi (griddata output)
    points = np.column_stack((Xi.ravel(), Yi.ravel()))
    mask = path.contains_points(points).reshape(Zi.shape)

    # apply the mask to the data
    Zi = np.ma.masked_array(Zi, mask=~mask) 

    # plot the masked data
    if contour == 'filled':
        plt.contourf(Xi, Yi, Zi, levels=levels, cmap=cmap)    # filled contours
    else:
        plt.contour(Xi, Yi, Zi, levels=levels, cmap=cmap)     # contour lines

    # Add colorbar to show the Z values
    plt.colorbar(label=f'{label} {units}', shrink=.5, fraction=0.046, pad=0.04)   

    # display boundary polygon
    patch = PathPatch(path, facecolor='none')
    ax.add_patch(patch)

    ax.set_title(title)                     # Add a title   

    plt.axis('off')                         # Hide X axis and Y axis labels

    plt.savefig(image_name,format=format)   # Save the plot to a pdf file

    #plt.show()                              # Show the plot

    plt.close('all')                        # close the plot to free up memory

    if verbose: print(f"Image saved to {image_name}")

