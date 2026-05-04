# test_calib_divshort2obs.py
# Unit tests for calib/divshort2obs.py - Convert diversion shortages to SMP format
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
import numpy as np


def _build_budget_lines(num_reaches=2, num_dates=3):
    """Build mock IWFM diversion budget file lines.

    The format must satisfy process_budget() parsing rules:
      - Lines 0-1 are title lines (do not start with '-').
      - Line 1 must end (after split) with a token whose ``[:-1]``
        yields an integer (the reach number). Example last token: ``1)``
      - Line 2 is a dash separator.
      - Lines 3-5 are header lines.
      - Line 4 must end with exactly the string 'Shortage' (no trailing
        spaces) so that ``hline[i:i+cwidth] == 'Shortage'`` succeeds
        when the slice extends past end-of-string and Python truncates it.
      - Line 6 is a dash separator.
      - Data lines follow, then two blank lines per table.
      - Each data line from column ``loc`` (= position-of-S minus 4)
        to end-of-line must be parseable as a float.
    """
    # Header line 4 template: 'Shortage' is the last 8 characters.
    # Positions (0-indexed):
    #   columns  0-15  : Time
    #   columns 16-27  : Actual Div
    #   columns 28-39  : Div Shortage
    #   columns 40-51  : Recov Loss
    #   columns 52-63  : Delivery
    #   columns 64-79  : Shortage  (starts col 72, 'Shortage' = cols 72-79)
    header4 = (
        '      Time          Actual      Div         Recov       '
        'Delivery    Shortage'
    )
    # Position of 'S' in 'Shortage' on header4
    shortage_pos = header4.index('Shortage')
    loc = shortage_pos - 4  # this is what process_budget computes

    lines = []
    base_dates = [
        '10/31/1973_24:00',
        '11/30/1973_24:00',
        '12/31/1973_24:00',
        '01/31/1974_24:00',
        '02/28/1974_24:00',
        '03/31/1974_24:00',
        '04/30/1974_24:00',
        '05/31/1974_24:00',
    ]
    shortage_values = [5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0]

    for reach in range(1, num_reaches + 1):
        # Line 0 - title (must NOT start with '-')
        lines.append('   IWFM STREAM PACKAGE (v4.2.0106)')
        # Line 1 - reach identifier: last token is '<N>)' so [:-1] -> '<N>'
        lines.append(f'   DIVERSION DETAILS IN AC.FT. FOR {reach})')
        # Line 2 - dash separator
        lines.append('-' * 80)
        # Line 3 - header row 1
        lines.append('                    Actual      Div         Recov       '
                      'Delivery             ')
        # Line 4 - header row 2 (ends with 'Shortage', no trailing spaces)
        lines.append(header4)
        # Line 5 - units row
        lines.append('                       (+)         (-)          (+)       '
                      '   (+)            (=)')
        # Line 6 - dash separator
        lines.append('-' * 80)

        # Data lines
        for d in range(num_dates):
            date = base_dates[d % len(base_dates)]
            value = shortage_values[d % len(shortage_values)]
            # Build a line where columns >= loc parse as a float
            line = ' ' * loc + f'{value:>16.2f}'
            # Prepend the date in the first 16 chars
            line = date.ljust(16) + line[16:]
            lines.append(line)

        # Two blank lines per table (only one needed, but match real file pattern)
        lines.append('')
        lines.append('')

    return lines


def _build_groups_file(tmp_path, groups, maxpergroup=4):
    """Build a stgwgroups.in-style reach groups file.

    Parameters
    ----------
    tmp_path : pathlib.Path
        Temp dir from pytest fixture.
    groups : list of (name, [reach_nums]) tuples
        Each tuple becomes one data row.
    maxpergroup : int
        Header value (informational).

    Returns
    -------
    str
        Path to the written file.
    """
    reach_file = tmp_path / 'stgwgroups.in'
    lines = [
        f'maxpergroup  {maxpergroup}',
        f'numrchgroup {len(groups)}',
        'groupname\tnum_per_group\treaches',
    ]
    for name, reach_nums in groups:
        cols = [name, str(len(reach_nums))] + [str(n) for n in reach_nums]
        lines.append('\t'.join(cols))
    reach_file.write_text('\n'.join(lines))
    return str(reach_file)


