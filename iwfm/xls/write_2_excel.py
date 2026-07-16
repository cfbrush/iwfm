# write_2_excel.py
# Writes a 3D array as 2D tables to an excel workbook
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

import warnings
from iwfm.debug.logger_setup import logger


def write_2_excel(file_base_name, data, sheets, elements, time_steps, dates, data_type='Crop'):
    """Write a 3D array as 2D tables to an excel workbook.

    .. deprecated::
        Use :func:`iwfm.xls.create_workbook`, :func:`iwfm.xls.add_worksheet`,
        :func:`iwfm.xls.write_cells`, and :func:`iwfm.xls.save_workbook` instead.

    Parameters
    ----------
    file_base_name : str
        Base name of output file (without .xlsx extension).
    data : list
        3D array of data [sheets][elements][time_steps].
    sheets : int
        Number of sheets.
    elements : int
        Number of elements (rows of data).
    time_steps : int
        Number of time steps.
    dates : list
        Dates corresponding to time steps.
    data_type : str, default='Crop'
        Type of information (used in sheet names).
    """
    warnings.warn(
        "write_2_excel() is deprecated. Use create_workbook(), add_worksheet(), "
        "write_cells(), save_workbook() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    logger.warning("Deprecated function write_2_excel() called")

    from iwfm.xls import create_workbook, add_worksheet, save_workbook, close_workbook

    # Create workbook
    wkbkname = f'{file_base_name}.xlsx'
    workbook = create_workbook(wkbkname)

    logger.info(f"Writing {sheets} sheets to {wkbkname}")

    for i in range(sheets):
        # Create worksheet
        sheet_name = f'{data_type}{i + 1}'
        ws = add_worksheet(workbook, name=sheet_name)

        # Write header
        ws.cell(row=1, column=1, value=sheet_name)
        ws.cell(row=2, column=1, value='WYr')

        # Write dates in header row
        for k in range(time_steps):
            ws.cell(row=2, column=k + 2, value=int(dates[k].year))

        # Write data
        for j in range(elements):
            ws.cell(row=j + 3, column=1, value=j + 1)
            for k in range(time_steps):
                ws.cell(row=j + 3, column=k + 2, value=float(data[i][j][k]))

        logger.debug(f"Wrote sheet '{sheet_name}': {elements} rows x {time_steps} cols")

    save_workbook(workbook)
    close_workbook(workbook)

    logger.info(f"Saved workbook: {wkbkname}")
