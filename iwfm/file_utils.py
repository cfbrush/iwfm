#!/usr/bin/env python
# file_utils.py
# Utility functions for file reading operations
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

'''IWFM File Format Conventions ----------------------------- IWFM input files follow a Fortran-style convention where:

- Comment lines start with 'C', 'c', '*', or '#' in the first column (column 1)
- Data lines MUST start with whitespace (space, tab) to avoid being treated as comments

This convention ensures that data values never accidentally get interpreted as comment
markers. For example, a filename 'crop_data.dat' would appear as ' crop_data.dat'
(with leading space) in IWFM input files.

The skip_ahead() function implements this convention and is used internally by the
utility functions in this module.
'''

from __future__ import annotations

from typing import Any, Callable, Dict, List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np


def skip_to_next_line(lines: List[str], line_index: int, skip_lines: int = 0) -> int:
    """
    Advance to the next non-comment line without parsing it.

    This is the positioning-only counterpart to :func:`read_next_line_value`.
    Use it when you just need to move the cursor between sections of an IWFM
    file and don't need a value at the new position. Unlike
    :func:`read_next_line_value`, it doesn't raise IndexError when the
    resulting line is empty or past EOF — it returns the raw skip_ahead
    result (-1 at EOF).

    Parameters
    ----------
    lines : list
        List of file lines.
    line_index : int
        Current line index (0-based). The function starts looking from
        ``line_index + 1`` (matching ``read_next_line_value`` semantics, so
        a literal ``iwfm.skip_ahead(start, lines, N)`` translates to
        ``skip_to_next_line(lines, start - 1, skip_lines=N)``).
    skip_lines : int, default=0
        Number of non-comment lines to skip.

    Returns
    -------
    new_line_index : int
        Updated line index, or -1 if EOF was reached.
    """
    import iwfm

    return iwfm.skip_ahead(line_index + 1, lines, skip_lines)


def read_next_line_value(lines: List[str], line_index: int, column: int = 0,
                         skip_lines: int = 0, strip: bool = True) -> Tuple[str, int]:
    """
    Skip ahead and read a value from the next line.

    This utility function consolidates the common pattern of skipping comment
    lines and extracting a value from a specific column in IWFM input files.

    Parameters
    ----------
    lines : list
        List of file lines (typically from file.readlines() or str.splitlines())
    line_index : int
        Current line index (0-based)
    column : int, default=0
        Column index to extract after splitting the line by whitespace
    skip_lines : int, default=0
        Number of comment/blank lines to skip using iwfm.skip_ahead()
    strip : bool, default=True
        Whether to strip whitespace from the extracted value

    Returns
    -------
    value : str
        The extracted value from the specified column
    new_line_index : int
        The updated line index after reading

    Examples
    --------
    >>> lines = ['# comment line', 'data.txt  ! inline comment', 'next.dat']
    >>> value, idx = read_next_line_value(lines, 0, skip_lines=0)
    >>> value
    'data.txt'
    >>> idx
    1

    >>> # Read from specific column
    >>> lines = ['10 20 30', '40 50 60']
    >>> value, idx = read_next_line_value(lines, -1, column=1)
    >>> value
    '20'

    Notes
    -----
    This function uses iwfm.skip_ahead() internally to handle comment lines
    marked with 'C', '!', '#', or '*' at the beginning.
    """
    import iwfm

    # Skip ahead to next non-comment line
    line_index = iwfm.skip_ahead(line_index + 1, lines, skip_lines)

    # Split line and extract value
    parts = lines[line_index].split()

    if column >= len(parts):
        raise IndexError(
            f"Column {column} not found in line {line_index}. "
            f"Line has {len(parts)} columns: {lines[line_index]}"
        )

    value = parts[column]

    if strip:
        value = value.strip()

    return value, line_index


def read_multiple_line_values(lines: List[str], start_index: int, count: int,
                              column: int = 0, skip_lines: int = 0) -> Tuple[List[str], int]:
    """
    Read multiple consecutive line values.

    This function reads a specified number of values from consecutive lines,
    useful when an IWFM input file contains a sequence of filenames or
    parameters listed one per line.

    Parameters
    ----------
    lines : list
        List of file lines
    start_index : int
        Starting line index (0-based)
    count : int
        Number of values to read
    column : int, default=0
        Column index to extract from each line (after splitting)
    skip_lines : int, default=0
        Number of comment/blank lines to skip between each read

    Returns
    -------
    values : list
        List of extracted values (as strings)
    final_line_index : int
        The line index after reading all values

    Examples
    --------
    >>> lines = ['file1.txt', 'file2.txt', 'file3.txt', 'file4.txt']
    >>> values, idx = read_multiple_line_values(lines, -1, 3)
    >>> values
    ['file1.txt', 'file2.txt', 'file3.txt']
    >>> idx
    2

    >>> # Read from specific column
    >>> lines = ['1 data1.dat', '2 data2.dat', '3 data3.dat']
    >>> values, idx = read_multiple_line_values(lines, -1, 3, column=1)
    >>> values
    ['data1.dat', 'data2.dat', 'data3.dat']

    Notes
    -----
    This function calls read_next_line_value() internally for each value,
    ensuring consistent handling of comments and whitespace.
    """
    values = []
    line_index = start_index

    for i in range(count):
        try:
            value, line_index = read_next_line_value(
                lines, line_index, column, skip_lines
            )
            values.append(value)
        except IndexError as e:
            raise IndexError(
                f"Failed to read value {i+1} of {count}: {str(e)}"
            )

    return values, line_index


