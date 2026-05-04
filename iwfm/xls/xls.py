# xls.py
# Typer subapp for `iwfm xls ...` subcommands
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

"""Typer subapp for IWFM Excel import/export utilities."""

from __future__ import annotations

import typer

app = typer.Typer(
    name="xls",
    help="Excel import/export utilities.",
    no_args_is_help=True,
)


@app.command("bud2xl")
def bud2xl_cmd(
    budget_file: str = typer.Argument(..., help="IWFM budget text file."),
    excel_file: str = typer.Argument(..., help="Output Excel workbook (.xlsx)."),
    row: int = typer.Option(6, "--row", help="Worksheet row to write data to (default 6)."),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Convert a single IWFM budget text file to an Excel worksheet."""
    import iwfm
    from iwfm.xls.bud2xl import bud2xl
    iwfm.file_test(budget_file)
    bud2xl(budget_file, excel_file, verbose=verbose, row=row)


@app.command("buds2xl")
def buds2xl_cmd(
    bud_file: str = typer.Argument(..., help="IWFM Budget input file (lists multiple budget HDFs)."),
    type: str = typer.Option("xlsx", "--type",
                             help="Output type: 'xlsx' (Excel) or 'csv'."),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Convert multiple IWFM budget HDFs (as listed in a Budget input file) to xlsx or csv."""
    import iwfm
    from iwfm.xls.buds2xl import buds2xl
    iwfm.file_test(bud_file)
    buds2xl(bud_file, type=type, verbose=verbose)
