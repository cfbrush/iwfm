#!/usr/bin/env python
# test_dicu2table.py
# Unit tests for dicu2table.py
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

from iwfm.dicu2table import dicu2table


# DICU model file format (DSS-Vue RTS export, e.g. dicu_201712.txt):
# per data set:
#   /DICU-HIST+NODE/<site>/<KIND>/01JAN1920/1MON/DWR-BDO/   (KIND: DIV-FLOW,
#   RTS  Ver: ...                                            DRAIN-FLOW,
#   Start: ... End: ... Number: N                            SEEP-FLOW)
#   Units: CFS    Type: PER-AVER
#   31DEC1969, 2400;   0.00        <- ddMONyyyy, exactly 3 spaces before value
#   ...
#   END DATA
# file ends with a final `END FILE` line. All sets have the same length.
# dicu2table() writes <base>_divflow.csv, <base>_drainflow.csv,
# <base>_seepflow.csv via iwfm.write_flows() (site-info header rows
# transposed, then one row per date).

DATES = ['31DEC1969', '31JAN1970', '28FEB1970']


def make_set(site, kind, values):
    lines = [
        f'/DICU-HIST+NODE/{site}/{kind}/01JAN1920/1MON/DWR-BDO/',
        'RTS  Ver:  1   Prog:DssVue  LW:12NOV20  19:39:44   Tag:Tag        Prec:2',
        'Start: 01DEC1969 at 0001 hours;   End: 28FEB1970 at 2400 hours;  Number: 3',
        'Units: CFS    Type: PER-AVER',
    ]
    for date, val in zip(DATES, values):
        lines.append(f'{date}, 2400;   {val}')
    lines.append('END DATA')
    return lines


def write_dicu_file(tmp_path, sets):
    lines = []
    for site, kind, values in sets:
        lines.extend(make_set(site, kind, values))
    lines.append('END FILE')
    f = tmp_path / 'dicu_test.txt'
    f.write_text('\n'.join(lines) + '\n')
    return f


def read_csv_rows(path):
    with open(path, encoding='utf-8') as f:
        return [line.rstrip('\r\n') for line in f if line.strip() != '']


class TestDicu2Table:

    def test_all_three_flow_kinds(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        write_dicu_file(tmp_path, [
            ('1', 'DIV-FLOW', ['0.00', '1.50', '2.25']),
            ('2', 'DIV-FLOW', ['3.00', '4.50', '5.25']),
            ('1', 'DRAIN-FLOW', ['10.00', '11.00', '12.00']),
            ('1', 'SEEP-FLOW', ['20.00', '21.00', '22.00']),
        ])
        dicu2table('dicu_test.txt')

        div = read_csv_rows(tmp_path / 'dicu_test_divflow.csv')
        assert div[0] == 'ID,1,2'
        assert div[1] == 'Type,DIV-FLOW,DIV-FLOW'
        assert div[2] == 'Units,CFS,CFS'
        assert div[3] == '12/31/1969,0.00,3.00'
        assert div[4] == '01/31/1970,1.50,4.50'
        assert div[5] == '02/28/1970,2.25,5.25'
        assert len(div) == 6

        drain = read_csv_rows(tmp_path / 'dicu_test_drainflow.csv')
        assert drain[0] == 'ID,1'
        assert drain[1] == 'Type,DRAIN-FLOW'
        assert drain[3] == '12/31/1969,10.00'

        seep = read_csv_rows(tmp_path / 'dicu_test_seepflow.csv')
        assert seep[1] == 'Type,SEEP-FLOW'
        assert seep[5] == '02/28/1970,22.00'

    def test_empty_kind_writes_dates_only(self, tmp_path, monkeypatch):
        """A kind with no sets still gets a CSV: header stubs + date rows."""
        monkeypatch.chdir(tmp_path)
        write_dicu_file(tmp_path, [('1', 'DIV-FLOW', ['0.00', '1.00', '2.00'])])
        dicu2table('dicu_test.txt')

        drain = read_csv_rows(tmp_path / 'dicu_test_drainflow.csv')
        assert drain[0] == 'ID'
        assert drain[3] == '12/31/1969'

    def test_unknown_kind_raises(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        write_dicu_file(tmp_path, [('1', 'BOGUS-FLOW', ['0.00', '1.00', '2.00'])])
        with pytest.raises(ValueError, match='BOGUS-FLOW'):
            dicu2table('dicu_test.txt')

    def test_verbose_output(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        write_dicu_file(tmp_path, [('1', 'DIV-FLOW', ['0.00', '1.00', '2.00'])])
        dicu2table('dicu_test.txt', verbose=True)
        captured = capsys.readouterr()
        assert 'Creating data table from dicu_test.txt' in captured.out
        assert 'dicu_test_divflow.csv' in captured.out
