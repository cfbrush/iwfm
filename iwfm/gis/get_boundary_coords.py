# get_boundary_coords.py 
# Use elem_nodes and node_coords to get (x,y) list for the nodes 
# on the bounding polygon
# Copyright (C) 2023-2024 University of California
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

'''Use elem_nodes and node_coords to get (x,y) list for the nodes on the bounding polygon.'''

def get_boundary_coords(elem_nodes, node_coords):
    '''Get (x,y) list for the nodes on the bounding polygon.

    Parameters
    ----------
    elem_nodes : list of lists
        list of nodes for each element

    node_coords : list of lists
        list of node coordinates

    Return
    ------
    boundary_coords : list of tuples
        bounding coordinates for the model
    '''

    from shapely.geometry import mapping
    import iwfm.gis as igis


    # create a bounding polygon shape from the element nodes and node coordinates
    model_boundary = igis.elem2boundingpoly(elem_nodes, node_coords)

    # map the bounding polygon to a dictionary
    mapped_boundary = mapping(model_boundary)

    # extract the coordinates from the dictionary
    boundary_coords = mapped_boundary['coordinates'][0]

    return boundary_coords
