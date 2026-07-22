#!/usr/bin/env python
# test_sub_rootzone_file.py
# Unit tests for sub/rootzone_file.py and sub/rz_dest_file.py
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

import iwfm
from iwfm.iwfm_dataclasses import SimulationFiles


# Rootzone main file layouts (verified against real C2VSimCG #4.13 and
# C2VSimFG #4.11 files plus the IWFM-2015.1.1443 templates):
# - 4.0/4.01: 3 factor lines (no GWUPTK); element rows end `TYPDEST DEST KPonded`
# - 4.1/4.11: 4 factor lines; inline destinations, same row tail
# - 4.12/4.13: destinations move to a separate DESTFL time-series file of
#   `date (TYPDEST,DEST) ...` pairs, one pair per element
# sub_rootzone_file() navigates the header by marker (header data lines carry
# '/ TAG' comments; element rows do not), so all 4.x layouts are handled.
# Component file entries are blank here so the component handlers are skipped.

def make_rz(tmp_path, factors, extra_header, elem_rows, name='RootZone.dat'):
    lines = ['#4.11', 'C rootzone fixture']
    lines += factors
    for tag in ('AGNPFL', 'PFL', 'URBFL', 'NVRVFL'):
        lines.append(f'                                    / {tag}')
    lines += extra_header
    lines += elem_rows
    f = tmp_path / name
    f.write_text('\n'.join(lines) + '\n')
    return f


FACTORS_4 = ['  0.01                              / RZCONV',
             '  30                                / RZITERMX',
             '  1.0                               / FACTCN',
             '  1                                 / GWUPTK']
FACTORS_3 = FACTORS_4[:3]

HEADER_411 = [f'                                    / {t}' for t in
              ('RFFL', 'RUFL', 'IPFL', 'MSRCFL', 'AGWDFL', 'LWUBUDFL',
               'RZBUDFL', 'ZLWUBUDFL', 'ZRZBUDFL', 'FNSMFL')] + [
              '  1.0                               / FACTK',
              '  1.0                               / FACTCPRISE',
              '  1MON                              / TUNITK']

# 14-column 4.11-style rows: ...IMSRC TYPDEST DEST PondedK
def row_411(e, typdest, dest):
    return (f'  {e}  0.15  0.25  0.33  0.35  0.016  1  0  1  1  0  '
            f'{typdest}  {dest}  0.01')

# 13-column 4.0-style rows: ...IMSRC TYPDEST DEST KPonded (no CPRISE column)
def row_40(e, typdest, dest):
    return (f'  {e}  0.15  0.25  0.33  0.35  0.016  1  1  1  0  '
            f'{typdest}  {dest}  0.01')


def run(tmp_path, rz_file, elems=(1, 2), snodes=(101,)):
    sim_files = SimulationFiles(root_file=str(rz_file))
    new = iwfm.new_sim_files(str(tmp_path / 'Sub'))
    iwfm.sub_rootzone_file(sim_files, new,
                           [[e, e] for e in elems], list(snodes))
    return new


def elem_lines(path):
    return [l for l in open(path).read().splitlines()
            if l.strip() and l[0] not in 'Cc*#' and '/' not in l]


class TestSubRootzone411:
    """v4.11-era: inline destinations, tail-anchored columns."""

    def test_filter_and_rewrite(self, tmp_path):
        rz = make_rz(tmp_path, FACTORS_4, HEADER_411, [
            row_411(1, 1, 101),   # stream in submodel: keep as-is
            row_411(2, 1, 999),   # stream outside: TYPDEST -> 0
            row_411(3, 1, 101),   # element outside submodel: row removed
        ])
        new = run(tmp_path, rz)
        rows = elem_lines(new.root_file)
        assert len(rows) == 2
        assert rows[0].split()[-3:] == ['1', '101', '0.01']
        assert rows[1].split()[-3:] == ['0', '999', '0.01']

    def test_non_stream_destinations_untouched(self, tmp_path):
        rz = make_rz(tmp_path, FACTORS_4, HEADER_411, [
            row_411(1, 0, 5), row_411(2, 3, 2),   # outside-model, lake
        ])
        new = run(tmp_path, rz)
        rows = elem_lines(new.root_file)
        assert rows[0].split()[-3] == '0'
        assert rows[1].split()[-3] == '3'


