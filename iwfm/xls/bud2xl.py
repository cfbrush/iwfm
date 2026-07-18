# bud2xl.py
# Read IWFM Budget or Z-Budget output file and paste into existing Excel workbook
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

def bud2xl(budget_file, excel_file, verbose=False, row=6):
    '''Read IWFM Budget or Z-Budget output file and paste into existing Excel workbook.

    .. deprecated::
        Use :func:`iwfm.xls.open_workbook`, :func:`iwfm.xls.write_cells`,
        and :func:`iwfm.xls.save_workbook` directly instead.

    Parameters
    ----------
    budget_file : str
        Name of IWFM Budget output file.
    excel_file : str
        Name of existing Excel file.
    verbose : bool, default=False
        Turn command-line output on or off.
    row : int, default=6
        Top row of table data in excel spreadsheets.

    Returns
    -------
    nothing
    '''
    import os
    import warnings
    from iwfm.xls import open_workbook, save_workbook, get_worksheet, write_cells, add_worksheet, close_workbook
    from iwfm.debug.logger_setup import logger

    warnings.warn(
        "bud2xl() is deprecated. Use open_workbook(), write_cells(), save_workbook() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    logger.warning("Deprecated function bud2xl() called")

    cwd = os.getcwd()

    # Read the Budget file into array file_lines
    try:
        with open(budget_file, encoding='utf-8') as f:
            file_lines = f.read().splitlines()
    except (FileNotFoundError, PermissionError, OSError) as e:
        logger.error(f'Failed to read budget file {budget_file}: {e}')
        raise
    logger.debug(f'Read budget file {budget_file}')
    file_lines = [word.replace('_24:00', ' ') for word in file_lines]

    # Get the Budget file header and footer info
    header, footer, table, line = 0, 0, 1, 0
    while not file_lines[line][0].isdigit():
        line += 1
        header += 1
    line += 1
    while line < len(file_lines) and file_lines[line][0].isdigit():
        line += 1
        table += 1
    line += 1

    if line + 5 < len(file_lines):
        while (len(file_lines[line]) == 0 or not file_lines[line][0].isdigit()):
            line += 1
            footer += 1
    footer += 1
    footer -= header
    tables = round(len(file_lines) / (header + table + footer))

    if verbose:
        print(f'  Read {tables} tables from {budget_file}')

    # Open the excel workbook
    excel_path = os.path.join(cwd, excel_file)
    try:
        wb = open_workbook(excel_path)
    except Exception as e:
        logger.error(f'Failed to open Excel workbook {excel_path}: {e}')
        raise
    logger.debug(f'Opened Excel workbook {excel_path}')

    if verbose:
        print(f'  Opened {excel_file}')

    # If there are too few worksheets, add some
    sheet_count = len(wb.sheetnames) if hasattr(wb, 'sheetnames') else wb.Sheets.Count
    if sheet_count < tables + 1:
        if verbose:
            print(f'=> {tables} tables for {sheet_count} worksheets in {excel_file}')
            print(f'=> Adding {tables - sheet_count + 1} worksheets to {excel_file}')
        for i in range(sheet_count, tables + 1):
            add_worksheet(wb)

    # Step through the Budget file, one table at a time
    line = 0
    for t in range(0, tables):
        line += header
        budget_data = []
        for _ in range(table):
            lines = file_lines[line].split()
            budget_data.append(lines)
            line += 1
        line += footer

        # Write to excel worksheet
        ws = get_worksheet(wb, t + 1)  # Skip first sheet (index 0)
        write_cells(ws, budget_data, start_row=row, start_col=1)
        budget_data.clear()

    try:
        save_workbook(wb, excel_path)
    except Exception as e:
        logger.error(f'Failed to save Excel workbook {excel_path}: {e}')
        raise
    logger.debug(f'Saved Excel workbook {excel_path}')

    try:
        close_workbook(wb)
    except Exception as e:
        logger.error(f'Failed to close Excel workbook {excel_path}: {e}')
        raise
    logger.debug(f'Closed Excel workbook {excel_path}')

    if verbose:
        print(f'  Closed {excel_file}')


if __name__ == '__main__':
    """Run bud2xl() from command line."""
    import sys
    import iwfm.debug as idb
    import iwfm
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    if len(sys.argv) > 1:
        budget_file = sys.argv[1]
        excel_file = sys.argv[2]

    else:
        budget_file = input('IWFM Budget file name: ')
        excel_file = input('Output Excel file name: ')

    iwfm.file_test(budget_file)
    iwfm.file_test(excel_file)

    idb.exe_time()
    bud2xl(budget_file, excel_file, verbose=verbose)

    idb.exe_time()
