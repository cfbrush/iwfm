#!/usr/bin/env python
# test_iwfm_lu4scenario.py
# Unit tests for iwfm_lu4scenario.py
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

from iwfm.iwfm_lu4scenario import iwfm_lu4scenario


# iwfm_lu4scenario() merges four single-date IWFM land use files (non-ponded
# ag, ponded ag, urban, native/riparian) into one combined table keyed by
# element ID and writes <base>_Landuse.dat. Column counts per file are
# parameters (defaults = C2VSim: 20 non-ponded, 5 ponded, 2 NV/RV, 1 urban).
# Values are kept as strings (input formatting preserved). Input files need
# not list elements in the same order, but must contain the same IDs.

DATE = '09/30/2001_24:00'
LU_SPEC = ['  4  / NCROP', '  1.0  / FACTLN', '  1  / NSP', '  1  / NTS']


def make_lu_file(tmp_path, name, rows, dates=None):
    """rows: list of (elem, [str values]). dates: one date per data block
    (multiple dates only used to test the multi-date error)."""
    dates = dates or [DATE]
    lines = ['C land use fixture', 'C']
    lines.extend(LU_SPEC)
    lines.append('C end of specs')
    for date in dates:
        for n, (elem, vals) in enumerate(rows):
            prefix = date if n == 0 else ''
            lines.append(f'{prefix}\t{elem}\t' + '\t'.join(vals))
    f = tmp_path / name
    f.write_text('\n'.join(lines) + '\n')
    return str(f)


def vals(start, n):
    """n distinct integer-string values starting at start."""
    return [str(start + i) for i in range(n)]


def std_inputs(tmp_path, **file_rows):
    """Build the four input files. file_rows keys: npag, pag, urb, nvrv."""
    rows = {
        'npag': [(1, vals(100, 20)), (2, vals(200, 20))],
        'pag': [(1, vals(300, 5)), (2, vals(400, 5))],
        'urb': [(1, ['7']), (2, ['8'])],
        'nvrv': [(1, ['50', '51']), (2, ['60', '61'])],
    }
    rows.update(file_rows)
    return dict(
        out_base_name=str(tmp_path / 'scen'),
        in_npag_file=make_lu_file(tmp_path, 'npag.dat', rows['npag']),
        in_ponded_file=make_lu_file(tmp_path, 'pag.dat', rows['pag']),
        in_urban_file=make_lu_file(tmp_path, 'urb.dat', rows['urb']),
        in_nvrv_file=make_lu_file(tmp_path, 'nvrv.dat', rows['nvrv']),
    )


def read_lines(path):
    with open(path, encoding='utf-8') as f:
        return [line.rstrip('\n') for line in f]


class TestIwfmLu4Scenario:

    def test_default_c2vsim_shape(self, tmp_path):
        iwfm_lu4scenario(**std_inputs(tmp_path))

        lines = read_lines(tmp_path / 'scen_Landuse.dat')
        assert lines[0] == f'# Date: {DATE}'
        expected_header = (
            '# Elem\t'
            + '\t'.join(f'NPA{i}' for i in range(1, 21)) + '\t'
            + '\t'.join(f'PA{i}' for i in range(1, 6))
            + '\tNV\tRV\tUrb'
        )
        assert lines[1] == expected_header
        # values preserved as strings, order: npag, pag, nvrv, urb
        assert lines[2] == '\t'.join(
            ['1'] + vals(100, 20) + vals(300, 5) + ['50', '51', '7'])
        assert lines[3] == '\t'.join(
            ['2'] + vals(200, 20) + vals(400, 5) + ['60', '61', '8'])
        assert len(lines) == 4

    def test_custom_column_counts(self, tmp_path):
        inputs = std_inputs(
            tmp_path,
            npag=[(1, ['10', '11', '12'])],
            pag=[(1, ['20', '21'])],
            urb=[(1, ['30', '31'])],
            nvrv=[(1, ['40'])],
        )
        iwfm_lu4scenario(
            **inputs, npag_cols=3, pag_cols=2, nvrv_cols=1, urban_cols=2)

        lines = read_lines(tmp_path / 'scen_Landuse.dat')
        assert lines[1] == '# Elem\tNPA1\tNPA2\tNPA3\tPA1\tPA2\tNVRV1\tUrb1\tUrb2'
        assert lines[2] == '1\t10\t11\t12\t20\t21\t40\t30\t31'

    def test_extra_columns_trimmed(self, tmp_path):
        inputs = std_inputs(
            tmp_path,
            npag=[(1, ['10', '11', '12', '99'])],   # 4th value ignored
            pag=[(1, ['20'])],
            urb=[(1, ['30'])],
            nvrv=[(1, ['40'])],
        )
        iwfm_lu4scenario(
            **inputs, npag_cols=3, pag_cols=1, nvrv_cols=1, urban_cols=1)

        lines = read_lines(tmp_path / 'scen_Landuse.dat')
        assert lines[2] == '1\t10\t11\t12\t20\t40\t30'

    def test_merged_by_element_id_not_position(self, tmp_path):
        """Files list the same elements in different orders; output is merged
        by element ID and written in ascending ID order."""
        inputs = std_inputs(
            tmp_path,
            npag=[(5, ['10', '11']), (3, ['20', '21'])],
            pag=[(3, ['30']), (5, ['40'])],
            urb=[(5, ['50']), (3, ['60'])],
            nvrv=[(3, ['70']), (5, ['80'])],
        )
        iwfm_lu4scenario(
            **inputs, npag_cols=2, pag_cols=1, nvrv_cols=1, urban_cols=1)

        lines = read_lines(tmp_path / 'scen_Landuse.dat')
        assert lines[2] == '3\t20\t21\t30\t70\t60'
        assert lines[3] == '5\t10\t11\t40\t80\t50'

    def test_mismatched_element_ids_raise(self, tmp_path):
        inputs = std_inputs(tmp_path, urb=[(1, ['7']), (9, ['8'])])
        with pytest.raises(ValueError, match='element IDs'):
            iwfm_lu4scenario(**inputs)

    def test_multi_date_file_raises(self, tmp_path):
        inputs = std_inputs(tmp_path)
        inputs['in_npag_file'] = make_lu_file(
            tmp_path, 'npag2.dat',
            [(1, vals(100, 20)), (2, vals(200, 20))],
            dates=[DATE, '09/30/2002_24:00'],
        )
        with pytest.raises(ValueError, match='more than one time step'):
            iwfm_lu4scenario(**inputs)

    def test_too_few_columns_raise(self, tmp_path):
        inputs = std_inputs(tmp_path, pag=[(1, ['1', '2']), (2, ['3', '4'])])
        with pytest.raises(ValueError, match='expected at least 5'):
            iwfm_lu4scenario(**inputs)

    def test_verbose_output(self, tmp_path, capsys):
        iwfm_lu4scenario(**std_inputs(tmp_path), verbose=True)
        captured = capsys.readouterr()
        assert 'lines from' in captured.out
        assert f'Wrote land use data for {DATE}' in captured.out
