# iwfm_boundary_coords.py
# Return (x,y) list for the nodes on the bounding polygon
# Copyright (C) 2020-2026 University of California
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


'''Return (x,y) list for the nodes on the bounding polygon.'''

def iwfm_boundary_coords(node_filename, elem_filename):
    '''Return (x,y) list for the nodes on the bounding polygon.

    Parameters
    ----------
    nose_filename : str
        Path to node file

    elem_filename : str
        Path to elelment file


    Returns
    -------
    centroids : list
        (x,y) list for the nodes on the bounding polygon
    '''
    import iwfm
    import iwfm.gis as igis

    node_coords, node_list, factor = iwfm.iwfm_read_nodes(node_filename)

    elem_ids, elem_nodes, elem_sub = iwfm.iwfm_read_elements(elem_filename)
    
    boundary_coords = igis.get_boundary_coords(elem_nodes, node_coords)

    return boundary_coords
