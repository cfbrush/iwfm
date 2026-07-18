# iwfm_nearest_node.py
# Given an (x,y) location, return the nearest IWFM node
# Copyright (C) 2020-2023 University of California
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


'''Given an (x,y) location, return the nearest IWFM node.'''

def iwfm_nearest_node(point, node_set):
    '''Given an (x,y) location, return the nearest IWFM node.

    Parameters
    ----------
    point : [float,float]
        [X,Y] values of a point

    node_set : list
        node IDs and x,y locations

    Returns
    -------
    nearest_node: list
        node ID and x,y location

    nearest_distance : float
        distance between point and nearest node
    '''
    import math

    nearest_distance = 1000000000000000.0 # arbitrarily lare number
    nearest_node = -1
    for node in node_set:
        dist = math.sqrt((float(point[0]) - float(node[1])) ** 2 + 
                         (float(point[1]) - float(node[2])) ** 2)
        if dist < nearest_distance:
            nearest_node = node
            nearest_distance = dist
    return nearest_node, nearest_distance

