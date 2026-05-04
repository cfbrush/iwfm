# debug.py
# Typer subapp for `iwfm debug ...` subcommands
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

"""Typer subapp for IWFM developer/diagnostic commands."""

from __future__ import annotations

import typer

app = typer.Typer(
    name="debug",
    help="Developer and diagnostic commands.",
    no_args_is_help=True,
)


@app.command("env")
def env() -> None:
    """Print environment info (PATH, PYTHONPATH, system, cwd)."""
    from iwfm.debug.print_env import print_env
    print_env()


@app.command("python")
def python_info() -> None:
    """Print info about the running Python interpreter (version, path, platform)."""
    from iwfm.debug.this_python import this_python
    this_python()
