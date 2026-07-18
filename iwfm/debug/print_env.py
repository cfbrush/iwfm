# print_env.py
# Print some envoronment variables to the console for debugging
# Copyright (C) 2018-2021 University of California
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


'''Print some envoronment variables to the console for debugging.'''

def print_env():  # print some paths
    '''Print some environment variables to the console, for debugging.

    Parameters
    ----------
    nothing

    Return
    ------
    nothing
    '''
    import os
    import platform

    print('Environment:')
    print(f'  System:            {platform.system()} version {platform.release()}')
    print(f'  pwd:               {os.getcwd()}')
    print(f'  PATH:              {os.environ["PATH"]}')
    # print(f'  LD_LIBRARY_PATH:   {os.environ['LD_LIBRARY_PATH']}')
    # print(f'  DYLD_LIBRARY_PATH: {os.environ['DYLD_LIBRARY_PATH']}')
    print(f'  PYTHONPATH:        {os.environ["PATH"]}')
    print(' ')
    return

