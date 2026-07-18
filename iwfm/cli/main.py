# main.py
# Unified Command Line Interface entry point for iwfm
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



"""
Unified CLI entry point for IWFM.

This module defines:
- Root Typer app
- Global flags (--power, --dev)
- Logging configuration
- Registration of command groups

Existing scripts remain directly runnable.
"""

from __future__ import annotations

import sys
import typer
from iwfm.debug.logger_setup import logger
from iwfm.cli.context import UserLevel

# Root Typer app
app = typer.Typer(
    name="iwfm",
    help="Integrated Water Flow Model utilities",
    add_completion=True,
    no_args_is_help=True,
)

# ---- CLI Context -------------------------------------------------------------

class CLIContext:
    """
    Holds global CLI state shared across commands.
    """
    def __init__(self):
        self.user_level: UserLevel = UserLevel.USER


def get_context() -> CLIContext:
    ctx = typer.get_current_context()
    if ctx.obj is None:
        ctx.obj = CLIContext()
    return ctx.obj


# ---- Logging ----------------------------------------------------------------

def configure_logging(user_level: UserLevel) -> None:
    """
    Configure logging once, based on CLI mode using loguru logger.
    """
    if user_level.is_dev():
        level = "DEBUG"
    elif user_level.is_power():
        level = "INFO"
    else:
        level = "WARNING"

    logger.remove()  # Remove default loguru logger
    logger.add(
        sys.stderr,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    )
    logger.debug(f"Logging configured: level={level}")


# ---- Root Callback -----------------------------------------------------------

@app.callback()
def main(
    ctx: typer.Context,
    level: UserLevel = typer.Option(
        UserLevel.USER,
        "--level",
        "-l",
        help="User level: user (default), power (INFO logging), or dev (DEBUG logging)",
        case_sensitive=False,
    ),
):
    """
    IWFM unified command-line interface.
    """
    ctx.ensure_object(CLIContext)
    ctx.obj.user_level = level

    configure_logging(user_level=level)


# ---- Subcommand Registration -------------------------------------------------
# Importing here avoids circular imports and keeps startup predictable

def _register_commands():
    '''Register all command groups.

    Power/dev visibility is handled inside each group.
    '''
    try:
        from iwfm.calib import calib
        app.add_typer(calib.app, name="calib", help="Model calibration commands")
    except (ImportError, AttributeError):
        pass

    try:
        from iwfm.gis import gis
        app.add_typer(gis.app, name="gis", help="GIS-related utilities")
    except (ImportError, AttributeError):
        pass

    try:
        from iwfm.xls import xls
        app.add_typer(xls.app, name="xls", help="Excel import/export utilities")
    except (ImportError, AttributeError):
        pass

    try:
        from iwfm.hdf5 import hdf5
        app.add_typer(hdf5.app, name="hdf5", help="HDF5 budget conversion utilities")
    except (ImportError, AttributeError):
        pass

    try:
        from iwfm.debug import debug
        # Note: `hidden` can't be computed from get_context() here because there
        # is no active typer context at registration time (this runs at import).
        # Always-visible for now; hide-by-default-unless-dev would need each
        # command to inspect ctx.obj.user_level at invocation.
        app.add_typer(debug.app, name="debug", help="Developer and diagnostic commands")
    except (ImportError, AttributeError):
        pass


_register_commands()


# ---- Entry Point -------------------------------------------------------------

def run():
    """
    Console script entry point.
    """
    app()


if __name__ == "__main__":
    run()
