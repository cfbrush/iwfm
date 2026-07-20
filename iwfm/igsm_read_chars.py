# igsm_read_chars.py
# Read an IGSM pre-processor element characteristics file
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


'''Read an IGSM Element Characteristics file and return a list of characteristics for each element.'''

def igsm_read_chars(char_file, elem_nodes):
    '''Read an IGSM Element Characteristics file and return a list of characteristics for each element.

    Parameters
    ----------
    char_file : str
        IGSM Element Characteristics file name

    elem_nodes : list
        elements and associated nodes

    Returns
    -------
    elem_char : list
        element characteristics
    '''
    import iwfm
    from iwfm.file_utils import read_next_line_value

    iwfm.file_test(char_file)
    with open(char_file, encoding='utf-8') as f:
        char_lines = f.read().splitlines()  # open and read input file

    # skip comments to find first data line
    _, char_index = read_next_line_value(char_lines, -1, column=0)
    elem_char = []
    for i in range(0, len(elem_nodes)):
        l = char_lines[char_index + i].split()
        l.pop(0)                       # element ID
        chars = []
        chars.append(int(l.pop(0)))    # rain station
        chars.append(float(l.pop(0)))  # rain factor
        chars.append(int(l.pop(0)))    # drainage destination
        chars.append(int(l.pop(0)))    # subregion
        l.pop(0)                       # don't use
        chars.append(float(l.pop(0)))  # soil type
        elem_char.append(chars)
    return elem_char
