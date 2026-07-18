# map.py
# Create a colored image map representing groundwater data.
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

'''Create a colored image map representing groundwater data.'''

def map(dataset, image_name, scaling_factor = 0.01 , point_type='polygon', point_width=100, verbose=False):
    '''Create a colored image map representing groundwater data.

    NOTE: add title, legend, etc. to plot

    Parameters
    ----------
    dataset : list of tuples
        A list containing tuples of three values (x, y, value), representing the x and y coordinates of each
        data point along with their corresponding values.

    image_name : str
        The desired name of the image file to be saved.

    scaling_factor : float, default = 0.01
        The scaling factor to be applied to the x and y coordinates.  The default is 0.01.
        This determines the size of the image.  The value can be adjusted based on the data range
        to produce a more useful image.

    point_type : str, default = 'polygon'
        The type of shape to be drawn around each data point.  
        The other option is 'circle'.

    point_width : int, default = 100
        The width of the polygon or diameter of the circle to be drawn around each data point.

    verbose : bool, default = False
        If True, print status messages.  

    Returns
    -------
    nothing
    '''
    from PIL import Image, ImageDraw
    import iwfm.plot as iplot

    #  Find min and max values
    min_x, min_y, min_value = iplot.get_mins(dataset)
    max_x, max_y, max_value = iplot.get_maxs(dataset)

    # Calculate the range of x and y values
    range_x = max_x - min_x
    range_y = max_y - min_y
   

    # Create a new image with a white background for the main plot
    image_width  = int(range_x * scaling_factor) + 200
    image_height = int(range_y * scaling_factor) + 200
    image = Image.new('RGB', (image_width, image_height), color='white')

    # Create a drawing context for the main plot
    draw = ImageDraw.Draw(image)

    # Scale the coordinates to fit within the image size
    def scale_x(x):
        return int((x - min_x) * scaling_factor) + 100

    def scale_y(y):
        return int((y - min_y) * scaling_factor) + 100


    # Draw a polygon or circle around each data point
    for x, y, value in dataset:
        norm_value = (value) / (max_value)
        color = iplot.data_to_color(norm_value * (max_value) + min_value, min_value, max_value)
        scaled_x = scale_x(x)
        scaled_y = scale_y(y)

        if point_type == 'circle':
            # Define the vertices of a circle
            c_vertices = [
                (scaled_x - point_width/4),
                (scaled_y - point_width/4),
                (scaled_x + point_width/4),
                (scaled_y + point_width/4)
            ]
            # Draw the circle
            draw.ellipse(c_vertices, fill=color, outline=color)
        else:
            # Define the vertices of the polygon
            p_vertices = [
                (scaled_x - point_width/2, scaled_y),
                (scaled_x, scaled_y - point_width/2),
                (scaled_x + point_width/2, scaled_y),
                (scaled_x, scaled_y + point_width/2)
            ]
            # Draw the polygon
            draw.polygon(p_vertices, fill=color, outline=color)

    # Save the image
    image.save(image_name)

    if verbose: print(f"Image of groundwater data saved to {image_name}")

