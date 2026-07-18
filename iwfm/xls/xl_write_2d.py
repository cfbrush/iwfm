# xl_write_2d.py
# Writes 2D array to excel workbook (DEPRECATED)
# Copyright (C) 2020-2026 University of California
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

'''Write 2D array to excel workbook (DEPRECATED).'''

import warnings
from iwfm.debug.logger_setup import logger


def xl_write_2d(output, wb, row=1, col=1, sheet=0):
    """Write a 2D array to an existing excel workbook.

    .. deprecated::
        Use :func:`iwfm.xls.write_cells` instead.

    Parameters
    ----------
    output : list
        2D array of data.
    wb : object
        Excel workbook object.
    row : int, default=1
        Top row of write area.
    col : int, default=1
        Left column of write area.
    sheet : int, default=0
        Worksheet number to write to.
    """
    warnings.warn(
        "xl_write_2d() is deprecated. Use get_worksheet() and write_cells() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    logger.warning("Deprecated function xl_write_2d() called - use write_cells() instead")

    from iwfm.xls import _get_backend_module, get_worksheet
    ws = get_worksheet(wb, sheet)
    return _get_backend_module().write_cells(ws, output, start_row=row, start_col=col)
