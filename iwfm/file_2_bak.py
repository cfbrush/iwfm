# file_2_bak.py
# Create backup of file
# Copyright (C) 2020-2021 University of California
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


def file_2_bak(filename, force=1):
    '''Rename a file to contain .bak extension.

    Parameters
    ----------
    filename : str
        Name of existing file

    force : int, default=1
        Force overwrite? 1=yes, 0=no

    Returns
    -------
    nothing
    '''
    import os
    import iwfm

    if os.path.isfile(filename):  # if the file exists...
        newfile = os.path.splitext(filename)[0] + '.bak'
        iwfm.file_rename(filename, newfile, force)
    return

if __name__ == '__main__':
    ''' Run file_2_bak() from command line '''
    import sys
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    if len(sys.argv) > 1:  # arguments are listed on the command line
        input_file = sys.argv[1]
    else:  # ask for file names from terminal
        input_file = input('Input file name: ')

    file_2_bak(input_file)
