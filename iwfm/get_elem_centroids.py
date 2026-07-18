# get_elem_centroids.py 
# Calculate the centroid of each element
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

def get_elem_centroids(elem_ids, elem_nodes, node_coords):
    '''Calculate the centroid of each element.

    Parameters
    ----------
    elem_ids : list
        list of element ids

    elem_nodes : list of lists
        list of nodes for each element

    node_coords : list of lists
        list of node coordinates

    Return
    ------
    elem_centroids : list of lists
        list of element centroids
    '''

    elem_centroids = []
    for elem_id, nodes in zip(elem_ids, elem_nodes):
        x = [node_coords[node-1][1] for node in nodes]
        y = [node_coords[node-1][2] for node in nodes]
        elem_centroids.append([elem_id, sum(x)/len(x), sum(y)/len(y)])

    return elem_centroids
