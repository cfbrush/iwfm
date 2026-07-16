#!/usr/bin/env python
# test_iwfm_adj_crops.py
# Unit tests for iwfm_adj_crops.py
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

from iwfm.iwfm_adj_crops import iwfm_adj_crops


# iwfm_adj_crops() reads a zone file (element -> change zone), two
# change-factor files (Ag->Native, Ag->Urban; header row 'name,year,...',
# data rows 'zone,factor,...'), and three IWFM land-use area files
# (non-ponded ag with multiple crop columns, native, urban). For the
# requested year it scales each element's ag crop areas by (1 - factor)
# for the element's zone and adds the removed ag area to the native or
# urban area (column 0). Writes <base>_AG_<yr>.dat, _NV_, _UR_ via
# write_lu2file (which labels elements positionally 1..n).
#
# Land-use file format (read_lu_file, skip=4 spec lines after comments):
#   C comment
#   <4 spec lines>
#   09/30/2001_24:00  <elem>  <area> [<area> ...]
#                     <elem>  <area> [<area> ...]

LU_SPEC = ['  4  / NCROP', '  1.0  / FACTLN', '  1  / NSP', '  1  / NTS']


def make_lu_file(tmp_path, name, rows, date='09/30/2001_24:00'):
    """rows: list of (elem, [areas])."""
    lines = ['C land use fixture', 'C']
    lines.extend(LU_SPEC)
    lines.append('C end of specs')
    for n, (elem, areas) in enumerate(rows):
        prefix = date if n == 0 else ''
        lines.append(f'{prefix}\t{elem}\t' + '\t'.join(str(a) for a in areas))
    f = tmp_path / name
    f.write_text('\n'.join(lines) + '\n')
    return str(f)


def make_csv(tmp_path, name, rows):
    f = tmp_path / name
    f.write_text('\n'.join(rows) + '\n')
    return str(f)


def read_lines(path):
    with open(path, encoding='utf-8') as f:
        return [line.rstrip('\n') for line in f]


def std_inputs(tmp_path, ag_rows=None):
    """Two elements, two zones. Year 2001 factors:
    NV: zone 1 = 0.1 (ag2nv 0.9), zone 2 = 0.0
    UR: zone 1 = 0.0, zone 2 = 0.5 (ag2ur 0.5)"""
    if ag_rows is None:
        ag_rows = [(1, [100.0, 50.0]), (2, [40.0, 60.0])]
    return dict(
        in_year='2001',
        in_zone_file=make_csv(tmp_path, 'zones.csv', ['C elem,zone', '1,1', '2,2']),
        in_chg_file_NV=make_csv(
            tmp_path, 'chg_nv.csv', ['name,2000,2001', '1,0.0,0.1', '2,0.0,0.0']),
        in_chg_file_UR=make_csv(
            tmp_path, 'chg_ur.csv', ['name,2000,2001', '1,0.0,0.0', '2,0.0,0.5']),
        in_area_npag=make_lu_file(tmp_path, 'ag.dat', ag_rows),
        in_area_nvrv=make_lu_file(tmp_path, 'nv.dat', [(1, [10.0]), (2, [20.0])]),
        in_area_urban=make_lu_file(tmp_path, 'ur.dat', [(1, [5.0]), (2, [6.0])]),
        out_basename=str(tmp_path / 'out'),
    )


