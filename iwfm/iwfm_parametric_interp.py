# iwfm_parametric_interp.py
# Interpolate parametric-grid aquifer parameter values to model nodes
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

'''Interpolate parametric-grid values to target points using finite element shape functions, matching IWFM's parametric grid method: linear (barycentric) interpolation within triangles and bilinear interpolation within quadrilaterals.'''

import numpy as np


def iwfm_parametric_interp(pnode_xy, pnode_vals, pelems, targets, tol=1e-6):
    '''Interpolate parametric-grid values to target points using finite element shape functions, matching IWFM's parametric grid method: linear (barycentric) interpolation within triangles and bilinear interpolation within quadrilaterals.

    Parameters
    ----------
    pnode_xy : dict
        key = parametric node ID, value = (x, y) coordinates

    pnode_vals : dict
        key = parametric node ID, value = numpy array of shape
        (layers, nparam) with parameter values

    pelems : list
        parametric element connectivity, one entry per element as
        [n1, n2, n3, n4] node IDs; n4 = 0 for triangles

    targets : list
        (x, y) coordinates of the points to interpolate to

    tol : float, default=1e-6
        tolerance for point-in-element tests (fraction of local coordinates)

    Returns
    -------
    values : numpy array
        shape (len(targets), layers, nparam). Points outside the parametric
        grid receive the values of the nearest parametric node.
    '''
    ids = sorted(pnode_xy)
    xy = np.array([pnode_xy[i] for i in ids], dtype=float)
    layers, nparam = pnode_vals[ids[0]].shape

    # element node coordinate/value arrays and bounding boxes
    elems = []
    for e in pelems:
        enodes = [n for n in e if n > 0]
        exy = np.array([pnode_xy[n] for n in enodes], dtype=float)
        evals = np.array([pnode_vals[n] for n in enodes], dtype=float)
        bbox = (exy[:, 0].min(), exy[:, 0].max(), exy[:, 1].min(), exy[:, 1].max())
        elems.append((exy, evals, bbox))

    def tri_weights(exy, p):
        (x1, y1), (x2, y2), (x3, y3) = exy
        det = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
        if det == 0.0:
            return None
        w1 = ((y2 - y3) * (p[0] - x3) + (x3 - x2) * (p[1] - y3)) / det
        w2 = ((y3 - y1) * (p[0] - x3) + (x1 - x3) * (p[1] - y3)) / det
        w3 = 1.0 - w1 - w2
        w = np.array([w1, w2, w3])
        if np.all(w >= -tol):
            return np.clip(w, 0.0, 1.0)
        return None

    def quad_weights(exy, p):
        # Newton inversion of the bilinear isoparametric map to local
        # coordinates (xi, eta) in [-1, 1]^2
        xi = eta = 0.0
        for _ in range(15):
            n = 0.25 * np.array([(1 - xi) * (1 - eta), (1 + xi) * (1 - eta),
                                 (1 + xi) * (1 + eta), (1 - xi) * (1 + eta)])
            r = n @ exy - p
            if abs(r[0]) < 1e-9 and abs(r[1]) < 1e-9:
                break
            dn_dxi = 0.25 * np.array([-(1 - eta), (1 - eta), (1 + eta), -(1 + eta)])
            dn_deta = 0.25 * np.array([-(1 - xi), -(1 + xi), (1 + xi), (1 - xi)])
            jac = np.array([dn_dxi @ exy, dn_deta @ exy]).T
            try:
                d = np.linalg.solve(jac, r)
            except np.linalg.LinAlgError:
                return None
            xi -= d[0]
            eta -= d[1]
        if abs(xi) <= 1 + tol and abs(eta) <= 1 + tol:
            xi = min(max(xi, -1.0), 1.0)
            eta = min(max(eta, -1.0), 1.0)
            return 0.25 * np.array([(1 - xi) * (1 - eta), (1 + xi) * (1 - eta),
                                    (1 + xi) * (1 + eta), (1 - xi) * (1 + eta)])
        return None

    out = np.zeros((len(targets), layers, nparam))
    for t, p in enumerate(targets):
        p = np.asarray(p, dtype=float)
        found = False
        for exy, evals, bbox in elems:
            if not (bbox[0] - tol <= p[0] <= bbox[1] + tol
                    and bbox[2] - tol <= p[1] <= bbox[3] + tol):
                continue
            w = tri_weights(exy, p) if len(exy) == 3 else quad_weights(exy, p)
            if w is not None:
                out[t] = np.tensordot(w, evals, axes=1)
                found = True
                break
        if not found:
            # outside the parametric grid: use the nearest parametric node
            d2 = ((xy - p) ** 2).sum(axis=1)
            out[t] = pnode_vals[ids[int(np.argmin(d2))]]
    return out
