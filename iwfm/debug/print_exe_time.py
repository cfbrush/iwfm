# print_exe_time.py
# Print difference between two datetime values
# Copyright (C) 2020-2026 University of California
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


'''Function print_exe_time(start, end) returns the time between two datetime values as a sting hh:mm:ss,.'''

def print_exe_time(start, end, verbose=1):
    '''Function print_exe_time(start, end) returns the time between two datetime values as a sting hh:mm:ss,.

    Parameters
    ----------
    start : datetime
        starting time

    end : datetime
        ending time

    verbose : bool, default=False
        True = print exe_time

    Return
    ------
    exe_time : str
        execution time as a sting, format dependes on exe_time value
          if exe_time >= 1 hour:
             'hh:mm:ss'
          elif exe_time >1 minute:
             'mm min ss sec'
          else:
             'ss.s seconds'
    '''
    diff = str(end - start).split(':')
    secs = str(round(float(diff[2]), 1))
    if int(diff[0]) > 0:
        hours = str(int(diff[0])).zfill(2) + ':'
        mins = str(int(diff[1])).zfill(2) + ':'
    elif int(diff[1]) > 0:
        hours = ''
        mins = f'{int(diff[1])} min '
        secs += ' sec'
    else:
        hours, mins = '', ''
        secs += ' seconds'
    exe_time = f'{hours}{mins}{secs}'
    if verbose:
        print(f'  Execution time: {exe_time}\n')
    return exe_time
