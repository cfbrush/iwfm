# exe_time.py
# Print difference between two datetime values
# First call stores start time, subsequent calls print elapsed time
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

'''Print difference between two datetime values.

First call stores start time, subsequent calls print elapsed time.
'''

import datetime


class ExeTimeTracker:
    """Class to track execution time with a start datetime."""
    def __init__(self):
        self.start = datetime.datetime.now()

    def get_start(self):
        return self.start


# Module-level singleton instance
_exe_time_instance = None


def exe_time():
    '''Track the time since the first call and print the elapsed time on subsequent calls.

    Parameters
    ----------
    nothing

    Return
    ------
    nothing
    '''
    global _exe_time_instance

    if _exe_time_instance is None:
        # First call - create the tracker instance
        _exe_time_instance = ExeTimeTracker()
        return
    else:
        # Subsequent calls - calculate and print elapsed time
        end = datetime.datetime.now()

        diff = str(end - _exe_time_instance.get_start()).split(':')
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
        print(f'  Elapsed time: {hours}{mins}{secs}\n')

