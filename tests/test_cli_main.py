# test_cli_main.py
# Tests for CLI main module
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
from typer.testing import CliRunner


class TestCLIContext:
    """Tests for CLIContext class."""

    def test_cli_context_exists(self):
        """Test that CLIContext class exists."""
        from iwfm.cli.main import CLIContext
        
        assert CLIContext is not None

    def test_cli_context_instantiation(self):
        """Test that CLIContext can be instantiated."""
        from iwfm.cli.main import CLIContext
        
        ctx = CLIContext()
        assert ctx is not None

    def test_cli_context_default_user_level(self):
        """Test that CLIContext defaults to USER level."""
        from iwfm.cli.main import CLIContext
        from iwfm.cli.context import UserLevel
        
        ctx = CLIContext()
        assert ctx.user_level == UserLevel.USER

    def test_cli_context_user_level_assignment(self):
        """Test that user_level can be assigned."""
        from iwfm.cli.main import CLIContext
        from iwfm.cli.context import UserLevel
        
        ctx = CLIContext()
        ctx.user_level = UserLevel.DEV
        assert ctx.user_level == UserLevel.DEV

        ctx.user_level = UserLevel.POWER
        assert ctx.user_level == UserLevel.POWER


class TestConfigureLogging:
    """Tests for configure_logging function."""

    def test_configure_logging_exists(self):
        """Test that configure_logging function exists."""
        from iwfm.cli.main import configure_logging
        
        assert callable(configure_logging)

    def test_configure_logging_user_level(self):
        """Test configure_logging with USER level."""
        from iwfm.cli.main import configure_logging
        from iwfm.cli.context import UserLevel
        
        # Should not raise
        configure_logging(UserLevel.USER)

    def test_configure_logging_power_level(self):
        """Test configure_logging with POWER level."""
        from iwfm.cli.main import configure_logging
        from iwfm.cli.context import UserLevel
        
        # Should not raise
        configure_logging(UserLevel.POWER)

    def test_configure_logging_dev_level(self):
        """Test configure_logging with DEV level."""
        from iwfm.cli.main import configure_logging
        from iwfm.cli.context import UserLevel
        
        # Should not raise
        configure_logging(UserLevel.DEV)


class TestTyperApp:
    """Tests for the Typer app configuration."""

    def test_app_exists(self):
        """Test that app exists."""
        from iwfm.cli.main import app
        
        assert app is not None

    def test_app_is_typer(self):
        """Test that app is a Typer instance."""
        from iwfm.cli.main import app
        import typer
        
        assert isinstance(app, typer.Typer)

    def test_app_name(self):
        """Test that app has correct name."""
        from iwfm.cli.main import app
        
        assert app.info.name == "iwfm"

    def test_app_has_help(self):
        """Test that app has help text."""
        from iwfm.cli.main import app
        
        assert app.info.help is not None
        assert "Integrated Water Flow Model" in app.info.help


class TestRunFunction:
    """Tests for run() entry point function."""

    def test_run_function_exists(self):
        """Test that run function exists."""
        from iwfm.cli.main import run
        
        assert callable(run)


class TestCLIInvocation:
    """Tests for CLI invocation using CliRunner."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    def test_cli_help(self, runner):
        """Test that --help flag works."""
        from iwfm.cli.main import app
        
        result = runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        assert "iwfm" in result.output.lower() or "IWFM" in result.output

    def test_cli_no_args_shows_help(self, runner):
        """Test that no args shows help (no_args_is_help=True)."""
        from iwfm.cli.main import app
        
        result = runner.invoke(app, [])

        # click < 8.2 exits 0 for no_args_is_help; click >= 8.2 exits 2
        assert result.exit_code in (0, 2)
        assert "Usage" in result.output or "--help" in result.output

    def test_cli_level_option_user(self, runner):
        """Test --level user option."""
        from iwfm.cli.main import app
        
        result = runner.invoke(app, ["--level", "user", "--help"])
        
        assert result.exit_code == 0

    def test_cli_level_option_power(self, runner):
        """Test --level power option."""
        from iwfm.cli.main import app
        
        result = runner.invoke(app, ["--level", "power", "--help"])
        
        assert result.exit_code == 0

    def test_cli_level_option_dev(self, runner):
        """Test --level dev option."""
        from iwfm.cli.main import app
        
        result = runner.invoke(app, ["--level", "dev", "--help"])
        
        assert result.exit_code == 0

    def test_cli_short_level_option(self, runner):
        """Test -l short option for level."""
        from iwfm.cli.main import app
        
        result = runner.invoke(app, ["-l", "power", "--help"])
        
        assert result.exit_code == 0

    def test_cli_invalid_level_option(self, runner):
        """Test invalid --level option."""
        from iwfm.cli.main import app
        
        result = runner.invoke(app, ["--level", "invalid"])
        
        # Should fail with error
        assert result.exit_code != 0


class TestSubcommandRegistration:
    """Tests for subcommand registration."""

    def test_register_commands_function_exists(self):
        """Test that _register_commands function exists."""
        from iwfm.cli.main import _register_commands
        
        assert callable(_register_commands)

    def test_calib_subcommand_registered(self):
        """Test that calib subcommand is registered if module exists."""
        from iwfm.cli.main import app

        command_names = [cmd.name for cmd in app.registered_groups]
        # Subcommand only registered if iwfm.calib.calib module exists
        try:
            from iwfm.calib import calib
            assert 'calib' in command_names
        except (ImportError, AttributeError):
            pytest.skip("calib CLI module not available")

    def test_gis_subcommand_registered(self):
        """Test that gis subcommand is registered if module exists."""
        from iwfm.cli.main import app

        command_names = [cmd.name for cmd in app.registered_groups]
        try:
            from iwfm.gis import gis
            assert 'gis' in command_names
        except (ImportError, AttributeError):
            pytest.skip("gis CLI module not available")

    def test_xls_subcommand_registered(self):
        """Test that xls subcommand is registered if module exists."""
        from iwfm.cli.main import app

        command_names = [cmd.name for cmd in app.registered_groups]
        try:
            from iwfm.xls import xls
            assert 'xls' in command_names
        except (ImportError, AttributeError):
            pytest.skip("xls CLI module not available")

    def test_debug_subcommand_registered(self):
        """Test that debug subcommand is registered if module exists."""
        from iwfm.cli.main import app

        command_names = [cmd.name for cmd in app.registered_groups]
        try:
            from iwfm.debug import debug
            assert 'debug' in command_names
        except (ImportError, AttributeError):
            pytest.skip("debug CLI module not available")


class TestMainImports:
    """Tests for main module imports."""

    def test_import_app(self):
        """Test importing app."""
        from iwfm.cli.main import app
        assert app is not None

    def test_import_cli_context(self):
        """Test importing CLIContext."""
        from iwfm.cli.main import CLIContext
        assert CLIContext is not None

    def test_import_get_context(self):
        """Test importing get_context."""
        from iwfm.cli.main import get_context
        assert callable(get_context)

    def test_import_configure_logging(self):
        """Test importing configure_logging."""
        from iwfm.cli.main import configure_logging
        assert callable(configure_logging)

    def test_import_main_callback(self):
        """Test importing main callback."""
        from iwfm.cli.main import main
        assert callable(main)

    def test_import_run(self):
        """Test importing run."""
        from iwfm.cli.main import run
        assert callable(run)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
