# file_missing.py
# Raise FileNotFoundError for a missing file
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


def file_missing(filename, context=None):
    '''Raise FileNotFoundError for a file that does not exist.

    Parameters
    ----------
    filename : str
        file name

    context : str, optional
        additional context message (e.g., "referenced in groundwater file")

    Returns
    -------
    nothing — this function never returns normally.

    Raises
    ------
    FileNotFoundError
        Always, with the file name, optional context, and current
        working directory in the message.
    '''
    import os

    msg = f'File path {filename} does not exist.'
    if context:
        msg += f' {context}.'
    msg += f' Current working directory: {os.getcwd()}'
    raise FileNotFoundError(msg)
