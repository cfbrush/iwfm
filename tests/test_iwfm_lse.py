#!/usr/bin/env python
# test_iwfm_lse.py
# Unit tests for iwfm_lse.py
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

from iwfm.iwfm_lse import iwfm_lse


class TestIwfmLse:
    """Tests for iwfm_lse() — extract [node_no, lse] pairs from a stratigraphy
    list. Each strat row is `[node_no, lse, layer1_thick, ...]`; this returns
    just the first two elements.
    """

    def test_typical_three_nodes(self):
        """Each strat row's first two values are returned as the LSE pair."""
        strat = [
            [1, 100.0, 50.0, 200.0],
            [2, 110.0, 55.0, 210.0],
            [3, 105.0, 52.0, 205.0],
        ]
        result = iwfm_lse(strat)
        assert result == [[1, 100.0], [2, 110.0], [3, 105.0]]

    def test_preserves_order(self):
        """Output order matches input order even with non-sequential node IDs."""
        strat = [
            [42, 200.0, 1.0],
            [7, 100.0, 1.0],
            [99, 300.0, 1.0],
        ]
        result = iwfm_lse(strat)
        assert [row[0] for row in result] == [42, 7, 99]
        assert [row[1] for row in result] == [200.0, 100.0, 300.0]

    def test_single_node(self):
        """Single-row strat returns a single-row LSE list."""
        result = iwfm_lse([[1, 50.0, 25.0]])
        assert result == [[1, 50.0]]

    def test_empty_strat(self):
        """Empty input yields empty output (no error)."""
        assert iwfm_lse([]) == []

    def test_doesnt_share_inner_list_with_input(self):
        """Returned LSE pairs are fresh lists, so caller can mutate them safely."""
        strat = [[1, 100.0, 50.0]]
        result = iwfm_lse(strat)
        result[0][1] = 999.0
        # Original strat unchanged
        assert strat[0][1] == 100.0

    def test_returned_pair_length(self):
        """Each returned row has exactly 2 elements."""
        strat = [[i, float(i * 10), 1.0, 2.0, 3.0] for i in range(1, 6)]
        result = iwfm_lse(strat)
        for row in result:
            assert len(row) == 2

    def test_exposed_via_iwfm_namespace(self):
        """iwfm_lse is re-exported from iwfm/__init__.py."""
        import iwfm
        assert iwfm.iwfm_lse is iwfm_lse


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