def read_line_values_to_dict(lines: List[str], start_index: int, keys: List[str],
                             column: int = 0, skip_lines: int = 0) -> Tuple[Dict[str, str], int]:
    """
    Read multiple line values directly into a dictionary.

    This is a convenience function for the common pattern of reading sequential
    values and storing them in a dictionary with specific keys. Particularly
    useful for reading file configuration sections in IWFM input files.

    Parameters
    ----------
    lines : list
        List of file lines
    start_index : int
        Starting line index (0-based)
    keys : list of str
        List of dictionary keys to use for the extracted values
    column : int, default=0
        Column index to extract from each line
    skip_lines : int, default=0
        Number of comment/blank lines to skip between reads

    Returns
    -------
    result_dict : dict
        Dictionary mapping keys to extracted values
    final_line_index : int
        The line index after reading all values

    Examples
    --------
    >>> lines = ['np_crops.dat', 'p_crops.dat', 'urban.dat', 'native.dat']
    >>> keys = ['np_file', 'p_file', 'ur_file', 'nr_file']
    >>> result, idx = read_line_values_to_dict(lines, -1, keys)
    >>> result
    {'np_file': 'np_crops.dat', 'p_file': 'p_crops.dat',
     'ur_file': 'urban.dat', 'nr_file': 'native.dat'}

    Notes
    -----
    This function is equivalent to calling read_multiple_line_values() and
    then zipping the results with keys, but provides a cleaner interface
    for this common pattern.
    """
    values, line_index = read_multiple_line_values(
        lines, start_index, len(keys), column, skip_lines
    )

    result_dict = dict(zip(keys, values))

    return result_dict, line_index


def read_param_table(file_lines: List[str], line_index: int, lines: int,
                     cast: Callable[[str], Any] = float) -> Tuple['np.ndarray', int]:
    '''Read a table of numeric parameters and return a numpy array.

    Shared engine for iwfm_read_param_table_floats and
    iwfm_read_param_table_ints.

    If the first value on the starting line is 0, one set of parameter
    values applies to all elements and only that line is read; otherwise
    one line is read per element.

    Parameters
    ----------
    file_lines : list
        File contents as list of lines

    line_index : int
        The index of the line to start reading from.

    lines : int
        The number of lines to read.

    cast : callable, default=float
        Type conversion applied to each value (float or int).

    Returns
    -------
    params : numpy array
        Table of parameter values

    line_index : int
        Index of the last line read
    '''
    import numpy as np

    params = []
    parts = file_lines[line_index].split()
    if int(parts[0]) == 0:                                              # one set of parameter values for all elements
        params = [cast(e) for e in parts[1:]]                           # skip the first value which is the element number
        _, line_index = read_next_line_value(file_lines, line_index)    # skip to next value line
    else:
        for i in range(lines):
            parts = file_lines[line_index].split()
            params.append([cast(e) for e in parts[1:]])                 # skip the first value which is the element number
            line_index += 1                                             # skip to next line
    line_index -= 1

    return np.array(params), line_index


if __name__ == '__main__':
    # Simple tests
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()
    print("Testing file_utils.py functions...")

    # Test read_next_line_value
    test_lines = ['# Comment', 'file1.txt  ! inline comment', 'file2.txt']
    value, idx = read_next_line_value(test_lines, 0)
    assert value == 'file1.txt', f"Expected 'file1.txt', got '{value}'"
    assert idx == 1, f"Expected index 1, got {idx}"
    print("✓ read_next_line_value() works correctly")

    # Test read_multiple_line_values
    test_lines = ['file1.txt', 'file2.txt', 'file3.txt']
    values, idx = read_multiple_line_values(test_lines, -1, 3)
    assert values == ['file1.txt', 'file2.txt', 'file3.txt']
    assert idx == 2
    print("✓ read_multiple_line_values() works correctly")

    # Test read_line_values_to_dict
    keys = ['file1', 'file2', 'file3']
    result, idx = read_line_values_to_dict(test_lines, -1, keys)
    assert result == {'file1': 'file1.txt', 'file2': 'file2.txt', 'file3': 'file3.txt'}
    print("✓ read_line_values_to_dict() works correctly")

    print("\nAll tests passed!")
