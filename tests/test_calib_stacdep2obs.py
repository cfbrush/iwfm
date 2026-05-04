# test_calib_stacdep2obs.py
# Unit tests for calib/stacdep2obs.py - Convert Stream Budget to SMP format
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


def _build_groups_file(tmp_path, groups, maxpergroup=4):
    """Build a stgwgroups.in-style reach groups file (test helper)."""
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
    """Tests for read_reaches() — same parser is shared between
    iwfm.calib.divshort2obs and iwfm.iwfm_read_stream_reaches."""

    def test_returns_list(self, tmp_path):
        from iwfm.calib.divshort2obs import read_reaches
        reach_file = _build_groups_file(tmp_path, [('REACH1', [1])])
        assert isinstance(read_reaches(reach_file), list)

    def test_parses_reach_name(self, tmp_path):
        from iwfm.calib.divshort2obs import read_reaches
        reach_file = _build_groups_file(tmp_path, [('MY_REACH', [1])])
        assert read_reaches(reach_file)[0][0] == 'MY_REACH'

    def test_parses_reach_numbers(self, tmp_path):
        from iwfm.calib.divshort2obs import read_reaches
        reach_file = _build_groups_file(tmp_path, [('REACH1', [1, 2, 3])])
        assert read_reaches(reach_file)[0][1] == [1, 2, 3]

    def test_multiple_reaches(self, tmp_path):
        from iwfm.calib.divshort2obs import read_reaches
        reach_file = _build_groups_file(tmp_path, [
            ('REACH1', [1]),
            ('REACH2', [2, 3]),
            ('REACH3', [4, 5, 6]),
        ])
        assert len(read_reaches(reach_file)) == 3

    def test_skips_header_lines(self, tmp_path):
        from iwfm.calib.divshort2obs import read_reaches
        reach_file = _build_groups_file(tmp_path, [('REACH1', [1])])
        result = read_reaches(reach_file)
        # 3 header lines skipped, 1 data row
        assert len(result) == 1


class TestFormatStacdepSmp:
    """Tests for the pure formatter helper format_stacdep_smp."""

    def test_returns_two_lists(self):
        from iwfm.calib.stacdep2obs import format_stacdep_smp
        budget_table = [np.array([100.0, 110.0, 120.0])]
        dates = ['1/15/2020', '1/16/2020', '1/17/2020']
        reaches = [['REACH1', [1]]]
        result = format_stacdep_smp(budget_table, dates, reaches)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_creates_smp_format(self):
        from iwfm.calib.stacdep2obs import format_stacdep_smp
        budget_table = [np.array([100.0])]
        dates = ['1/15/2020']
        reaches = [['REACH1', [1]]]
        stacdep, ins = format_stacdep_smp(budget_table, dates, reaches)
        assert len(stacdep) == 1
        assert 'REACH1' in stacdep[0]
        assert '01/15/2020' in stacdep[0]

    def test_creates_ins_format(self):
        from iwfm.calib.stacdep2obs import format_stacdep_smp
        budget_table = [np.array([100.0])]
        dates = ['1/15/2020']
        reaches = [['REACH1', [1]]]
        stacdep, ins = format_stacdep_smp(budget_table, dates, reaches)
        assert len(ins) == 1
        assert 'l1' in ins[0]
        assert 'REACH1' in ins[0]
        assert '41:56' in ins[0]

    def test_multiple_dates(self):
        from iwfm.calib.stacdep2obs import format_stacdep_smp
        budget_table = [np.array([100.0, 110.0, 120.0])]
        dates = ['1/15/2020', '1/16/2020', '1/17/2020']
        reaches = [['REACH1', [1]]]
        stacdep, ins = format_stacdep_smp(budget_table, dates, reaches)
        assert len(stacdep) == 3
        assert len(ins) == 3

    def test_sums_multiple_reaches(self):
        """A group with multiple reach numbers sums their values."""
        from iwfm.calib.stacdep2obs import format_stacdep_smp
        budget_table = [
            np.array([100.0]),  # reach 1
            np.array([50.0]),   # reach 2
            np.array([25.0]),   # reach 3
        ]
        dates = ['1/15/2020']
        reaches = [['COMBINED', [1, 2, 3]]]
        stacdep, ins = format_stacdep_smp(budget_table, dates, reaches)
        # 100 + 50 + 25 = 175
        assert '175.0' in stacdep[0]

    def test_does_not_mutate_caller_arrays(self):
        from iwfm.calib.stacdep2obs import format_stacdep_smp
        a = np.array([100.0])
        b = np.array([50.0])
        budget_table = [a, b]
        dates = ['1/15/2020']
        reaches = [['SUM', [1, 2]]]
        format_stacdep_smp(budget_table, dates, reaches)
        assert a[0] == 100.0
        assert b[0] == 50.0


