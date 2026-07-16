#!/usr/bin/env python
# test_read_sim_wells.py
# Unit tests for read_sim_wells.py
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

from iwfm.read_sim_wells import read_sim_wells


# IWFM Groundwater.dat hydrograph section (format confirmed against
# C2VSimCG_Groundwater1974.dat):
# - 20 non-comment lines (component file names, factors, output files, flags)
#   precede NOUTH; read_sim_wells() reaches it with skip_lines=20.
# - Then FACTXY and GWHYDOUTFL, then NOUTH consecutive hydrograph spec lines
#   (no comment lines between them):
#     IHYDTYP=0:  ID  HYDTYP  LAYER  X  Y  NAME
#     IHYDTYP=1:  ID  HYDTYP  LAYER  NODE  NAME   (x = y = 0.0)
# - Comment lines start with C, c, *, or # in column 1; data lines start
#   with whitespace or a digit.

FILLER_TAGS = [
    'BCFL', 'TDFL', 'PUMPFL', 'SUBSFL', 'OVRWRTFL', 'FACTLTOU', 'UNITLTOU',
    'FACTVLOU', 'UNITVLOU', 'FACTVROU', 'UNITVROU', 'VELOUTFL', 'VFLOWOUTFL',
    'GWALLOUTFL', 'HTPOUTFL', 'VTPOUTFL', 'GWBUDFL', 'ZBUDFL', 'FNGWFL',
    'IHTPFLAG',
]


def make_gw_file(tmp_path, hyd_lines, nouth=None, comment_before_specs=False):
    """Build a minimal Groundwater.dat with the 20 pre-NOUTH non-comment
    lines, the NOUTH/FACTXY/GWHYDOUTFL block, and the hydrograph spec lines."""
    if nouth is None:
        nouth = len(hyd_lines)
    lines = [
        'C IWFM Groundwater.dat test fixture',
        'C*******************************************************',
    ]
    lines.extend(f'  somevalue{i}    / {tag}' for i, tag in enumerate(FILLER_TAGS))
    lines.append('C comment between header block and NOUTH')
    lines.append(f'  {nouth}      / NOUTH')
    lines.append('  3.2808     / FACTXY')
    lines.append('  hyd.out    / GWHYDOUTFL')
    if comment_before_specs:
        lines.append('C comment before first hydrograph spec line')
        lines.append('# another comment')
    lines.extend(hyd_lines)
    f = tmp_path / 'Groundwater.dat'
    f.write_text('\n'.join(lines) + '\n')
    return str(f)


class TestReadSimWells:

    def test_ihydtyp0_xy_form(self, tmp_path):
        gw_file = make_gw_file(tmp_path, [
            '1\t0\t1\t616887\t4198677\t01n03e17e001m',
            '2\t0\t3\t651178.5\t4198961.25\t01N06E14Q003M',
        ])
        well_dict, well_list = read_sim_wells(gw_file)

        assert well_list == ['01N03E17E001M', '01N06E14Q003M']
        w1 = well_dict['01N03E17E001M']
        assert w1.column == 1
        assert w1.layer == 1
        assert w1.x == 616887.0
        assert w1.y == 4198677.0
        assert w1.name == '01n03e17e001m'
        w2 = well_dict['01N06E14Q003M']
        assert w2.column == 2
        assert w2.layer == 3
        assert w2.x == 651178.5
        assert w2.y == 4198961.25

    def test_ihydtyp1_node_form(self, tmp_path):
        gw_file = make_gw_file(tmp_path, [
            '1\t1\t2\t455\tWELL_A',
            '2\t1\t1\t871\tWELL_B',
        ])
        well_dict, well_list = read_sim_wells(gw_file)

        assert well_list == ['WELL_A', 'WELL_B']
        w = well_dict['WELL_A']
        assert w.column == 1
        assert w.layer == 2
        assert w.x == 0.0
        assert w.y == 0.0
        assert w.name == 'well_a'

    def test_mixed_hydtyp_forms(self, tmp_path):
        gw_file = make_gw_file(tmp_path, [
            '1  0  1  100.0  200.0  XYWELL',
            '2  1  2  455  NODEWELL',
        ])
        well_dict, well_list = read_sim_wells(gw_file)

        assert well_list == ['XYWELL', 'NODEWELL']
        assert well_dict['XYWELL'].x == 100.0
        assert well_dict['NODEWELL'].x == 0.0
        assert well_dict['NODEWELL'].layer == 2

    def test_nouth_zero(self, tmp_path):
        gw_file = make_gw_file(tmp_path, [], nouth=0)
        well_dict, well_list = read_sim_wells(gw_file)
        assert well_dict == {}
        assert well_list == []

    def test_comments_before_spec_lines_skipped(self, tmp_path):
        gw_file = make_gw_file(
            tmp_path, ['1\t0\t1\t10\t20\tW1'], comment_before_specs=True)
        well_dict, well_list = read_sim_wells(gw_file)
        assert well_list == ['W1']
        assert well_dict['W1'].x == 10.0

    def test_verbose_output(self, tmp_path, capsys):
        gw_file = make_gw_file(tmp_path, ['1\t0\t1\t10\t20\tW1'])
        read_sim_wells(gw_file, verbose=True)
        captured = capsys.readouterr()
        assert 'Entered read_sim_wells()' in captured.out
        assert 'Leaving read_sim_wells()' in captured.out