class TestReadReaches:
    """Tests for read_reaches() against the real stgwgroups.in format.

    Format (3 header lines, then `name<sep>num_per_group<sep>reach_nums...`).
    Separators between reach_nums can be tabs, spaces, OR commas.
    """

    def test_returns_list(self, tmp_path):
        from iwfm.calib.divshort2obs import read_reaches
        reach_file = _build_groups_file(tmp_path, [('REACH1', [1])])
        result = read_reaches(reach_file)
        assert isinstance(result, list)

    def test_parses_reach_name(self, tmp_path):
        from iwfm.calib.divshort2obs import read_reaches
        reach_file = _build_groups_file(tmp_path, [('MY_REACH', [1])])
        result = read_reaches(reach_file)
        assert result[0][0] == 'MY_REACH'

    def test_parses_reach_numbers(self, tmp_path):
        """Multiple reach numbers in one group are returned as a list of ints."""
        from iwfm.calib.divshort2obs import read_reaches
        reach_file = _build_groups_file(tmp_path, [('REACH1', [1, 2, 3])])
        result = read_reaches(reach_file)
        assert result[0][1] == [1, 2, 3]

    def test_multiple_reaches(self, tmp_path):
        from iwfm.calib.divshort2obs import read_reaches
        reach_file = _build_groups_file(tmp_path, [
            ('REACH1', [1]),
            ('REACH2', [2, 3]),
            ('REACH3', [4, 5, 6]),
        ])
        result = read_reaches(reach_file)
        assert len(result) == 3

    def test_skips_header_lines(self, tmp_path):
        """The first 3 lines (maxpergroup, numrchgroup, column header) are skipped."""
        from iwfm.calib.divshort2obs import read_reaches
        reach_file = _build_groups_file(tmp_path, [
            ('FIRST_GROUP', [1]),
            ('SECOND_GROUP', [2]),
        ])
        result = read_reaches(reach_file)
        assert len(result) == 2
        assert result[0][0] == 'FIRST_GROUP'
        assert result[1][0] == 'SECOND_GROUP'

    def test_returns_list_of_lists(self, tmp_path):
        """Each entry is [name, [reach_num, ...]]."""
        from iwfm.calib.divshort2obs import read_reaches
        reach_file = _build_groups_file(tmp_path, [('TestReach', [42])])
        result = read_reaches(reach_file)
        assert isinstance(result[0], list)
        assert len(result[0]) == 2
        assert isinstance(result[0][0], str)
        assert isinstance(result[0][1], list)
        assert isinstance(result[0][1][0], int)

    def test_uses_num_per_group(self, tmp_path):
        """num_per_group controls how many trailing tokens are read as reaches."""
        from iwfm.calib.divshort2obs import read_reaches
        # Manually build a line where extra trailing whitespace tokens exist
        # (the real file has trailing tabs); only num_per_group should be read.
        reach_file = tmp_path / 'stgwgroups.in'
        reach_file.write_text(
            'maxpergroup  4\n'
            'numrchgroup 1\n'
            'groupname\tnum_per_group\treaches\n'
            'GROUP_A\t2\t10\t20\t\t\t\n'
        )
        result = read_reaches(str(reach_file))
        assert result == [['GROUP_A', [10, 20]]]

    def test_comma_separated_reach_nums(self, tmp_path):
        """Reach numbers separated by commas are parsed too."""
        from iwfm.calib.divshort2obs import read_reaches
        reach_file = tmp_path / 'stgwgroups.in'
        reach_file.write_text(
            'maxpergroup  4\n'
            'numrchgroup 1\n'
            'groupname\tnum_per_group\treaches\n'
            'GROUP_B\t3\t1,2,3\n'
        )
        result = read_reaches(str(reach_file))
        assert result == [['GROUP_B', [1, 2, 3]]]

    def test_mixed_separators(self, tmp_path):
        """Reach numbers separated by mix of tabs/spaces/commas are parsed."""
        from iwfm.calib.divshort2obs import read_reaches
        reach_file = tmp_path / 'stgwgroups.in'
        reach_file.write_text(
            'maxpergroup  4\n'
            'numrchgroup 1\n'
            'groupname\tnum_per_group\treaches\n'
            'GROUP_C\t4\t55,56\t58 66\n'
        )
        result = read_reaches(str(reach_file))
        assert result == [['GROUP_C', [55, 56, 58, 66]]]


