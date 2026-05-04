#!/usr/bin/env python
# 06_xls_workbook.py
# Build an Excel workbook with the openpyxl backend
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
06_xls_workbook.py — Build an Excel workbook with the openpyxl backend.

Usage:
    python 06_xls_workbook.py <output.xlsx>

Demonstrates the new (post-deprecation) `iwfm.xls` API:
    create_workbook → add_worksheet → write_cells → save_workbook → close_workbook

The legacy `excel_init`/`xl_open`/`xl_save`/etc. functions still work but
issue DeprecationWarnings.
"""
from __future__ import annotations

import sys

from iwfm.xls import (
    create_workbook,
    add_worksheet,
    write_cells,
    save_workbook,
    close_workbook,
    get_backend,
)


def main(output_file: str) -> None:
    print(f"backend: {get_backend()}")  # 'openpyxl' (or 'win32com' fallback)

    wb = create_workbook(output_file)

    ws_a = add_worksheet(wb, name='Series A')
    write_cells(ws_a, [
        ['Date', 'Value'],
        ['2020-01-01', 100.0],
        ['2020-02-01', 110.5],
        ['2020-03-01', 105.7],
    ])

    ws_b = add_worksheet(wb, name='Series B')
    write_cells(ws_b, [
        ['Year', 'Total'],
        [2018, 12345],
        [2019, 13567],
        [2020, 14210],
    ])

    save_workbook(wb)
    close_workbook(wb)
    print(f"wrote {output_file}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    main(sys.argv[1])
