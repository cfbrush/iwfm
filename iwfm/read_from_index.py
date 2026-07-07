# read_from_index.py 
# Read lines from a text file starting from a specified index
# Copyright (C) 2018-2023 University of California
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

def read_from_index(file_name, start_index):
    """read_from_index() - Read lines from a text file starting from a specified index.

    Parameters
    ----------
    file_path : str
        The file name for the text file to be read.

    start_index : int
        The line number from which the reading should start.

    Returns
    -------
    lines : list
        A list containing the relevant lines read from the file. Each line is represented as a
        list of individual elements obtained by splitting the line based on whitespace.
    """
    #  List to hold the read lines
    lines = []

    with open(file_name, 'r', encoding='utf-8') as file:
        #  Skip lines until the start_index
        for _ in range(start_index - 1):
            next(file)

        # Read lines until a line is blank or starts with "C"
        for line in file:
            if line.strip().startswith("C") or len(line.split()) == 0:
                break

            #  Strip the line of spaces and split into a list 
            formatted_line = line.strip().split()

            #  If the line has a node number, remove it
            if len(formatted_line) == 6:
                formatted_line = formatted_line[1:]
            
            #  Add line to the list
            lines.append(formatted_line)

    return lines

