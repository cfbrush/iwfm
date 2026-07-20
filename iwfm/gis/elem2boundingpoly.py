# elem2boundingpoly.py
# Create shapely Polygon of boundary for an IWFM model
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


'''Create a shapely Polygon of the boundary of an IWFM model.'''

def elem2boundingpoly(elem_nodes, node_coords, verbose=False):
    '''Create a shapely Polygon of the boundary of an IWFM model.

    Parameters
    ----------
    elem_nodes : list
        list of elements and associated nodes

    node_coords : list
        list of nodes and associated X and Y coordinates

    verbose : bool, default=False
        True = command-line output on

    Returns
    -------
    bounding_polygon : shapely Polygon
        Model boundary polygon
    '''
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    # create dictionary of nodal coordinates
    d_nodes = {}
    for node in node_coords:
        key, values = node[0], [node[1], node[2]]
        d_nodes[key] = values


    # create a Polygon for each model element
    polys = []
    for elem in elem_nodes:  # for each element ...
        # Only include nodes that exist in d_nodes (skip missing nodes for submodels)
        points = [ [d_nodes[node][0], d_nodes[node][1]] for node in elem if node > 0 and node in d_nodes ]
        if len(points) >= 3:  # Need at least 3 points to make a polygon
            poly = Polygon([[p[0], p[1]] for p in points])
            # Only add valid polygons (skip invalid geometries)
            if poly.is_valid and not poly.is_empty:
                polys.append(poly)

    #  create poly_union
    # Handle case where no valid polygons exist
    if not polys:
        return Polygon()
    poly_union = unary_union(polys)

    # create bounding_polygon
    if poly_union.is_empty:
        bounding_polygon = Polygon()
    elif poly_union.geom_type == 'Polygon':
        bounding_polygon = Polygon(poly_union.exterior.coords)
    else:
        bounding_polygon = Polygon()
        for geom in poly_union.geoms:
            if geom.geom_type == 'Polygon':
                bounding_polygon = Polygon(geom.exterior.coords)
                break

    if verbose: print('  Created bounding polygon for model')

    return bounding_polygon    
