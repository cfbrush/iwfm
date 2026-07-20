# skip_ahead.py
# Skip a specified number of list elements plus all that begin with a comment character
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


'''Increment line_index by skipping (a) every line that begins with 'C', 'c' '*' or '#' and (b) 'skip' additional lines.'''

def skip_ahead(line_index, all_lines, skip=0):
    '''Increment line_index by skipping (a) every line that begins with 'C', 'c' '*' or '#' and (b) 'skip' additional lines.

    Stop if last line (all_lines) is reached

    Parameters
    ----------
    line_index : int
        current line number

    all_lines : list
        each item is one line from a file

    skip : int, default=0
        number of non-comment lines to skip

    Returns
    -------
    line_index : int
        new current line or -1 if end reached

    Raises
    ------
    ValueError
        If line_index is negative or skip is negative
    TypeError
        If all_lines is not a list or line_index/skip are not integers
    '''
    # Input validation
    if not isinstance(all_lines, list):
        raise TypeError(
            f"all_lines must be a list, got {type(all_lines).__name__}"
        )
    if not isinstance(line_index, int):
        raise TypeError(
            f"line_index must be an integer, got {type(line_index).__name__}"
        )
    if not isinstance(skip, int):
        raise TypeError(
            f"skip must be an integer, got {type(skip).__name__}"
        )
    if line_index < 0:
        raise ValueError(
            f"line_index must be non-negative, got {line_index}"
        )
    if skip < 0:
        raise ValueError(
            f"skip must be non-negative, got {skip}"
        )

    skip_lines = skip
    comments = 'Cc*#'

    # Skip non-comment lines according to skip parameter
    while skip_lines > 0:
        # Check bounds
        if line_index >= len(all_lines):
            return -1

        # Check if current line is a non-comment line
        # Empty strings are treated as non-comment lines but won't cause IndexError
        # because Python uses short-circuit evaluation
        if all_lines[line_index] and all_lines[line_index][0] not in comments:
            skip_lines -= 1
        line_index += 1

    # Skip all remaining comment lines
    # Using explicit bounds check and empty string check to prevent IndexError
    while line_index < len(all_lines):
        # Check if line is not empty and starts with comment character
        # Empty strings will be treated as non-comment and we'll stop here
        current_line = all_lines[line_index]
        if not current_line or current_line[0] not in comments:
            break
        line_index += 1

    # Check if we've reached the end
    if line_index >= len(all_lines):
        return -1

    return line_index
