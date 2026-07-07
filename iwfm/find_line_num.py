# find_line_num.py
# Find the line number in a text file where the desired string is located
# Copyright (C) 2020-2023 University of California
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


def find_line_num(file_path, desired):
    """find_line_num() - Find the line number in a text file where the desired string is located.

    Parameters
    ----------
    file_path : str
        The file path of the text file to be searched.

    desired : str
        The string to be searched for within the file.

    Returns
    -------
    line_number : int or None
        The line number where the first occurrence of the `desired` string was found. If the
        string is not found in the file, the function returns `None`.

    """
    line_number = None

    with open(file_path, 'r', encoding='utf-8') as file:
        for num, line in enumerate(file,1):
            #  If the string is in the line, break
            if desired in line:
                line_number = num
                break

    return line_number