# in_element.py
# Return number of element containing (x,y) point or 0 if none
# the nearest node to each (x,y) point
# Copyright (C) 2020-2025 University of California
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


def in_element(e_nodes, e_nos, d_nodexy, x, y):
    '''Return the element containing the point (x,y), or 0 if not in any element.

    Parameters
    ----------
    e_nodes : list
        element numbers and corresponding nodes

    e_nos : list
        element numbers

    d_nodexy : dictionary
        key=nodes, values=coordinates

    x : float
        X coordinate

    y : float
        Y coordinate

    Returns
    -------
    Integer element number of element containing point, or 0 if none
    '''
    from shapely.geometry import Polygon, Point

    point = Point(x, y)

    # brute force - cycle through all elements until contains() is true
    for i in range(0, len(e_nodes)):  
        points = []
        points.append(d_nodexy[e_nodes[i][0]])
        points.append(d_nodexy[e_nodes[i][1]])
        points.append(d_nodexy[e_nodes[i][2]])
        if len(e_nodes[i]) > 3:
            points.append(d_nodexy[e_nodes[i][3]])

        polygon = Polygon(points)

        if polygon.contains(point):
            return e_nos[i]  # if contains() is true, end and return element number
    return 0  # point is not inside any element
