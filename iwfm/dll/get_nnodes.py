# get_nnodes.py
# IWFM DLL: Get the number of FE nodes in the current model
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


def get_nnodes(iwfm_dll):
    '''IWFM DLL: Get the number of FE nodes in the current model.

    Parameters
    ----------
    iwfm_dll :  IWFM Model object
        instantiated IWFM model object

    Returns
    -------
    nnodes : int
        number of nodes in model FE grid

    status : int
        0 if everything worked
    '''

    from ctypes import byref, c_int

    nnodes, status = c_int(-1),  c_int(-1)

    iwfm_dll.IW_Model_GetNNodes( byref(nnodes),  byref(status) )

    return nnodes.value, status
    


if __name__ == '__main__':
    ' Run get_nnodes() from command line '
    import sys
    import iwfm.debug as idb
    import iwfm
    import iwfm.dll as idll
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    if len(sys.argv) > 1:  # arguments are listed on the command line
        dll_path, pre_file, sim_file = sys.argv[1], sys.argv[2], sys.argv[3]

    else:  # ask for file names from terminal
        dll_path = input('Path to IWFM DLL: ')
        pre_file = input('IWFM Preprocessor file name: ')
        sim_file = input('IWFM Simulation file name: ')

    iwfm.file_test(pre_file)
    iwfm.file_test(sim_file)

    idb.exe_time()  # initialize timer

    iwfm_dll = idll.dll_init(dll_path)  # instatiate the IWFM DLL
    status = idll.dll_open(iwfm_dll, pre_file, sim_file) # instantiate the model

    nnodes = get_nnodes(iwfm_dll)[0]
    
    print(f'  No of nodes: {nnodes:,}')

    idb.exe_time()  # print elapsed time