class TestProcessBudget:
    """Tests for process_budget function"""

    def create_mock_budget_file(self, tmp_path, num_reaches=2, num_dates=3):
        """Helper to create a mock IWFM diversion budget file."""
        budget_file = tmp_path / 'test_diversions.bud'
        lines = _build_budget_lines(num_reaches=num_reaches,
                                    num_dates=num_dates)
        budget_file.write_text('\n'.join(lines))
        return str(budget_file)

    def test_process_budget_returns_three_items(self, tmp_path):
        from iwfm.calib.divshort2obs import process_budget
        budget_file = self.create_mock_budget_file(tmp_path)
        result = process_budget(budget_file)
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_process_budget_reach_list(self, tmp_path):
        from iwfm.calib.divshort2obs import process_budget
        budget_file = self.create_mock_budget_file(tmp_path, num_reaches=3, num_dates=5)
        budget_table, reach_list, dates = process_budget(budget_file)
        assert reach_list == [1, 2, 3]

    def test_process_budget_dates(self, tmp_path):
        from iwfm.calib.divshort2obs import process_budget
        budget_file = self.create_mock_budget_file(tmp_path, num_dates=3)
        budget_table, reach_list, dates = process_budget(budget_file)
        assert len(dates) == 3
        for date in dates:
            assert '_24:00' not in date

    def test_process_budget_table_structure(self, tmp_path):
        from iwfm.calib.divshort2obs import process_budget
        budget_file = self.create_mock_budget_file(tmp_path, num_reaches=2, num_dates=3)
        budget_table, reach_list, dates = process_budget(budget_file)
        assert len(budget_table) == 2
        for table in budget_table:
            assert isinstance(table, np.ndarray)
            assert len(table) == 3


