#!/usr/bin/env python
# test_tables2lu.py
# Unit tests for tables2lu.py
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

from iwfm.tables2lu import tables2lu


# tables2lu() writes an IWFM land-use file: header lines, optional template
# lines (which carry the initial-acreage year), then one block per factor
# table. Factor table i produces year start_year+i+1; each block's rows are
# round(initial_acreage[r][c] * factor_tables[i][r][c], 2), first row
# prefixed 'MM/DD/YYYY_24:00\telem\t...', later rows '\telem\t...'.
# start_date is DSS-style 'MM/DD/YYYY_24:00'.

HEADER = ['C land use file header', 'C  units: acres']
TEMPLATE = ['09/30/1990_24:00\t1\t100.0\t50.0', '\t2\t200.0\t25.0']
INITIAL = [[100.0, 50.0], [200.0, 25.0]]
ELEMS = [1, 2]
START = '09/30/1990_24:00'


def read_lines(path):
    with open(path, encoding='utf-8') as f:
        return [line.rstrip('\n') for line in f]


class TestTables2Lu:

    def test_basic_two_years(self, tmp_path):
        out = tmp_path / 'lu_out.dat'
        factors = [
            [[1.0, 2.0], [0.5, 4.0]],      # -> 1991
            [[2.0, 1.0], [1.0, 2.0]],      # -> 1992
        ]
        tables2lu(HEADER, TEMPLATE, INITIAL, factors, str(out), START, ELEMS)

        lines = read_lines(out)
        assert lines[0] == 'C land use file header'
        assert lines[1] == 'C  units: acres'
        assert lines[2] == TEMPLATE[0]
        assert lines[3] == TEMPLATE[1]
        # factor table 0 -> year 1991
        assert lines[4] == '09/30/1991_24:00\t1\t100.0\t100.0'
        assert lines[5] == '\t2\t100.0\t100.0'
        # factor table 1 -> year 1992
        assert lines[6] == '09/30/1992_24:00\t1\t200.0\t50.0'
        assert lines[7] == '\t2\t200.0\t50.0'
        assert len(lines) == 8

    def test_empty_template_lines(self, tmp_path):
        out = tmp_path / 'lu_out.dat'
        factors = [[[1.0, 1.0], [1.0, 1.0]]]
        tables2lu(HEADER, [], INITIAL, factors, str(out), START, ELEMS)

        lines = read_lines(out)
        assert lines[0:2] == HEADER
        assert lines[2] == '09/30/1991_24:00\t1\t100.0\t50.0'
        assert lines[3] == '\t2\t200.0\t25.0'
        assert len(lines) == 4

    def test_values_rounded_to_two_decimals(self, tmp_path):
        out = tmp_path / 'lu_out.dat'
        factors = [[[1.111, 1.2345], [0.333, 0.6789]]]
        tables2lu(HEADER, [], INITIAL, factors, str(out), START, ELEMS)

        lines = read_lines(out)
        assert lines[2] == '09/30/1991_24:00\t1\t111.1\t61.72'
        assert lines[3] == '\t2\t66.6\t16.97'

    def test_empty_factor_tables(self, tmp_path):
        out = tmp_path / 'lu_out.dat'
        tables2lu(HEADER, TEMPLATE, INITIAL, [], str(out), START, ELEMS)

        lines = read_lines(out)
        assert lines == HEADER + TEMPLATE

    def test_unwritable_output_path_raises(self, tmp_path):
        out = tmp_path / 'no_such_dir' / 'lu_out.dat'
        with pytest.raises(OSError):
            tables2lu(HEADER, [], INITIAL, [], str(out), START, ELEMS)