class TestStacdep2ObsIntegration:
    """End-to-end test using temp files."""

    def test_runs_with_real_inputs(self, tmp_path):
        """Smoke test: stacdep2obs(budget_file, reach_file) end-to-end against
        the real C2VSimCG fixture if available; otherwise skip.

        The synthetic _build_budget_lines helper produces a file with only
        the 'Diversion Shortage' column populated, not 'Gain from GW', so
        stacdep2obs's process_budget can't parse it. End-to-end coverage for
        stacdep2obs requires a real Streams_Budget.bud (which has the
        'Gain from GW' columns).
        """
        from iwfm.calib.stacdep2obs import stacdep2obs
        test_dir = os.path.dirname(__file__)
        budget_path = os.path.join(test_dir, 'C2VSimCG-2021', 'Results',
                                   'C2VSimCG_Streams_Budget.bud')
        reach_path = os.path.join(test_dir, 'C2VSimCG-2021', 'Calib',
                                  'stgwgroups.in')
        if not (os.path.exists(budget_path) and os.path.exists(reach_path)):
            pytest.skip("Real C2VSimCG fixtures not present")

        # Some user-supplied stgwgroups.in files reference reaches outside
        # the budget file's range — write a filtered copy to ensure the
        # smoke test stays robust to that.
        from iwfm.calib.divshort2obs import read_reaches, process_budget
        budget_table, _, _ = process_budget(budget_path)
        groups = read_reaches(reach_path)
        valid = [g for g in groups if max(g[1]) <= len(budget_table)]
        if not valid:
            pytest.skip("No groups in stgwgroups.in fit within budget reaches")

        filtered = tmp_path / 'stgwgroups.in'
        lines = ['maxpergroup  4', f'numrchgroup {len(valid)}',
                 'groupname\tnum_per_group\treaches']
        for name, nums in valid:
            cols = [name, str(len(nums))] + [str(n) for n in nums]
            lines.append('\t'.join(cols))
        filtered.write_text('\n'.join(lines))

        stacdep, ins = stacdep2obs(budget_path, str(filtered))
        # one row per group per date
        assert len(stacdep) > 0
        assert len(ins) == len(stacdep)


class TestStacdep2ObsImports:
    """Verify the public symbols are importable from the expected locations."""

    def test_import_process_budget(self):
        from iwfm.calib.stacdep2obs import process_budget
        assert callable(process_budget)

    def test_import_read_reaches(self):
        """read_reaches lives in divshort2obs and is shared via that module."""
        from iwfm.calib.divshort2obs import read_reaches
        assert callable(read_reaches)

    def test_import_stacdep2obs(self):
        from iwfm.calib.stacdep2obs import stacdep2obs
        assert callable(stacdep2obs)

    def test_import_format_stacdep_smp(self):
        from iwfm.calib.stacdep2obs import format_stacdep_smp
        assert callable(format_stacdep_smp)

    def test_import_from_calib(self):
        from iwfm.calib import stacdep2obs
        assert hasattr(stacdep2obs, 'stacdep2obs') or callable(stacdep2obs)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
