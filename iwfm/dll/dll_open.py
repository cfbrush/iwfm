# dll_open.py
# IWFM DLL: instantiate an IWFM_Model object from Preprocessor and Simulation filenames
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


def dll_open(iwfm_dll, pre_file, sim_file, routed_streams=1, for_inquiry=1):
    ''' IWFM DLL: instantiate an IWFM_Model object from Preprocessor and Simulation filenames

    Parameters
    ----------
    iwfm_dll :  IWFM DLL object
        instantiated IWFM DLL object

    pre_file : str
        file path and name of the model preprocessor input file

    sim_file : str
        file path and name of the model simulation input file

    routed_streams : int, default=1
        1: model has routed streams
        0: stream routing in a linked model

    for_inquiry : int, default=1
        1: accessing the model to return input and output data
        0: running simulations

    Returns
    -------
    iwfm_model : object
        instantiated IWFM model object

    status : int
        0 if everything worked
 
    '''

    #import ctypes
    from ctypes import byref, c_int, create_string_buffer, sizeof
    import iwfm

    iwfm.file_test(pre_file)
    iwfm.file_test(sim_file)

    pfile = create_string_buffer(pre_file.encode('utf-8'))
    sfile = create_string_buffer(sim_file.encode('utf-8'))
            
    status = c_int(-1)

    iwfm_dll.IW_Model_New(byref(c_int(sizeof(pfile))), pfile, 
            byref(c_int(sizeof(sfile))), sfile, byref(c_int(routed_streams)), 
            byref(c_int(for_inquiry)), byref(status))

    return status.value
    


if __name__ == '__main__':
    ' Run dll_open() from command line '
    import sys
    import iwfm.debug as idb
    import iwfm
    import iwfm.dll as idll
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()
    #import iwfm.dll as dll

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

    status = dll_open(iwfm_dll, pre_file, sim_file)

    if status == 0:
        print('  dll_open() worked!')
    else:
        print('  dll_open() didn\'t work!')

    idb.exe_time()  # print elapsed time
