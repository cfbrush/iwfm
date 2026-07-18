# file_delete
# Delete file
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


'''Delete file.'''

from iwfm.debug.logger_setup import logger

def file_delete(filename):
    '''Delete a file.

    Parameters
    ----------
    filename : str
        file name

    Returns
    -------
    nothing
    '''
    import os

    if os.path.isfile(filename):  # if file exists
        try:
            os.remove(filename)  # delete it
        except (PermissionError, OSError) as e:
            logger.error(f'file_delete: failed to delete {filename}: {e}')
            raise
        logger.debug(f'file_delete: deleted {filename}')
    else:
        logger.debug(f'file_delete: file {filename} does not exist, no action taken')

