# budget_info.py
# Get the Budget file header and footer length and number of tables 
# Copyright (C) 2020-2025 University of California
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


def budget_info(budget_lines):
    '''Get the Budget file header and footer length and number of tables.

    Parameters
    ----------
    budget_lines : list of str
        contents of IWFM Budget file


    Returns
    -------
    tables : int
        number of tables in the busget file

    header : int
        number of header lines in each table

    footer : int
        number of footer lines in each table
    '''

    header, footer, table, line = 0, 0, 1, 0
    
    # Read to end of header (count lines that don't start with a digit)
    while line < len(budget_lines) and (not budget_lines[line] or not budget_lines[line][0].isdigit()):
        header += 1
        line += 1
    
    if line >= len(budget_lines):
        # No data lines found, return minimal values
        return 1, header, 0
        
    line += 1

    # Get field width (simplified approach)
    width, i = 0, 16  # get field width, width of DSS date
    if line < len(budget_lines) and len(budget_lines[line]) > i:
        while i + width < len(budget_lines[line]) and budget_lines[line][i+width].isspace():
            width += 1
        while i + width < len(budget_lines[line]) and not budget_lines[line][i+width].isspace():
            width += 1

    # Count data lines (lines that start with a digit)
    while line < len(budget_lines) and budget_lines[line] and budget_lines[line][0].isdigit():
        table += 1
        line += 1
        line += 1  # Skip every other line (original behavior)
    
    if line < len(budget_lines):
        line += 1

    # Count footer lines
    if line + 5 < len(budget_lines):  # budget file contains more than one table
        while line < len(budget_lines) and (not budget_lines[line] or not budget_lines[line][0].isdigit()):
            footer += 1
            line += 1
    
    footer = footer + 1 - header  # to get footer length
    if footer < 0:
        footer = 0
        
    # Calculate number of tables (ensure at least 1)
    total_lines_per_table = header + table + footer
    if total_lines_per_table > 0:
        tables = max(1, round(len(budget_lines) / total_lines_per_table))
    else:
        tables = 1

    return tables, header, footer
