# bnds2mask.py
# Bounding polygon for IWFM mmodel
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

def bnds2mask(bnds_d, coords):
    ''' bnds2mask() - Bounding polygon for IWFM mmodel

    Parameters
    ----------
    bnds_d : dictionary
        Boundry elements and order along boundary 

    elem_nodes : list
        List of elements and associated nodes

    coords : list [[node_id, x, y], ...]
        Nodal coordinates

    Returns
    -------
    Bounding polygon as numpy array of x,y coordinates
    '''
    import sys
    coords_d = dict( (c[0], c[1:]) for c in coords)

    xy = []
    for i in range(len(bnds_d)):    # march down the list of boundary nodes
        node = bnds_d[i]
        try:
            xy.append((coords_d[node][0],coords_d[node][1])) 
        except KeyError:
            from iwfm.debug.logger_setup import logger
            logger.error(f'Invalid node number {bnds_d[i]} in boundary list')
            sys.exit(1)
    node = bnds_d[0]                # close the polygon
    xy.append((coords_d[node][0],coords_d[node][1])) 
    return xy                             # create numpy array of coordinates

