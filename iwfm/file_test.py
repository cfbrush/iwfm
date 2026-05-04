# file_test.py
# Test for file
# Copyright (C) 2020-2023 University of California
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


def file_test(filename):
    ''' file_test() - Check that the file exists and exit if it does not

    Parameters
    ----------
    filename : str
        file name

    Returns
    -------
    nothing

    Raises
    ------
    SystemExit
        Raised (via :func:`iwfm.file_missing`) if ``filename`` does not
        resolve to an existing file. Callers that want a recoverable
        signal should pre-check with ``os.path.isfile`` or
        ``Path(...).is_file()`` instead.

    '''
    import os
    import iwfm

    if not os.path.isfile(filename):  # test that input file exists
        iwfm.file_missing(filename)
