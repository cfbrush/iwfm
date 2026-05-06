#!/usr/bin/env python
# test_read_nodes_csv.py
# Unit tests for read_nodes_csv.py
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

from iwfm.read_nodes_csv import read_nodes_csv


class TestReadNodesCsv:
    """Reads node CSV: header row, then `node_id,x,y` triplets. Returns
    `(node_ids, node_coord_dict)`. Stops at first row with <3 columns."""

    def test_basic(self, tmp_path):
        f = tmp_path / "nodes.csv"
        f.write_text("id,x,y\n1,100.0,200.0\n2,150.5,250.5\n3,300.0,400.0\n")
        ids, coords = read_nodes_csv(str(f))
        assert ids == [1, 2, 3]
        assert coords == {1: [100.0, 200.0], 2: [150.5, 250.5], 3: [300.0, 400.0]}

    def test_returns_tuple(self, tmp_path):
        f = tmp_path / "nodes.csv"
        f.write_text("id,x,y\n1,0,0\n")
        result = read_nodes_csv(str(f))
        assert isinstance(result, tuple) and len(result) == 2
        assert isinstance(result[0], list)
        assert isinstance(result[1], dict)

    def test_header_skipped(self, tmp_path):
        """First row is treated as header and not included in output."""
        f = tmp_path / "nodes.csv"
        f.write_text("node_id,x,y\n42,1.0,2.0\n")
        ids, coords = read_nodes_csv(str(f))
        assert ids == [42]
        assert 'node_id' not in coords

    def test_empty_data(self, tmp_path):
        """Header only, no data rows."""
        f = tmp_path / "nodes.csv"
        f.write_text("id,x,y\n")
        ids, coords = read_nodes_csv(str(f))
        assert ids == []
        assert coords == {}

    def test_stops_at_short_row(self, tmp_path):
        """Rows with <3 columns terminate parsing (treated as EOF marker)."""
        f = tmp_path / "nodes.csv"
        f.write_text("id,x,y\n1,1.0,2.0\n2,3.0,4.0\n\n5,5.0,6.0\n")
        ids, coords = read_nodes_csv(str(f))
        assert ids == [1, 2]
        assert 5 not in coords

    def test_types(self, tmp_path):
        """node_id is int; x, y are float."""
        f = tmp_path / "nodes.csv"
        f.write_text("id,x,y\n7,12.5,34.5\n")
        _, coords = read_nodes_csv(str(f))
        assert isinstance(list(coords.keys())[0], int)
        x, y = coords[7]
        assert isinstance(x, float) and isinstance(y, float)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