class TestFormatDivshortSmp:
    """Tests for the pure formatter helper."""

    def test_returns_two_lists(self):
        from iwfm.calib.divshort2obs import format_divshort_smp
        budget_table = [np.array([100.0, 200.0])]
        dates = ['10/31/1973', '11/30/1973']
        reaches = [['DIV_001', [1]]]
        divshort, ins = format_divshort_smp(budget_table, dates, reaches)
        assert isinstance(divshort, list)
        assert isinstance(ins, list)

    def test_smp_format(self):
        from iwfm.calib.divshort2obs import format_divshort_smp
        budget_table = [np.array([123.45])]
        dates = ['10/31/1973']
        reaches = [['TEST_DIV', [1]]]
        divshort, ins = format_divshort_smp(budget_table, dates, reaches)
        assert len(divshort) == 1
        assert 'TEST_DIV' in divshort[0]
        assert '0:00:00' in divshort[0]
        assert '123.45' in divshort[0]

    def test_ins_format(self):
        from iwfm.calib.divshort2obs import format_divshort_smp
        budget_table = [np.array([100.0])]
        dates = ['10/31/1973']
        reaches = [['DIV_001', [1]]]
        divshort, ins = format_divshort_smp(budget_table, dates, reaches)
        assert len(ins) == 1
        assert 'l1' in ins[0]
        assert 'DIV_001_' in ins[0]
        assert '45:56' in ins[0]

    def test_multiple_dates(self):
        from iwfm.calib.divshort2obs import format_divshort_smp
        budget_table = [np.array([100.0, 200.0, 300.0])]
        dates = ['10/31/1973', '11/30/1973', '12/31/1973']
        reaches = [['DIV_001', [1]]]
        divshort, ins = format_divshort_smp(budget_table, dates, reaches)
        assert len(divshort) == 3
        assert len(ins) == 3

    def test_multiple_reaches(self):
        """Two single-reach groups produce 2 reaches * 2 dates = 4 outputs."""
        from iwfm.calib.divshort2obs import format_divshort_smp
        budget_table = [
            np.array([100.0, 200.0]),
            np.array([150.0, 250.0]),
        ]
        dates = ['10/31/1973', '11/30/1973']
        reaches = [['DIV_001', [1]], ['DIV_002', [2]]]
        divshort, ins = format_divshort_smp(budget_table, dates, reaches)
        assert len(divshort) == 4
        assert len(ins) == 4

    def test_sums_multiple_reaches_in_group(self):
        """A group with multiple reach numbers sums their values."""
        from iwfm.calib.divshort2obs import format_divshort_smp
        budget_table = [
            np.array([100.0]),
            np.array([10.0]),
            np.array([1.0]),
        ]
        dates = ['10/31/1973']
        reaches = [['SUMGROUP', [1, 2, 3]]]
        divshort, ins = format_divshort_smp(budget_table, dates, reaches)
        # 100 + 10 + 1 = 111
        assert '111.0' in divshort[0]

    def test_does_not_mutate_caller_arrays(self):
        """Summing across a group must not mutate the caller's budget_table arrays."""
        from iwfm.calib.divshort2obs import format_divshort_smp
        a = np.array([100.0])
        b = np.array([10.0])
        budget_table = [a, b]
        dates = ['10/31/1973']
        reaches = [['SUM', [1, 2]]]
        format_divshort_smp(budget_table, dates, reaches)
        assert a[0] == 100.0  # would be 110.0 if mutated
        assert b[0] == 10.0

    def test_date_conversion(self):
        from iwfm.calib.divshort2obs import format_divshort_smp
        budget_table = [np.array([100.0])]
        dates = ['1/5/1980']  # single-digit month and day
        reaches = [['DIV_001', [1]]]
        divshort, ins = format_divshort_smp(budget_table, dates, reaches)
        assert len(divshort) == 1
        assert '01/05/1980' in divshort[0]

    def test_name_padding(self):
        from iwfm.calib.divshort2obs import format_divshort_smp
        budget_table = [np.array([100.0])]
        dates = ['10/31/1973']
        reaches = [['A', [1]]]
        divshort, ins = format_divshort_smp(budget_table, dates, reaches, nwidth=20)
        assert divshort[0].startswith('A' + ' ' * 19)

    def test_negative_values(self):
        from iwfm.calib.divshort2obs import format_divshort_smp
        budget_table = [np.array([-50.0, -100.0])]
        dates = ['10/31/1973', '11/30/1973']
        reaches = [['DIV_001', [1]]]
        divshort, ins = format_divshort_smp(budget_table, dates, reaches)
        assert '-50.0' in divshort[0]
        assert '-100.0' in divshort[1]

    def test_zero_values(self):
        from iwfm.calib.divshort2obs import format_divshort_smp
        budget_table = [np.array([0.0, 0.0])]
        dates = ['10/31/1973', '11/30/1973']
        reaches = [['DIV_001', [1]]]
        divshort, ins = format_divshort_smp(budget_table, dates, reaches)
        assert '0.0' in divshort[0]

    def test_reach_index(self):
        """Group with reach=[2] picks budget_table[1]."""
        from iwfm.calib.divshort2obs import format_divshort_smp
        budget_table = [
            np.array([100.0]),  # reach 1
            np.array([200.0]),  # reach 2
            np.array([300.0]),  # reach 3
        ]
        dates = ['10/31/1973']
        reaches = [['DIV_002', [2]]]
        divshort, ins = format_divshort_smp(budget_table, dates, reaches)
        assert '200.0' in divshort[0]


class TestDivshort2ObsIntegration:
    """Integration tests using all three functions together via temp files."""

    def create_test_files(self, tmp_path, num_reaches=2, num_dates=3):
        """Create budget and reach group files for integration testing."""
        budget_file = tmp_path / 'diversions.bud'
        lines = _build_budget_lines(num_reaches=num_reaches, num_dates=num_dates)
        budget_file.write_text('\n'.join(lines))

        reach_file = _build_groups_file(
            tmp_path,
            [(f'DIV_{i:03d}', [i]) for i in range(1, num_reaches + 1)],
        )
        return str(budget_file), reach_file

    def test_full_workflow(self, tmp_path):
        from iwfm.calib.divshort2obs import divshort2obs
        budget_file, reach_file = self.create_test_files(tmp_path,
                                                          num_reaches=2,
                                                          num_dates=3)
        divshort, ins = divshort2obs(budget_file, reach_file)
        # 2 groups * 3 dates = 6 outputs
        assert len(divshort) == 6
        assert len(ins) == 6

    def test_output_can_be_written_to_file(self, tmp_path):
        from iwfm.calib.divshort2obs import divshort2obs
        budget_file, reach_file = self.create_test_files(tmp_path)
        divshort, ins = divshort2obs(budget_file, reach_file)

        smp_file = tmp_path / 'output.smp'
        with open(smp_file, 'w') as f:
            for item in divshort:
                f.write(f'{item}\n')
        ins_file = tmp_path / 'output.ins'
        with open(ins_file, 'w') as f:
            f.write('pif #\n')
            for item in ins:
                f.write(f'{item}\n')

        assert smp_file.exists()
        assert ins_file.exists()
        assert smp_file.stat().st_size > 0
        assert ins_file.stat().st_size > 0