class TestSubRootzone40:
    """v4.0-era: 3 factor lines, 13-column rows — previously refused."""

    def test_filter_and_rewrite(self, tmp_path):
        rz = make_rz(tmp_path, FACTORS_3, HEADER_411[:8], [
            row_40(1, 1, 999), row_40(2, 2, 7), row_40(3, 1, 101),
        ])
        rz.write_text(rz.read_text().replace('#4.11', '#4.0'))
        new = run(tmp_path, rz, elems=(1, 2))
        rows = elem_lines(new.root_file)
        assert len(rows) == 2
        assert rows[0].split()[-3] == '0'      # stream 999 left submodel
        assert rows[1].split()[-3] == '2'      # element destination untouched


class TestSubRootzone413:
    """v4.12+: destinations in DESTFL; element rows carry no TYPDEST."""

    def test_destfl_extracted_and_rewritten(self, tmp_path):
        destfl = tmp_path / 'SurfFlowDest.dat'
        destfl.write_text('\n'.join([
            'C surface flow destinations',
            '      3                                      / NDSTN',
            '      1                                      / NSPDSTN',
            '      0                                      / NFQDSTN',
            ' 12/31/2100_24:00    (1,101)    (1,999)    (2,5)',
        ]) + '\n')
        header_413 = HEADER_411[:12] + [
            f'   SurfFlowDest.dat                  / DESTFL']
        rows_16col = [
            f'  {e}  0.11  0.22  0.32  0.09  0.037  0.009  1  0.5  1  1  0  313  316  317  319'
            for e in (1, 2, 3)]
        rz = make_rz(tmp_path, FACTORS_4, header_413, rows_16col)
        rz.write_text(rz.read_text().replace('#4.11', '#4.13'))

        sim_files = SimulationFiles(root_file=str(rz))
        new = iwfm.new_sim_files(str(tmp_path / 'Sub'))
        iwfm.sub_rootzone_file(sim_files, new, [[1, 1], [2, 2]], [101],
                               base_path=tmp_path)

        # main file: 2 element rows kept, untouched; DESTFL name rewritten
        rows = elem_lines(new.root_file)
        assert len(rows) == 2
        assert rows[0].split()[-4:] == ['313', '316', '317', '319']
        assert 'Sub_SurfFlowDest.dat' in open(new.root_file).read()

        # DESTFL: element 3's pair dropped; element 2's out-of-submodel
        # stream destination rewritten to outside-of-model
        dest = open(new.dest_file).read()
        assert '(1,101)' in dest
        assert '(0,0)' in dest
        assert '(2,5)' not in dest
        assert [l for l in dest.splitlines() if 'NDSTN' in l][0].split()[0] == '2'


class TestSubRzDestFile:

    def test_pair_count_mismatch_raises(self, tmp_path):
        destfl = tmp_path / 'd.dat'
        destfl.write_text('  5   / NDSTN\n  1  / NSPDSTN\n  0  / NFQDSTN\n'
                          ' 12/31/2100_24:00  (1,1)  (1,2)\n')
        with pytest.raises(ValueError, match='expected 5'):
            iwfm.sub_rz_dest_file(str(destfl), str(tmp_path / 'o.dat'),
                                  [1], [1])


class TestVersionGuard:

    def test_v5_raises(self, tmp_path):
        rz = make_rz(tmp_path, FACTORS_4, HEADER_411, [row_411(1, 1, 101)])
        rz.write_text(rz.read_text().replace('#4.11', '#5.0'))
        with pytest.raises(NotImplementedError, match="version '5.0'"):
            run(tmp_path, rz)
