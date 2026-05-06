#!/usr/bin/env python
# test_read_lu_change_zones.py
# Unit tests for read_lu_change_zones.py
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

from iwfm.read_lu_change_zones import read_lu_change_zones


class TestReadLuChangeZones:
    """Reads a zone definition file. Comment lines start with C/c/*/# in col 0.
    Data lines: zone_id,elem_id1,elem_id2,... — all ints. Delimiter is comma,
    semicolon, asterisk, or tab.
    """

    def test_basic_comma_delimited(self, tmp_path):
        f = tmp_path / "zones.csv"
        f.write_text(" 1,10,11,12\n 2,20,21\n")
        result = read_lu_change_zones(str(f))
        assert result == [[1, 10, 11, 12], [2, 20, 21]]

    def test_skip_comment_lines(self, tmp_path):
        f = tmp_path / "zones.csv"
        f.write_text("C this is a comment\n# another\n* third style\n 1,5,6\n 2,7,8\n")
        result = read_lu_change_zones(str(f))
        assert result == [[1, 5, 6], [2, 7, 8]]

    def test_tab_delimited(self, tmp_path):
        f = tmp_path / "zones.tsv"
        f.write_text(" 1\t100\t200\n 2\t300\n")
        result = read_lu_change_zones(str(f))
        assert result == [[1, 100, 200], [2, 300]]

    def test_all_values_are_ints(self, tmp_path):
        f = tmp_path / "zones.csv"
        f.write_text(" 1,2,3\n")
        result = read_lu_change_zones(str(f))
        for row in result:
            for v in row:
                assert isinstance(v, int)

    def test_lowercase_c_comment(self, tmp_path):
        f = tmp_path / "zones.csv"
        f.write_text("c lowercase comment\n 9,1\n")
        result = read_lu_change_zones(str(f))
        assert result == [[9, 1]]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
