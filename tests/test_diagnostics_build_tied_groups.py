# test_diagnostics_build_tied_groups.py
# Unit tests for diagnostics/build_tied_groups.py
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

from iwfm.diagnostics.build_tied_groups import (
    build_tied_groups,
    build_stream_tied_groups,
)


class TestBuildTiedGroups:

    def test_all_nodes_assigned(self):
        """Every non-rep node should be tied to exactly one rep."""
        coords = {
            1: (0.0, 0.0),
            2: (100.0, 0.0),
            3: (200.0, 0.0),
            4: (50.0, 0.0),   # between 1 and 2
            5: (150.0, 0.0),  # between 2 and 3
        }
        reps = [1, 3]
        tied_map, groups = build_tied_groups(coords, reps)

        # Reps should not be in tied_map
        assert 1 not in tied_map
        assert 3 not in tied_map
        # All non-reps should be tied
        assert set(tied_map.keys()) == {2, 4, 5}

    def test_nearest_rep_assignment(self):
        coords = {
            1: (0.0, 0.0),
            2: (1000.0, 0.0),
            3: (10.0, 0.0),  # very close to 1
        }
        reps = [1, 2]
        tied_map, groups = build_tied_groups(coords, reps)
        assert tied_map[3] == 1  # closest to node 1

    def test_single_rep(self):
        """All nodes tied to single representative."""
        coords = {1: (0.0, 0.0), 2: (100.0, 0.0), 3: (200.0, 0.0)}
        reps = [2]
        tied_map, groups = build_tied_groups(coords, reps)
        assert tied_map[1] == 2
        assert tied_map[3] == 2
        assert len(groups[2]) == 2

    def test_groups_structure(self):
        coords = {1: (0.0, 0.0), 2: (10.0, 0.0), 3: (1000.0, 0.0)}
        reps = [1, 3]
        tied_map, groups = build_tied_groups(coords, reps)
        # Node 2 closest to node 1
        assert 2 in groups[1]
        # Both reps have entries in groups
        assert 1 in groups
        assert 3 in groups

    def test_empty_reps(self):
        coords = {1: (0.0, 0.0), 2: (10.0, 0.0)}
        reps = []
        tied_map, groups = build_tied_groups(coords, reps)
        assert tied_map == {}
        assert groups == {}


class TestBuildStreamTiedGroups:

    def test_topological_tying(self):
        """Without coords, ties by stream node ID proximity."""
        stream_ids = [1, 2, 3, 10, 11, 12, 20]
        reps = [1, 10, 20]
        tied_map, groups = build_stream_tied_groups(stream_ids, reps)
        # Node 2 closest to rep 1
        assert tied_map[2] == 1
        # Node 3 closest to rep 1
        assert tied_map[3] == 1
        # Node 11 closest to rep 10
        assert tied_map[11] == 10
        # Node 12 closest to rep 10
        assert tied_map[12] == 10

    def test_reps_not_in_tied_map(self):
        stream_ids = [1, 2, 3]
        reps = [1, 3]
        tied_map, groups = build_stream_tied_groups(stream_ids, reps)
        assert 1 not in tied_map
        assert 3 not in tied_map
        assert 2 in tied_map
