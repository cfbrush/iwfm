# test_iwfm_parametric_interp.py
# Unit tests for parametric-grid interpolation to model nodes
# Copyright (C) 2026 University of California
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

import os
import tempfile

import numpy as np
import pytest

from iwfm.iwfm_parametric_interp import iwfm_parametric_interp


def _unit_square():
    """4 parametric nodes on the unit square, 1 layer, 1 parameter."""
    pnode_xy = {1: (0.0, 0.0), 2: (1.0, 0.0), 3: (1.0, 1.0), 4: (0.0, 1.0)}
    pnode_vals = {1: np.array([[10.0]]), 2: np.array([[20.0]]),
                  3: np.array([[30.0]]), 4: np.array([[40.0]])}
    pelems = [[1, 2, 3, 4]]
    return pnode_xy, pnode_vals, pelems


class TestQuadInterpolation:
    def test_exact_at_corners(self):
        pnode_xy, pnode_vals, pelems = _unit_square()
        out = iwfm_parametric_interp(pnode_xy, pnode_vals, pelems,
                                     [(0.0, 0.0), (1.0, 1.0)])
        assert out[0, 0, 0] == pytest.approx(10.0)
        assert out[1, 0, 0] == pytest.approx(30.0)

    def test_bilinear_at_center(self):
        pnode_xy, pnode_vals, pelems = _unit_square()
        out = iwfm_parametric_interp(pnode_xy, pnode_vals, pelems, [(0.5, 0.5)])
        assert out[0, 0, 0] == pytest.approx(25.0)  # mean of 10, 20, 30, 40

    def test_edge_midpoint(self):
        pnode_xy, pnode_vals, pelems = _unit_square()
        out = iwfm_parametric_interp(pnode_xy, pnode_vals, pelems, [(0.5, 0.0)])
        assert out[0, 0, 0] == pytest.approx(15.0)  # mean of 10, 20

    def test_outside_uses_nearest_node(self):
        pnode_xy, pnode_vals, pelems = _unit_square()
        out = iwfm_parametric_interp(pnode_xy, pnode_vals, pelems, [(5.0, 5.0)])
        assert out[0, 0, 0] == pytest.approx(30.0)  # nearest is node 3 at (1,1)


class TestTriangleInterpolation:
    def test_barycentric(self):
        pnode_xy = {1: (0.0, 0.0), 2: (2.0, 0.0), 3: (0.0, 2.0)}
        pnode_vals = {1: np.array([[3.0]]), 2: np.array([[6.0]]), 3: np.array([[9.0]])}
        pelems = [[1, 2, 3, 0]]  # trailing 0 marks a triangle
        out = iwfm_parametric_interp(pnode_xy, pnode_vals, pelems,
                                     [(0.0, 0.0), (2/3, 2/3)])
        assert out[0, 0, 0] == pytest.approx(3.0)
        assert out[1, 0, 0] == pytest.approx(6.0)  # centroid = mean(3, 6, 9)

    def test_multiple_layers_and_params(self):
        pnode_xy = {1: (0.0, 0.0), 2: (2.0, 0.0), 3: (0.0, 2.0)}
        # 2 layers x 5 params
        pnode_vals = {i: np.full((2, 5), float(i)) for i in (1, 2, 3)}
        pelems = [[1, 2, 3, 0]]
        out = iwfm_parametric_interp(pnode_xy, pnode_vals, pelems, [(2/3, 2/3)])
        assert out.shape == (1, 2, 5)
        assert np.allclose(out, 2.0)  # centroid = mean(1, 2, 3)


