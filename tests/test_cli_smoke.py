#!/usr/bin/env python
# test_cli_smoke.py
# Smoke tests for the `iwfm` console_script entry point
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


class TestCliSmoke:
    """Verify the unified `iwfm` CLI is wired correctly.

    The CLI scaffold lives at iwfm/iwfm/cli/main.py. The entry point is
    `iwfm.cli.main:run`, which is wired as a console_script in pyproject.toml
    and setup.py so users can run `iwfm` directly after `pip install -e .`.

    These tests don't shell out to the installed binary (slow, env-coupled);
    they exercise the underlying Typer app via CliRunner.
    """

    def test_app_is_a_typer(self):
        """The root CLI is a typer.Typer instance."""
        import typer
        from iwfm.cli.main import app
        assert isinstance(app, typer.Typer)

    def test_run_is_callable(self):
        """`run` is the entry-point function used by the console_script."""
        from iwfm.cli.main import run
        assert callable(run)

    def test_help_runs_cleanly(self):
        """Invoking the CLI with --help exits 0 and shows the app banner."""
        from typer.testing import CliRunner
        from iwfm.cli.main import app

        result = CliRunner().invoke(app, ['--help'])
        assert result.exit_code == 0
        assert 'Integrated Water Flow Model' in result.output

    def test_no_args_shows_help(self):
        """The app is configured with no_args_is_help=True; bare invocation
        prints help and exits non-zero (typer convention)."""
        from typer.testing import CliRunner
        from iwfm.cli.main import app

        result = CliRunner().invoke(app, [])
        # exit code can be 0 or 2 depending on typer version; just check that
        # the help banner is printed
        assert 'Integrated Water Flow Model' in result.output

    def test_level_flag_accepts_valid_choices(self):
        """--level should accept user/power/dev (the UserLevel enum values)."""
        from typer.testing import CliRunner
        from iwfm.cli.main import app

        for level in ('user', 'power', 'dev'):
            result = CliRunner().invoke(app, ['--level', level, '--help'])
            assert result.exit_code == 0, (
                f'--level {level} --help failed: {result.output}'
            )

    def test_level_flag_rejects_invalid_choice(self):
        """An unknown --level value should be rejected by typer.

        Note: don't pair this with --help — typer short-circuits to print
        help (exit 0) before validating other options.
        """
        from typer.testing import CliRunner
        from iwfm.cli.main import app

        result = CliRunner().invoke(app, ['--level', 'bogus'])
        assert result.exit_code != 0

    def test_top_level_help_lists_subgroups(self):
        """The five subgroups (calib, gis, xls, hdf5, debug) appear in help."""
        from typer.testing import CliRunner
        from iwfm.cli.main import app

        result = CliRunner().invoke(app, ['--help'])
        assert result.exit_code == 0
        for group in ('calib', 'gis', 'xls', 'hdf5', 'debug'):
            assert group in result.output, f'subgroup {group!r} missing from --help'


@pytest.mark.parametrize('group,expected_cmd', [
    # calib (15)
    ('calib', 'divshort'),
    ('calib', 'stacdep'),
    ('calib', 'fac2iwfm'),
    ('calib', 'iwfm2obs'),
    ('calib', 'calib-stats'),
    ('calib', 'ltbud'),
    ('calib', 'ltsmp'),
    ('calib', 'pest-res-stats'),
    ('calib', 'ppk2fac-trans'),
    ('calib', 'real2iwfm'),
    ('calib', 'res-stats'),
    ('calib', 'simout2gw'),
    ('calib', 'smp-avg'),
    ('calib', 'smp-format'),
    ('calib', 'well-pairs-to-obs'),
    # hdf5 (18)
    ('hdf5', 'bud-gw'),
    ('hdf5', 'bud-stream'),
    ('hdf5', 'bud-lw'),
    ('hdf5', 'bud-rz'),
    ('hdf5', 'bud-unsat'),
    ('hdf5', 'bud-swat'),
    ('hdf5', 'bud-diversions'),
    ('hdf5', 'bud-snodes'),
    ('hdf5', 'xlsx-gw'),
    ('hdf5', 'xlsx-stream'),
    ('hdf5', 'xlsx-lw'),
    ('hdf5', 'xlsx-rz'),
    ('hdf5', 'xlsx-unsat'),
    ('hdf5', 'xlsx-swat'),
    ('hdf5', 'xlsx-diversions'),
    ('hdf5', 'xlsx-snodes'),
    ('hdf5', 'zbud-gw'),
    ('hdf5', 'zxlsx-gw'),
    # gis (4)
    ('gis', 'map-param2shp-npc'),
    ('gis', 'map-param2shp-pc'),
    ('gis', 'map-param2shp-urban'),
    ('gis', 'shp-reproject'),
    # xls (2)
    ('xls', 'bud2xl'),
    ('xls', 'buds2xl'),
    # debug (2)
    ('debug', 'env'),
    ('debug', 'python'),
])
def test_subcommand_help_works(group, expected_cmd):
    """Each registered subcommand answers --help cleanly."""
    from typer.testing import CliRunner
    from iwfm.cli.main import app

    result = CliRunner().invoke(app, [group, expected_cmd, '--help'])
    assert result.exit_code == 0, (
        f'iwfm {group} {expected_cmd} --help failed: {result.output}'
    )


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
