# dll_init.py
# Initialize IWFM DLL
# Copyright (C) 2021 University of California
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


'''Initialize IWFM DLL.'''

def dll_init(dll_path):
    '''Initialize IWFM DLL.

    Parameters
    ----------
    dll_path : str
        file path and name of the IWFM DLL to access IWFM procedures


    Returns
    -------
    iwfm_dll : object
        iwfm dll object
    '''
    import ctypes
    import iwfm

    iwfm.file_test(dll_path)

    return ctypes.windll.LoadLibrary(dll_path)    


if __name__ == '__main__':
    ' Run dll_init() from command line '
    import sys
    import iwfm.debug as idb
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    if len(sys.argv) > 1:  # arguments are listed on the command line
        dll_path = sys.argv[1]

    else:  # ask for file names from terminal
        dll_path = input('Path to IWFM DLL: ')

    idb.exe_time()  # initialize timer

    iwfm_dll = dll_init(dll_path)
    print(f'  IWFM DLL: {iwfm_dll}')

    idb.exe_time()  # print elapsed time
