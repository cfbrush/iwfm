# get_node_xy.py
# IWFM DLL: Get X- and Y-coordinates of FE grid
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


'''IWFM DLL: Get X- and Y-coordinates of FE grid.'''

def get_node_xy(iwfm_dll):
    '''IWFM DLL: Get X- and Y-coordinates of FE grid.

    Parameters
    ----------
    iwfm_dll :  IWFM Model object
        instantiated IWFM model object

    Returns
    -------
    x : list of floats
        X-coordinates of FE grid nodes

    y : list of floats
        Y-coordinates of FE grid nodes

    status : int
        0 if everything worked
    '''

    from ctypes import byref, c_int, c_double
    import iwfm.dll as idll

    nnodes = idll.get_nnodes(iwfm_dll)[0]

    x = (c_double * nnodes)(*range(nnodes))
    y = x
   
    status = c_int(-1)

    iwfm_dll.IW_Model_GetNodeXY(byref(c_int(nnodes)), byref(x), byref(y), byref(status))

    return x, y, status
    


if __name__ == '__main__':
    ' Run get_node_xy() from command line '
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

    x, y, status = get_node_xy(iwfm_dll)
    
    print(f'  No of (x,y) coordinate pairs: {len(x):,}')
    print(f'  (x[1],y[1]) : ({x.value:,},{y.value:,})')

    idb.exe_time()  # print elapsed time
