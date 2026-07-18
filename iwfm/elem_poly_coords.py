# elem_poly_coords.py
# Return a list of the (x,y) coordinates for the nodes of each elememnt
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


def elem_poly_coords(elem_nodes, node_coords):
    '''Return a list of element coordinates in the form: [[x0,y0],[x1,y1],[x2,y2]<,...>].

    Parameters
    ----------
    elem_nodes : list
        list of elements and associated nodes

    node_coords : list or dictionary
        if list: [[node_id, x, y], ...]
        if dictionary: key = node_id, values = associated X and Y coordinates

    Returns
    -------
    polygons : list
        list of polygon coordinates
    '''

    # Convert node_coords to dictionary if it's a list
    if isinstance(node_coords, list):
        node_coord_dict = {int(nc[0]): (nc[1], nc[2]) for nc in node_coords}
    else:
        node_coord_dict = node_coords

    polygons = []

    for i in range(0, len(elem_nodes)):  # for each element ...
        coords = []
        for j in elem_nodes[i]:  # for each node in the element ...
            coords.append((node_coord_dict[j][0],node_coord_dict[j][1]))
        coords.append(
            (node_coord_dict[elem_nodes[i][0]][0], node_coord_dict[elem_nodes[i][0]][1])
        )  # close the polygon with the first node
        polygons.append(coords)
    return polygons
