# test_read_factltou.py
# Tests for read_factltou and the head_divisor option of read_sim_hyd
# Copyright (C) 2020-2026 University of California
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

import numpy as np

import iwfm


def create_gw_file(filepath, factltou_line):
    '''Write a minimal groundwater-file fragment around a FACTLTOU line.'''
    lines = [
        'C   FACTLTOU  ;  Factor to convert simulation unit of groundwater heads',
        'C                 of cell centroids for velocity print-out',
        '   KernIWFM_Pumping.dat                                 / PUMPFL',
        factltou_line,
        '   FEET                                                 / UNITLTOU',
    ]
    filepath.write_text('\n'.join(lines))


def create_gw_hyd_file(filepath, data_rows, num_hydrographs):
    '''Write a minimal IWFM groundwater hydrograph output file.'''
    lines = [
        '*   ***************************************',
        '*   *       GROUNDWATER HYDROGRAPH        *',
        '*   *             (UNIT=FEET)             *',
        '*   ***************************************',
        '*          HYDROGRAPH ID' + ''.join(f'{i+1:12d}' for i in range(num_hydrographs)),
        '*                  LAYER' + ''.join(f'{1:12d}' for _ in range(num_hydrographs)),
        '*                   NODE' + ''.join(f'{0:12d}' for _ in range(num_hydrographs)),
        '*                ELEMENT' + ''.join(f'{i+1:12d}' for i in range(num_hydrographs)),
        '*        TIME',
    ]
    for date_str, values in data_rows:
        lines.append(date_str + ''.join(f'{v:12.4f}' for v in values))
    filepath.write_text('\n'.join(lines))


class TestReadFactltou:
    """Tests for the read_factltou function."""

    def test_plain_value(self, tmp_path):
        """Read a plain .dat-style FACTLTOU line."""
        gw_file = tmp_path / 'gw.dat'
        create_gw_file(gw_file, '   1                                                    / FACTLTOU')
        assert iwfm.read_factltou(str(gw_file)) == 1.0

    def test_scaled_value_with_inline_comment(self, tmp_path):
        """Read a template-style line with trailing commentary after the value."""
        gw_file = tmp_path / 'gw.tpl'
        create_gw_file(gw_file, '   1000.0 /1  increase sig digits, iwfm2obs corrects  / FACTLTOU')
        assert iwfm.read_factltou(str(gw_file)) == 1000.0

    def test_comment_lines_skipped(self, tmp_path):
        """The C-comment header mentioning FACTLTOU must not be parsed."""
        gw_file = tmp_path / 'gw.dat'
        create_gw_file(gw_file, '   10.0                                                 / FACTLTOU')
        assert iwfm.read_factltou(str(gw_file)) == 10.0

    def test_missing_file_returns_one(self, tmp_path):
        """A nonexistent file falls back to 1.0."""
        assert iwfm.read_factltou(str(tmp_path / 'no_such_file.dat')) == 1.0

    def test_no_factltou_line_returns_one(self, tmp_path):
        """A file without a non-comment FACTLTOU line falls back to 1.0."""
        gw_file = tmp_path / 'gw.dat'
        gw_file.write_text('C   FACTLTOU  ;  comment only\n   FEET   / UNITLTOU\n')
        assert iwfm.read_factltou(str(gw_file)) == 1.0


class TestReadSimHydDivisor:
    """Tests for the head_divisor option of read_sim_hyd/read_sim_hyds."""

    def test_default_unscaled(self, tmp_path):
        """Default head_divisor leaves values unchanged."""
        hyd_file = tmp_path / 'hyd.out'
        create_gw_hyd_file(hyd_file, [('09/30/1973_24:00', [100.0, 200.0])], 2)
        result = iwfm.read_sim_hyd(str(hyd_file))
        assert result[0][1] == 100.0
        assert result[0][2] == 200.0

    def test_divisor_applied(self, tmp_path):
        """head_divisor divides every value column."""
        hyd_file = tmp_path / 'hyd.out'
        create_gw_hyd_file(hyd_file, [('09/30/1973_24:00', [130367.6, 349436.0]),
                                      ('10/31/1973_24:00', [132846.4, 349342.4])], 2)
        result = iwfm.read_sim_hyd(str(hyd_file), head_divisor=1000.0)
        assert np.isclose(result[0][1], 130.3676)
        assert np.isclose(result[1][2], 349.3424)

    def test_divisor_passthrough_read_sim_hyds(self, tmp_path):
        """read_sim_hyds forwards head_divisor to read_sim_hyd."""
        hyd_file = tmp_path / 'hyd.out'
        create_gw_hyd_file(hyd_file, [('09/30/1973_24:00', [1000.0])], 1)
        result = iwfm.read_sim_hyds([str(hyd_file)], head_divisor=10.0)
        assert np.isclose(result[0][0][1], 100.0)
