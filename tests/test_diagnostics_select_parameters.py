# test_diagnostics_select_parameters.py
# Unit tests for diagnostics/select_parameters.py
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

import pytest

from iwfm.diagnostics.select_parameters import select_parameters


class TestSelectParameters:

    def _grid_coords(self, nx=10, ny=10, spacing=1000.0):
        """Create a regular grid of node coordinates."""
        coords = {}
        nid = 1
        for j in range(ny):
            for i in range(nx):
                coords[nid] = (i * spacing, j * spacing)
                nid += 1
        return coords

    def test_returns_correct_count(self):
        coords = self._grid_coords(10, 10)
        n_reps = 5
        selected, scores = select_parameters(coords, n_reps)
        assert len(selected) == n_reps

    def test_all_nodes_if_n_reps_exceeds(self):
        coords = {1: (0.0, 0.0), 2: (100.0, 0.0), 3: (200.0, 0.0)}
        selected, scores = select_parameters(coords, n_reps=10)
        assert len(selected) == 3

    def test_selected_are_node_ids(self):
        coords = self._grid_coords(5, 5)
        selected, scores = select_parameters(coords, n_reps=3)
        for nid in selected:
            assert nid in coords

    def test_spatial_spread(self):
        """Selected nodes should be spatially distributed."""
        coords = self._grid_coords(10, 10, spacing=1000.0)
        selected, scores = select_parameters(coords, n_reps=4)
        # At least some spread — not all in same corner
        xs = [coords[nid][0] for nid in selected]
        ys = [coords[nid][1] for nid in selected]
        assert max(xs) - min(xs) > 2000.0
        assert max(ys) - min(ys) > 2000.0

    def test_candidate_nodes_restricts(self):
        coords = self._grid_coords(10, 10)
        candidates = {1, 2, 3, 4, 5}
        selected, scores = select_parameters(
            coords, n_reps=3, candidate_nodes=candidates)
        for nid in selected:
            assert nid in candidates

    def test_sensitivity_influences_selection(self):
        """High-sensitivity nodes should be preferred."""
        coords = {
            1: (0.0, 0.0),
            2: (5000.0, 0.0),
            3: (10000.0, 0.0),
            4: (15000.0, 0.0),
        }
        # Only node 2 has high sensitivity
        sensitivity = {
            'PKH001_L1': {'sensitivity': 0.01},
            'PKH002_L1': {'sensitivity': 100.0},
            'PKH003_L1': {'sensitivity': 0.01},
            'PKH004_L1': {'sensitivity': 0.01},
        }
        selected, scores = select_parameters(
            coords, n_reps=1, sensitivity=sensitivity,
            param_prefix='PKH', layer=1, diagnostic_weight=0.0)
        assert selected[0] == 2

    def test_scores_dict_structure(self):
        coords = self._grid_coords(5, 5)
        selected, scores = select_parameters(coords, n_reps=3)
        for nid in selected:
            assert nid in scores
            s = scores[nid]
            assert 'sensitivity' in s or 'combined' in s
