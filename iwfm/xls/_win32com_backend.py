# _win32com_backend.py
# win32com backend for Excel operations (Windows only, legacy)
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
Legacy win32com backend for Excel operations (Windows only).

This module is deprecated and maintained only for backward compatibility.
It is used as a fallback when openpyxl is not installed.

Install openpyxl for cross-platform support: pip install openpyxl
"""

import warnings
from iwfm.debug.logger_setup import logger

# Issue deprecation warning on import
warnings.warn(
    "Using legacy win32com backend. This is Windows-only and deprecated. "
    "Install openpyxl for cross-platform support: pip install openpyxl",
    DeprecationWarning,
    stacklevel=2
)
logger.warning("win32com backend loaded - this is deprecated, install openpyxl")


def _get_win32():
    """Import and return win32com.client."""
    import win32com.client as win32
    return win32


# -----------------------------------------------------------------------------
# New API implemented with win32com
# -----------------------------------------------------------------------------

def create_workbook(filename=None):
    """Create a new Excel workbook using win32com.

    Parameters
    ----------
    filename : str, optional
        Path to save workbook to when save_workbook() is called.

    Returns
    -------
    workbook : win32com workbook object
        New Excel workbook object.
    """
    win32 = _get_win32()

    logger.debug(f"Creating new workbook (win32com){f' for {filename}' if filename else ''}")
    excel = win32.DispatchEx('Excel.Application')
    excel.Visible = False
    excel.DisplayAlerts = False
    wb = excel.Workbooks.Add()
    wb._iwfm_filename = filename
    wb._iwfm_excel_app = excel
    logger.info(f"Created new workbook{f': {filename}' if filename else ''}")
    return wb


def open_workbook(filename, data_only=False):
    """Open existing Excel workbook using win32com.

    Parameters
    ----------
    filename : str
        Path to existing Excel file.
    data_only : bool, default=False
        If True, read cell values only (not formulas).
        Note: win32com always reads computed values.

    Returns
    -------
    workbook : win32com workbook object
        Opened Excel workbook object.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    """
    import os
    win32 = _get_win32()

    if not os.path.exists(filename):
        raise FileNotFoundError(f"Excel file not found: {filename}")

    logger.debug(f"Opening workbook (win32com): {filename}")
    excel = win32.gencache.EnsureDispatch('Excel.Application')
    excel.Visible = False
    excel.DisplayAlerts = False
    wb = excel.Workbooks.Open(os.path.abspath(filename))
    wb._iwfm_filename = filename
    wb._iwfm_excel_app = excel
    logger.info(f"Opened workbook: {filename}")
    return wb


def save_workbook(workbook, filename=None):
    """Save workbook using win32com.

    Parameters
    ----------
    workbook : win32com workbook object
        Workbook to save.
    filename : str, optional
        Path to save to. If not provided, uses filename from
        create_workbook() or open_workbook().

    Raises
    ------
    ValueError
        If no filename provided and workbook has no associated filename.
    """
    import os
    save_path = filename or getattr(workbook, '_iwfm_filename', None)
    if not save_path:
        raise ValueError("No filename specified")

    logger.debug(f"Saving workbook (win32com): {save_path}")
    workbook.SaveAs(os.path.abspath(save_path))
    logger.info(f"Saved workbook: {save_path}")


def close_workbook(workbook):
    """Close workbook and Excel application.

    Parameters
    ----------
    workbook : win32com workbook object
        Workbook to close.
    """
    logger.debug("Closing workbook (win32com)")
    excel = getattr(workbook, '_iwfm_excel_app', None)
    try:
        workbook.Close(SaveChanges=False)
    except Exception:
        pass
    if excel:
        try:
            excel.Quit()
        except Exception:
            pass
    logger.debug("Workbook closed")


def add_worksheet(workbook, name=None, position=None):
    """Add worksheet using win32com.

    Parameters
    ----------
    workbook : win32com workbook object
        Workbook to add sheet to.
    name : str, optional
        Name for the new sheet.
    position : int, optional
        Position to insert sheet (0-indexed). If None, adds at end.

    Returns
    -------
    worksheet : win32com worksheet object
        The newly created worksheet.
    """
    if position is None:
        ws = workbook.Sheets.Add(After=workbook.Sheets(workbook.Sheets.Count))
    else:
        ws = workbook.Sheets.Add(Before=workbook.Sheets(position + 1))
    if name:
        ws.Name = name
    logger.debug(f"Added worksheet: '{ws.Name}'")
    return ws


def get_worksheet(workbook, name_or_index):
    """Get worksheet by name or index.

    Parameters
    ----------
    workbook : win32com workbook object
        Workbook to get sheet from.
    name_or_index : str or int
        Sheet name or 0-based index.

    Returns
    -------
    worksheet : win32com worksheet object
        The requested worksheet.
    """
    if isinstance(name_or_index, int):
        ws = workbook.Worksheets(name_or_index + 1)  # COM is 1-indexed
    else:
        ws = workbook.Worksheets(name_or_index)
    logger.debug(f"Selected worksheet: '{ws.Name}'")
    return ws


def write_cells(worksheet, data, start_row=1, start_col=1):
    """Write 2D array to worksheet using win32com Range.

    Parameters
    ----------
    worksheet : win32com worksheet object
        Worksheet to write to.
    data : list of lists
        2D array of data to write.
    start_row : int, default=1
        Starting row (1-indexed).
    start_col : int, default=1
        Starting column (1-indexed).
    """
    if not data:
        logger.debug("No data to write")
        return

    rows = len(data)
    cols = len(data[0]) if data else 0
    end_row = start_row + rows - 1
    end_col = start_col + cols - 1

    worksheet.Range(
        worksheet.Cells(start_row, start_col),
        worksheet.Cells(end_row, end_col)
    ).Value = data

    logger.debug(f"Wrote {rows}x{cols} cells (win32com)")


def write_budget_data(workbook, budget_data):
    """Write IWFM budget data with formatting (win32com).

    Parameters
    ----------
    workbook : win32com workbook object
        Workbook to write to.
    budget_data : list
        List containing four lists:
        - loc_names : list of str - Location names
        - column_headers : list of lists - Column headers for each location
        - loc_values : list of DataFrames - Values for each location
        - titles : list of lists - Titles (3 items) for each location
    """
    loc_names, column_headers, loc_values, titles = budget_data

    logger.info(f"Writing budget data for {len(loc_names)} locations (win32com)")

    for loc in range(len(loc_names)):
        # Add worksheet
        ws = workbook.Sheets.Add(Before=None, After=workbook.Sheets(workbook.Sheets.Count))
        ws.Name = loc_names[loc]
        logger.debug(f"Creating budget sheet: '{loc_names[loc]}'")

        # Write titles
        for i in range(len(titles[loc])):
            ws.Cells(i + 1, 1).Value = titles[loc][i]

        # Write column headers to row 5
        for i in range(len(column_headers[loc])):
            ws.Cells(5, i + 1).Value = column_headers[loc][i]

        # Write data
        df = loc_values[loc]
        for i in range(df.shape[0]):
            ws.Cells(i + 6, 1).Value = df.iloc[i, 0].strftime('%m/%d/%Y')

        # Write values as array for performance
        col = chr(ord("@") + df.shape[1])
        row = 5 + df.shape[0]
        ws.Range("B6", f"{col}{row}").Value = df.iloc[:, 1:].values

        # Format cells
        ws.Range("A6", f"A{row}").NumberFormat = "MM/DD/YYYY"
        ws.Range("B6", f"{col}{row}").NumberFormat = "#,##0.00"
        ws.Range("A1", f"{col}5").Font.Bold = True
        ws.Range("A5", f"{col}5").HorizontalAlignment = 3
        ws.Range("A5", f"{col}5").WrapText = True
        ws.Range("A5", f"{col}5").VerticalAlignment = 2

        # Set column widths
        for i in range(1, 36):
            ws.Columns(i).ColumnWidth = 14

        logger.debug(f"Wrote {df.shape[0]} rows to '{loc_names[loc]}'")

    logger.info("Completed writing budget data")


# -----------------------------------------------------------------------------
# Legacy function support
# -----------------------------------------------------------------------------

def excel_init(visible=False, display_alerts=False):
    """Initialize Excel application (legacy win32com).

    Parameters
    ----------
    visible : bool, default=False
        Whether to make Excel visible.
    display_alerts : bool, default=False
        Whether to display Excel alerts.

    Returns
    -------
    excel : win32com Excel Application object
        Excel application instance.
    """
    win32 = _get_win32()

    logger.debug("excel_init called (win32com mode)")
    excel = win32.DispatchEx('Excel.Application')
    excel.Visible = visible
    excel.DisplayAlerts = display_alerts
    return excel


def excel_new_workbook(excel):
    """Create a new workbook (legacy win32com).

    Parameters
    ----------
    excel : win32com Excel Application object
        Excel application instance.

    Returns
    -------
    workbook : win32com workbook object
        New workbook.
    """
    logger.debug("excel_new_workbook called (win32com mode)")
    return excel.Workbooks.Add()


def excel_kill(excel):
    """Close Excel application (legacy win32com).

    Parameters
    ----------
    excel : win32com Excel Application object
        Excel application instance to close.
    """
    logger.debug("excel_kill called (win32com mode)")
    excel.DisplayAlerts = False
    excel.Visible = False
    excel.Quit()


def xl_quit(excel):
    """Close Excel application (legacy win32com).

    Parameters
    ----------
    excel : win32com Excel Application object
        Excel application instance to close.
    """
    logger.debug("xl_quit called (win32com mode)")
    excel.DisplayAlerts = False
    excel.Visible = False
    excel.Application.Quit()
