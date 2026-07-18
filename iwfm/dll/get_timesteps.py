# get_timesteps.py
# IWFM DLL: Get number of time steps in current model
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


def get_timesteps(iwfm_dll):
    '''IWFM DLL: Get number of time steps in current model.

    Parameters
    ----------
    iwfm_dll :  IWFM Model object
        instantiated IWFM model object

    Returns
    -------
    n_timesteps : int
        number of time steps

    status : int
        0 if everything worked
    '''

    from ctypes import byref, c_int

    n_timesteps, status = c_int(-1), c_int(-1)

    import iwfm.dll as idll
    idll.seek_proc(iwfm_dll,'IW_Model_GetNTimeSteps')

    iwfm_dll.IW_Model_GetNTimeSteps(byref(n_timesteps), byref(status))

    return n_timesteps.value, status.value
    


if __name__ == '__main__':
    ' Run get_timesteps() from command line '
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

    n_timesteps, status = get_timesteps(iwfm_dll)
    
    print(f'  No of time steps: {n_timesteps}')

    idb.exe_time()  # print elapsed time
