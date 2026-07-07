# file_type_error.py
# Message re. wrong file type
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


def file_type_error(filename, filetype):
    ''' file_type_error() - Raise ValueError for an input file of the
        wrong type

    Parameters
    ----------
    filename : str
        file name for message

    filetype : str
        file type for message

    Returns
    -------
    nothing — this function never returns normally.

    Raises
    ------
    ValueError
        Always, naming the file and the required file type.

    '''
    raise ValueError(f'{filename} must be a {filetype} file')