class TestIwfmAdjCrops:

    def test_ag_to_nv_and_ur_transfer(self, tmp_path):
        iwfm_adj_crops(**std_inputs(tmp_path))

        # elem 1 (zone 1): ag * 0.9 -> [90, 45], removed 15 -> NV
        # elem 2 (zone 2): ag * 0.5 -> [20, 30], removed 50 -> UR
        ag = read_lines(tmp_path / 'out_AG_2001.dat')
        assert ag[0] == '09/30/2001_24:00\t1\t90.0\t45.0\t'
        assert ag[1] == '\t2\t20.0\t30.0\t'

        nv = read_lines(tmp_path / 'out_NV_2001.dat')
        assert nv[0] == '09/30/2001_24:00\t1\t25.0\t'
        assert nv[1] == '\t2\t20.0\t'

        ur = read_lines(tmp_path / 'out_UR_2001.dat')
        assert ur[0] == '09/30/2001_24:00\t1\t5.0\t'
        assert ur[1] == '\t2\t56.0\t'

    def test_area_conserved(self, tmp_path):
        inputs = std_inputs(tmp_path)
        iwfm_adj_crops(**inputs)

        def row_sum(line):
            return sum(float(v) for v in line.split('\t')[2:] if v)

        ag = read_lines(tmp_path / 'out_AG_2001.dat')
        nv = read_lines(tmp_path / 'out_NV_2001.dat')
        ur = read_lines(tmp_path / 'out_UR_2001.dat')
        # initial totals per element: ag+nv+ur = 165.0 (elem 1), 126.0 (elem 2)
        assert row_sum(ag[0]) + row_sum(nv[0]) + row_sum(ur[0]) == pytest.approx(165.0)
        assert row_sum(ag[1]) + row_sum(nv[1]) + row_sum(ur[1]) == pytest.approx(126.0)

    def test_zero_factors_leave_areas_unchanged(self, tmp_path):
        inputs = std_inputs(tmp_path)
        inputs['in_chg_file_NV'] = make_csv(
            tmp_path, 'chg_nv0.csv', ['name,2000,2001', '1,0.0,0.0', '2,0.0,0.0'])
        inputs['in_chg_file_UR'] = make_csv(
            tmp_path, 'chg_ur0.csv', ['name,2000,2001', '1,0.0,0.0', '2,0.0,0.0'])
        iwfm_adj_crops(**inputs)

        ag = read_lines(tmp_path / 'out_AG_2001.dat')
        assert ag[0] == '09/30/2001_24:00\t1\t100.0\t50.0\t'
        assert ag[1] == '\t2\t40.0\t60.0\t'
        nv = read_lines(tmp_path / 'out_NV_2001.dat')
        assert nv[0].split('\t')[2] == '10.0'
        ur = read_lines(tmp_path / 'out_UR_2001.dat')
        assert ur[1].split('\t')[2] == '6.0'

    def test_zero_ag_area_not_adjusted(self, tmp_path):
        inputs = std_inputs(
            tmp_path, ag_rows=[(1, [0.0, 0.0]), (2, [40.0, 60.0])])
        iwfm_adj_crops(**inputs)

        ag = read_lines(tmp_path / 'out_AG_2001.dat')
        assert ag[0] == '09/30/2001_24:00\t1\t0.0\t0.0\t'
        nv = read_lines(tmp_path / 'out_NV_2001.dat')
        assert nv[0].split('\t')[2] == '10.0'    # NV unchanged for elem 1

    def test_element_ids_mapped_not_positional(self, tmp_path):
        """Ag file rows in reverse element order: factors must follow element
        IDs, not row positions (write_lu2file relabels rows positionally, so
        row 0 of the output holds element 2's data here)."""
        inputs = std_inputs(
            tmp_path, ag_rows=[(2, [40.0, 60.0]), (1, [100.0, 50.0])])
        iwfm_adj_crops(**inputs)

        ag = read_lines(tmp_path / 'out_AG_2001.dat')
        # row 0 = element 2 (zone 2, ag2ur 0.5); row 1 = element 1 (zone 1, ag2nv 0.9)
        assert ag[0] == '09/30/2001_24:00\t1\t20.0\t30.0\t'
        assert ag[1] == '\t2\t90.0\t45.0\t'
        nv = read_lines(tmp_path / 'out_NV_2001.dat')
        assert nv[0].split('\t')[2] == '25.0'    # NV file row 0 is element 1
        ur = read_lines(tmp_path / 'out_UR_2001.dat')
        assert ur[1].split('\t')[2] == '56.0'    # UR file row 1 is element 2

    def test_year_not_in_change_file_raises(self, tmp_path):
        inputs = std_inputs(tmp_path)
        inputs['in_year'] = '2050'
        with pytest.raises(ValueError, match='2050'):
            iwfm_adj_crops(**inputs)

    def test_existing_output_overwritten(self, tmp_path):
        (tmp_path / 'out_AG_2001.dat').write_text('stale\n')
        iwfm_adj_crops(**std_inputs(tmp_path))
        ag = read_lines(tmp_path / 'out_AG_2001.dat')
        assert ag[0].startswith('09/30/2001_24:00')