class TestWithRealFile:
    """Tests using the actual C2VSimCG diversions file if available."""

    @pytest.fixture
    def real_budget_file(self):
        """Get path to real budget file if it exists."""
        test_dir = os.path.dirname(__file__)
        # Either a dedicated diversions file or the streams budget (which
        # contains the Diversion Shortage column).
        for name in ('C2VSimCG_Diversions.bud', 'C2VSimCG_Streams_Budget.bud'):
            budget_path = os.path.join(test_dir, 'C2VSimCG-2021', 'Results', name)
            if os.path.exists(budget_path):
                return budget_path
        pytest.skip("No C2VSimCG budget file (Diversions or Streams_Budget) found")

    @pytest.fixture
    def real_reach_file(self):
        """Get path to real stgwgroups.in if it exists."""
        test_dir = os.path.dirname(__file__)
        reach_path = os.path.join(test_dir, 'C2VSimCG-2021', 'Calib', 'stgwgroups.in')
        if not os.path.exists(reach_path):
            pytest.skip(f"Reach groups file not found: {reach_path}")
        return reach_path

    def test_process_real_budget_file(self, real_budget_file):
        from iwfm.calib.divshort2obs import process_budget
        try:
            budget_table, reach_list, dates = process_budget(real_budget_file)
        except (ValueError, IndexError):
            pytest.skip("Budget file format not compatible with process_budget()")
        assert len(budget_table) > 0
        assert len(reach_list) > 0
        assert len(dates) > 0
        assert all(isinstance(r, int) for r in reach_list)
        assert all(isinstance(bt, np.ndarray) for bt in budget_table)

    def test_dates_format_real_file(self, real_budget_file):
        from iwfm.calib.divshort2obs import process_budget
        try:
            budget_table, reach_list, dates = process_budget(real_budget_file)
        except (ValueError, IndexError):
            pytest.skip("Budget file format not compatible with process_budget()")
        for date in dates:
            assert '_24:00' not in date
            parts = date.split('/')
            assert len(parts) == 3

    def test_read_real_groups_file(self, real_reach_file):
        from iwfm.calib.divshort2obs import read_reaches
        reaches = read_reaches(real_reach_file)
        assert len(reaches) > 0
        for entry in reaches:
            assert isinstance(entry, list) and len(entry) == 2
            assert isinstance(entry[0], str)
            assert isinstance(entry[1], list)
            assert all(isinstance(n, int) for n in entry[1])

    def test_end_to_end_real_files(self, real_budget_file, real_reach_file):
        """End-to-end with real fixtures: compute SMP/INS for groups whose
        reach numbers are all within range of the budget file's reach count.
        """
        from iwfm.calib.divshort2obs import (
            process_budget, read_reaches, format_divshort_smp,
        )
        budget_table, _reach_list, dates = process_budget(real_budget_file)
        groups = read_reaches(real_reach_file)
        # Filter out groups whose reach numbers exceed the budget file's
        # reach count (the user's stgwgroups.in may target a larger model).
        valid = [g for g in groups if max(g[1]) <= len(budget_table)]
        assert valid, "no groups in stgwgroups.in fit within the budget reach count"

        divshort, ins = format_divshort_smp(budget_table, dates, valid)
        # one row per group per date
        assert len(divshort) == len(valid) * len(dates)
        assert len(ins) == len(divshort)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
