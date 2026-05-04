#!/usr/bin/env python
# test_meas_bounds.py
# Unit tests for meas_bounds.py
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

from datetime import datetime

import pytest

from iwfm.meas_bounds import meas_bounds


def _write_smp(tmp_path, body):
    path = tmp_path / 'obs.smp'
    path.write_text(body)
    return str(path)


def test_function_exists():
    """meas_bounds is importable and callable."""
    assert callable(meas_bounds)
    assert meas_bounds.__name__ == 'meas_bounds'


def test_function_signature():
    """meas_bounds takes a single positional argument gwhyd_obs."""
    import inspect
    params = list(inspect.signature(meas_bounds).parameters.keys())
    assert params == ['gwhyd_obs']


def test_exposed_via_iwfm_namespace():
    """meas_bounds is re-exported from iwfm/__init__.py."""
    import iwfm
    assert iwfm.meas_bounds is meas_bounds


class TestMeasBounds:
    """Tests for meas_bounds() over SMP-format observation files."""

    def test_typical_multi_row(self, tmp_path):
        """Earliest and latest dates over a normal SMP file."""
        body = (
            ' 11N19W05Q001S          01/28/1987   00:00:00   108.530\n'
            ' 11N19W05Q001S          02/15/1987   00:00:00   109.110\n'
            ' 11N19W05Q002S          12/31/1986   00:00:00    98.420\n'
            ' 11N19W05Q002S          06/01/2001   00:00:00    87.330\n'
        )
        earliest, latest = meas_bounds(_write_smp(tmp_path, body))
        assert earliest == datetime(1986, 12, 31)
        assert latest == datetime(2001, 6, 1)

    def test_single_row(self, tmp_path):
        """A single observation: earliest == latest."""
        body = ' WELL_A   05/15/2010   00:00:00   42.0\n'
        earliest, latest = meas_bounds(_write_smp(tmp_path, body))
        assert earliest == datetime(2010, 5, 15)
        assert latest == datetime(2010, 5, 15)

    def test_blank_lines_ignored(self, tmp_path):
        """Leading/trailing/interspersed blank lines must not break parsing."""
        body = (
            '\n'
            '\n'
            ' WELL_X   01/01/1990   00:00:00   1.0\n'
            '\n'
            ' WELL_Y   12/31/1995   00:00:00   2.0\n'
            '\n'
        )
        earliest, latest = meas_bounds(_write_smp(tmp_path, body))
        assert earliest == datetime(1990, 1, 1)
        assert latest == datetime(1995, 12, 31)

    def test_unparseable_lines_skipped(self, tmp_path):
        """Lines whose second token isn't MM/DD/YYYY are silently skipped."""
        body = (
            'header_line not_a_date\n'
            ' WELL_A   06/15/2000   00:00:00   10.0\n'
            ' WELL_B   garbage      00:00:00   11.0\n'
            ' WELL_C   07/04/2003   00:00:00   12.0\n'
        )
        earliest, latest = meas_bounds(_write_smp(tmp_path, body))
        assert earliest == datetime(2000, 6, 15)
        assert latest == datetime(2003, 7, 4)

    def test_empty_file_returns_none(self, tmp_path):
        """Empty (or all-blank) file → (None, None) so callers can detect it."""
        earliest, latest = meas_bounds(_write_smp(tmp_path, ''))
        assert earliest is None
        assert latest is None

    def test_missing_file_exits(self, tmp_path):
        """A nonexistent path triggers iwfm.file_test, which calls sys.exit()."""
        bogus = str(tmp_path / 'does_not_exist.smp')
        with pytest.raises(SystemExit):
            meas_bounds(bogus)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