class TestReadGwParametric:
    def _gw_content(self):
        content = "#4.0\n"
        content += "C IWFM Groundwater File (parametric interp test)\n"
        content += "   BC.dat                       / BCFL\n"
        content += "   /                            / TDFL\n"
        content += "   /                            / PUMPFL\n"
        content += "   /                            / SUBSFL\n"
        content += "                                / OVRWRTFL\n"
        content += "   1                            / FACTLTOU\n"
        content += "   FEET                         / UNITLTOU\n"
        content += "   0.000022957                  / FACTVLOU\n"
        content += "   ACRE-FEET                    / UNITVLOU\n"
        content += "   0.000022957                  / FACTVROU\n"
        content += "   AC-FT/MON                    / UNITVROU\n"
        content += "                                / VELOUTFL\n"
        content += "                                / VFLOWOUTFL\n"
        content += "   headall.out                  / GWALLOUTFL\n"
        content += "                                / HTPOUTFL\n"
        content += "                                / VTPOUTFL\n"
        content += "                                / GWBUDFL\n"
        content += "                                / ZBUDFL\n"
        content += "                                / FNGWFL\n"
        content += "      1                         / KDEB\n"
        content += "     1                          / NOUTH\n"
        content += "     1.0                        / FACTXY\n"
        content += "     hydrographs.out            / GWHYDOUTFL\n"
        content += "1  0  1  100.0  200.0  Well1\n"
        content += "     0                          / NOUTF\n"
        content += "                                / GWFFLOUTFL\n"
        content += "          1                     / NGROUP\n"
        content += "   1.0  1.0  1.0  1.0  1.0  1.0 / FACT\n"
        content += "    1DAY               / TUNITKH\n"
        content += "    1DAY               / TUNITV\n"
        content += "    1DAY               / TUNITL\n"
        content += "   1-2                          / node range\n"
        content += "   4                            / NDP\n"
        content += "   1                            / NEP\n"
        content += "   1  1  2  3  4\n"
        content += "C separator\n"
        content += "   1  0.0  0.0  10.0  0.0001  0.15  1.0  0.1\n"
        content += "   2  1.0  0.0  20.0  0.0002  0.16  1.1  0.2\n"
        content += "   3  1.0  1.0  30.0  0.0003  0.17  1.2  0.3\n"
        content += "   4  0.0  1.0  40.0  0.0004  0.18  1.3  0.4\n"
        content += "   0                            / NEBK\n"
        content += "   1.0                          / FACT\n"
        content += "   1MON                         / TUNITH\n"
        content += "   1.0                          / FACTHP\n"
        content += "1  100.0\n"
        content += "2  101.0\n"
        return content

    def test_interpolates_with_node_coords(self):
        from iwfm.iwfm_read_gw import iwfm_read_gw

        fd, temp_file = tempfile.mkstemp(suffix='.dat')
        os.close(fd)
        try:
            with open(temp_file, 'w') as f:
                f.write(self._gw_content())

            # model node 1 at parametric node 1 (exact), node 2 at cell center
            coords = [[1, 0.0, 0.0], [2, 0.5, 0.5]]
            (_, node_id, layers, Kh, Ss, Sy, Kq, Kv, init_cond,
             units, hyds, factxy) = iwfm_read_gw(temp_file, node_coords=coords)

            assert layers == 1
            assert len(Kh) == 2
            assert Kh[0][0] == pytest.approx(10.0)   # exact at parametric node 1
            assert Kh[1][0] == pytest.approx(25.0)   # bilinear center
            assert Sy[1][0] == pytest.approx(0.165)  # mean of 0.15..0.18
            assert Kv[0][0] == pytest.approx(0.1)
        finally:
            os.unlink(temp_file)

    def test_no_coords_returns_empty(self):
        from iwfm.iwfm_read_gw import iwfm_read_gw

        fd, temp_file = tempfile.mkstemp(suffix='.dat')
        os.close(fd)
        try:
            with open(temp_file, 'w') as f:
                f.write(self._gw_content())

            result = iwfm_read_gw(temp_file)
            Kh = result[3]
            assert Kh == []
        finally:
            os.unlink(temp_file)

    def test_missing_coordinate_raises(self):
        from iwfm.iwfm_read_gw import iwfm_read_gw

        fd, temp_file = tempfile.mkstemp(suffix='.dat')
        os.close(fd)
        try:
            with open(temp_file, 'w') as f:
                f.write(self._gw_content())

            with pytest.raises(ValueError, match='without coordinates'):
                iwfm_read_gw(temp_file, node_coords=[[1, 0.0, 0.0]])  # node 2 missing
        finally:
            os.unlink(temp_file)
