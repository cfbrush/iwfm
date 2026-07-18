# dll_init.py
# Initialize IWFM DLL
# Copyright (C) 2021-2026 University of California
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

def dll_init(dll_path, preprocessor_file_name, simulation_file_name, has_routed_streams=1, is_for_inquiry=1):
    '''Initialize IWFM DLL.

    Parameters
    ----------
    dll_path : str
        file path and name of the IWFM DLL to access IWFM procedures

    preprocessor_file_name : str
        file path and name of the model preprocessor input file

    simulation_file_name : str
        file path and name of the model simulation input file

    has_routed_streams : int, default=1
        option=1 for model having routed streams
        option=0 for model not having routed streams

    is_for_inquiry : int, default=1
        option=1 for model being accessed to return input and output data
        option=0 for model simulations

        notes:
        is_for_inquiry=1: when an instance of the IWFM_Model class is 
        created for the first time, the entire model object will be 
        available for returning data. A binary file will be generated 
        for quicker loading, if this binary file exists when subsequent 
        instances of the IWFM_Model object are created, not all functions
        will be available.

    Returns
    -------
    -- ? --
    '''
    import ctypes

    if isinstance(dll_path, str):
        dll_path = dll_path
    else:
        raise TypeError(f'DLL path must be a string.\nProvided {dll_path} is a {type(dll_path)}')

    if isinstance(preprocessor_file_name, str):
        preprocessor_file_name = ctypes.create_string_buffer(preprocessor_file_name.encode('utf-8'))
        length_preprocessor_file_name = ctypes.c_int(ctypes.sizeof(preprocessor_file_name))

    if isinstance(simulation_file_name, str):
        simulation_file_name = ctypes.create_string_buffer(simulation_file_name.encode('utf-8'))
        length_simulation_file_name = ctypes.c_int(ctypes.sizeof(simulation_file_name))

    if isinstance(has_routed_streams, int):
        has_routed_streams = ctypes.c_int(has_routed_streams)

    if isinstance(is_for_inquiry, int):
        is_for_inquiry = ctypes.c_int(is_for_inquiry)
            
    status = ctypes.c_int(-1)
            
    dll = ctypes.windll.LoadLibrary(dll_path)
        
    # check to see if IWFM procedure is available in user version of IWFM DLL
    seek_proc = 'IW_Model_New'
    if not hasattr(dll, seek_proc):
        raise AttributeError(f'IWFM DLL does not have "{seek_proc}" procedure. Check for an updated version')

    return dll.IW_Model_New(ctypes.byref(length_preprocessor_file_name), 
                preprocessor_file_name, 
                ctypes.byref(length_simulation_file_name), 
                simulation_file_name, 
                ctypes.byref(has_routed_streams), 
                ctypes.byref(is_for_inquiry), 
                ctypes.byref(status))
    


if __name__ == '__main__':
    ' Run dll_init() from command line '
    import sys
    import iwfm.debug as idb
    import iwfm
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()
    #import iwfm.dll as dll

    if len(sys.argv) > 1:  # arguments are listed on the command line
        dll_path = sys.argv[1]
        preprocessor_file_name = sys.argv[2]
        simulation_file_name = sys.argv[3]

    else:  # ask for file names from terminal
        dll_path               = input('Path to IWFM DLL: ')
        preprocessor_file_name = input('IWFM Preprocessor file name: ')
        simulation_file_name   = input('IWFM Simulation file name: ')

    iwfm.file_test(preprocessor_file_name)
    iwfm.file_test(simulation_file_name)

    idb.exe_time()  # initialize timer
    dll_init(dll_path, preprocessor_file_name, simulation_file_name)

    idb.exe_time()  # print elapsed time
