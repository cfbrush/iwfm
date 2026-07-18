# get_timespecs.py
# IWFM DLL: Get all time information from current model
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


'''IWFM DLL: Get all time information from current model.'''

def get_timespecs(iwfm_dll):
    '''IWFM DLL: Get all time information from current model.

    Parameters
    ----------
    iwfm_dll :  IWFM Model object
        instantiated IWFM model object

    Returns
    -------
    timestamps : list of strings
        timestamps for all model time steps

    timestep : str
        simulation timestep

    status : int
        0 if everything worked
    '''

    #from ctypes import c_int, create_string_buffer
    from ctypes import byref, c_int, create_string_buffer
    import iwfm.dll as idll

    n_timesteps = idll.get_timesteps(iwfm_dll)[0]

    buff = 'MM/DD/YYYY_hh:mm'

    dates_times = create_string_buffer((buff * n_timesteps).encode('utf-8'))
    
    time_step = create_string_buffer(buff.encode('utf-8'))

    iLocArray = (c_int * n_timesteps)(*range(n_timesteps))
   
    status = c_int(-1)

    iwfm_dll.IW_Model_GetTimeSpecs(byref(dates_times), 
            byref(c_int( len(buff) * n_timesteps )), byref(time_step), 
            byref(c_int(len(buff))), byref(c_int(n_timesteps)), 
            byref(iLocArray), byref(status))

    # convert return values from binary to ascii
    dates_times = [dates_times.value.decode("ascii")[i:i+len(buff)] for i in range(0, len(dates_times.value), len(buff))]

    time_step = time_step.value.decode("ascii")

    return dates_times, time_step, status
    


if __name__ == '__main__':
    ' Run get_timespecs() from command line '
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

    dates_times, time_step, status = get_timespecs(iwfm_dll)
    
    print(f'  No of time steps: {len(dates_times)}')
    print(f'  date range: {dates_times[0]} - {dates_times[len(dates_times)-1]}')
    print(f'  time_step: {time_step}')

    idb.exe_time()  # print elapsed time
