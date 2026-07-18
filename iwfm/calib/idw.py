# idw.py
# Inverse-distance-weighted interpolation of per-layer nodal values to a point
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

'''Inverse-distance-weighted interpolation of per-layer nodal values to a point.'''

from iwfm.debug.logger_setup import logger


def idw(x, y, elem, nnodes, nlayers, nodexy, elevations, debug=0):
    '''Interpolate per-layer nodal values to the point (x, y) using inverse distance weighting over the nodes of the element containing the point.

    Parameters
    ----------
    x : float
        point X coordinate

    y : float
        point Y coordinate

    elem : int
        element containing the point (informational, used in log messages)

    nnodes : list of ints
        node IDs of the element's nodes; a 0 entry (triangle placeholder)
        is skipped along with its nodexy/elevations row

    nlayers : int
        number of model layers

    nodexy : list
        (x, y) coordinates of the element's nodes, same order as nnodes

    elevations : list
        per-node list of nlayers values (e.g. layer elevations), same
        order as nnodes

    debug : int, default=0, optional
        >0 = log debug information

    Returns
    -------
    interp_values : list
        nlayers values interpolated to (x, y)
    '''
    import math

    if debug:
        logger.debug(f'idw() point=({x}, {y}) {elem=} {nnodes=}')

    weights, values = [], []
    for j, node in enumerate(nnodes):
        if node == 0:  # triangle placeholder in a quad connectivity list
            continue
        d = math.hypot(x - nodexy[j][0], y - nodexy[j][1])
        if d < 1e-12:  # point coincides with a node: return its values
            return [float(elevations[j][k]) for k in range(nlayers)]
        weights.append(1.0 / d)
        values.append(elevations[j])

    wsum = sum(weights)
    interp_values = [
        sum(w * float(v[k]) for w, v in zip(weights, values)) / wsum
        for k in range(nlayers)
    ]

    if debug:
        logger.debug(f'idw() {interp_values=}')
    return interp_values
