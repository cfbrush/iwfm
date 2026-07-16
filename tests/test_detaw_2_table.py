#!/usr/bin/env python
# test_detaw_2_table.py
# Unit tests for detaw_2_table.py
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

import pytest

from iwfm.detaw_2_table import detaw_2_table


# DETAW subarea output CSV format (e.g. Historical/SA0040.csv):
# - Row 0: column names `DATE,TYPE,UR,PA,AL,...` (crop codes)
# - Row 1: crop numbers `number,#,1,2,3,...`
# - Rows 2+: `year,year_type,val1,val2,...` — one row per year
# detaw_2_table() reads every non-hidden file in a directory (one file per
# subarea) and writes a single CSV: both header rows once, then for each year
# one row per subarea with the year replaced by (year-or-blank, subarea_number).

SA1_LINES = [
    'DATE,TYPE,UR,PA,',
    'number,#,1,2,',
    '1922,AN,39,38,',
    '1923,BN,40,45,',
]

SA2_LINES = [
    'DATE,TYPE,UR,PA,',
    'number,#,1,2,',
    '1922,AN,11,12,',
    '1923,BN,13,14,',
]


def make_detaw_dir(tmp_path, files):
    """Write dict {filename: lines} into a fresh input directory."""
    in_dir = tmp_path / 'detaw_in'
    in_dir.mkdir()
    for name, lines in files.items():
        (in_dir / name).write_text('\n'.join(lines) + '\n')
    return in_dir


def read_output_rows(outfile):
    with open(outfile, encoding='utf-8') as f:
        return [line.rstrip('\r\n') for line in f if line.strip() != '']


class TestDetaw2Table:

    def test_two_subareas_deterministic_order(self, tmp_path, monkeypatch):
        in_dir = make_detaw_dir(
            tmp_path, {'SA0001.csv': SA1_LINES, 'SA0002.csv': SA2_LINES})
        # os.listdir order is platform-dependent; pin it for exact assertions
        real_listdir = os.listdir
        monkeypatch.setattr(
            os, 'listdir', lambda d: sorted(real_listdir(d)))
        outfile = tmp_path / 'out.csv'
        detaw_2_table(str(in_dir), str(outfile))

        rows = read_output_rows(outfile)
        assert rows[0] == 'DATE,TYPE,UR,PA,'
        assert rows[1] == 'number,#,1,2,'
        # year 1922: subarea 1 carries the year, subarea 2 gets a blank
        assert rows[2] == '1922,1,AN,39,38,'
        assert rows[3] == ' ,2,AN,11,12,'
        # year 1923
        assert rows[4] == '1923,1,BN,40,45,'
        assert rows[5] == ' ,2,BN,13,14,'
        assert len(rows) == 6

    def test_single_subarea(self, tmp_path):
        in_dir = make_detaw_dir(tmp_path, {'SA0001.csv': SA1_LINES})
        outfile = tmp_path / 'out.csv'
        detaw_2_table(str(in_dir), str(outfile))

        rows = read_output_rows(outfile)
        assert rows[0] == 'DATE,TYPE,UR,PA,'
        assert rows[1] == 'number,#,1,2,'
        assert rows[2] == '1922,1,AN,39,38,'
        assert rows[3] == '1923,1,BN,40,45,'
        assert len(rows) == 4

    def test_hidden_files_skipped(self, tmp_path):
        in_dir = make_detaw_dir(
            tmp_path,
            {'SA0001.csv': SA1_LINES, '.DS_Store': ['junk,junk', 'x,y']})
        outfile = tmp_path / 'out.csv'
        detaw_2_table(str(in_dir), str(outfile))

        rows = read_output_rows(outfile)
        assert len(rows) == 4          # headers + 2 year rows, no junk
        assert 'junk' not in ''.join(rows)

    def test_year_appears_once_per_block(self, tmp_path):
        """Order-independent check: each year appears exactly once, and each
        year block contains every subarea's data row."""
        in_dir = make_detaw_dir(
            tmp_path, {'SA0001.csv': SA1_LINES, 'SA0002.csv': SA2_LINES})
        outfile = tmp_path / 'out.csv'
        detaw_2_table(str(in_dir), str(outfile))

        rows = read_output_rows(outfile)
        data_rows = rows[2:]
        years = [r.split(',')[0] for r in data_rows]
        assert years.count('1922') == 1
        assert years.count('1923') == 1
        assert years.count(' ') == 2
        # every subarea's values appear exactly once
        payloads = sorted(','.join(r.split(',')[2:]) for r in data_rows)
        assert payloads == sorted([
            'AN,39,38,', 'AN,11,12,', 'BN,40,45,', 'BN,13,14,'])

    def test_verbose_output(self, tmp_path, capsys):
        in_dir = make_detaw_dir(tmp_path, {'SA0001.csv': SA1_LINES})
        outfile = tmp_path / 'out.csv'
        detaw_2_table(str(in_dir), str(outfile), verbose=True)
        captured = capsys.readouterr()
        assert 'Read 1 files' in captured.out
        assert str(outfile) in captured.out
