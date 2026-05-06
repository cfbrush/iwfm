#!/usr/bin/env python
# test_read_lu_change_factors.py
# Unit tests for read_lu_change_factors.py
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

from iwfm.read_lu_change_factors import read_lu_change_factors


class TestReadLuChangeFactors:
    """Reads a land-use change-factors file. Format:
    - Row 0: header `name,landuse_type_id1,landuse_type_id2,...` — ints after col 0.
    - Subsequent rows: `zone_id,factor1,factor2,...` — int zone, float factors.
    Delimiter is `,`, `;`, `*`, `\\n`, or tab.
    """

    def test_basic_comma_delimited(self, tmp_path):
        f = tmp_path / "chg.csv"
        f.write_text("zone,1,2,3\n10,0.5,1.0,1.5\n20,0.25,0.75,1.25\n")
        result = read_lu_change_factors(str(f))
        assert result[0] == ['zone', 1, 2, 3]
        assert result[1] == [10, 0.5, 1.0, 1.5]
        assert result[2] == [20, 0.25, 0.75, 1.25]

    def test_tab_delimited(self, tmp_path):
        f = tmp_path / "chg.tsv"
        f.write_text("zone\t1\t2\n10\t0.5\t0.5\n")
        result = read_lu_change_factors(str(f))
        assert result == [['zone', 1, 2], [10, 0.5, 0.5]]

    def test_semicolon_delimited(self, tmp_path):
        f = tmp_path / "chg.txt"
        f.write_text("zone;5;6\n1;1.0;2.0\n")
        result = read_lu_change_factors(str(f))
        assert result == [['zone', 5, 6], [1, 1.0, 2.0]]

    def test_data_rows_floats(self, tmp_path):
        """Data rows after row 0 have int zone and float factors."""
        f = tmp_path / "chg.csv"
        f.write_text("z,1\n42,1.5\n")
        result = read_lu_change_factors(str(f))
        assert isinstance(result[1][0], int)
        assert isinstance(result[1][1], float)

    def test_missing_file_raises(self):
        """iwfm.file_test() exits the process when the path does not exist."""
        with pytest.raises((FileNotFoundError, SystemExit)):
            read_lu_change_factors("/nonexistent/path/__nope__.csv")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
